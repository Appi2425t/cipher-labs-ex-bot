import discord
from discord.ext import commands
from discord import ui
import json
from utils import get_category_info, has_staff_role, has_admin_or_mod, build_ticket_embed, generate_html_transcript
import io


class TicketControlView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.secondary, custom_id="ticket:close")
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        config = await self.bot.db.get_config(interaction.guild_id)
        if not has_admin_or_mod(interaction.user, config):
            await interaction.response.send_message("❌ Only Admin/Mod can close tickets.", ephemeral=True)
            return
        await interaction.response.defer()
        ticket = await self.bot.db.get_ticket_by_channel(interaction.channel_id)
        if not ticket:
            await interaction.followup.send("❌ This is not a ticket channel.", ephemeral=True)
            return
        await close_ticket_logic(self.bot, interaction.channel, interaction.user, ticket, config)

    @ui.button(label="Claim", emoji="👤", style=discord.ButtonStyle.primary, custom_id="ticket:claim")
    async def claim_button(self, interaction: discord.Interaction, button: ui.Button):
        config = await self.bot.db.get_config(interaction.guild_id)
        if not has_staff_role(interaction.user, config):
            await interaction.response.send_message("❌ Only staff can claim tickets.", ephemeral=True)
            return

        ticket = await self.bot.db.get_ticket_by_channel(interaction.channel_id)
        if not ticket:
            await interaction.response.send_message("❌ This is not a ticket channel.", ephemeral=True)
            return

        if ticket["claimed_by"]:
            await interaction.response.send_message("❌ This ticket is already claimed.", ephemeral=True)
            return

        # Check limit for exchange tickets
        if ticket["category"] in ("i2c", "c2i") and ticket.get("deal_amount_usd"):
            limit_data = await self.bot.db.get_limit(interaction.guild_id, interaction.user.id)
            deal_amount = ticket["deal_amount_usd"] or 0
            if limit_data["limit_usd"] > 0:
                available = limit_data["limit_usd"] - limit_data["used_usd"]
                if deal_amount > available:
                    await interaction.response.send_message(
                        f"❌ **Limit Exceeded**\n"
                        f"Your Limit: `${limit_data['limit_usd']:.2f}`\n"
                        f"In Use: `${limit_data['used_usd']:.2f}`\n"
                        f"Available: `${available:.2f}`\n"
                        f"Deal Amount: `${deal_amount:.2f}`",
                        ephemeral=True
                    )
                    return
            # Reserve the amount
            await self.bot.db.add_used(interaction.guild_id, interaction.user.id, deal_amount)

        await self.bot.db.update_ticket(ticket["id"], claimed_by=interaction.user.id)
        ticket["claimed_by"] = interaction.user.id

        # Edit the pinned embed
        user = interaction.guild.get_member(ticket["user_id"])
        embed = build_ticket_embed(
            ticket["category"], user or interaction.user,
            ticket["ticket_number"], claimed_by=interaction.user
        )
        # Find the pinned message
        pins = await interaction.channel.pins()
        for pin in pins:
            if pin.author == self.bot.user and pin.embeds:
                await pin.edit(embed=embed)
                break

        await interaction.response.send_message(f"✅ Ticket claimed by {interaction.user.mention}", ephemeral=False)

        # Log
        log_channel_id = config.get("log_channel")
        if log_channel_id:
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                log_embed = discord.Embed(
                    title="👤 Ticket Claimed",
                    description=f"Ticket #{ticket['ticket_number']:04d} claimed by {interaction.user.mention}",
                    color=discord.Color.green()
                )
                await log_channel.send(embed=log_embed)


async def close_ticket_logic(bot, channel, closer, ticket, config):
    await bot.db.close_ticket(ticket["id"])

    # Generate transcript
    messages = await bot.db.get_ticket_messages(ticket["id"])
    guild = channel.guild
    html = generate_html_transcript(ticket, messages, guild)
    html_file = discord.File(io.BytesIO(html.encode()), filename=f"transcript-{ticket['ticket_number']:04d}.html")

    # Post to transcript channel
    transcript_channel_id = config.get("transcript_channel")
    if transcript_channel_id:
        transcript_channel = guild.get_channel(transcript_channel_id)
        if transcript_channel:
            embed = discord.Embed(
                title=f"📝 Transcript — Ticket #{ticket['ticket_number']:04d}",
                description=f"Category: {ticket['category']}\nUser: <@{ticket['user_id']}>\nClosed by: {closer.mention}",
                color=discord.Color.orange()
            )
            await transcript_channel.send(embed=embed, file=html_file)

    # Log
    log_channel_id = config.get("log_channel")
    if log_channel_id:
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title="🔒 Ticket Closed",
                description=f"Ticket #{ticket['ticket_number']:04d} closed by {closer.mention}\nChannel: {channel.name}",
                color=discord.Color.red()
            )
            await log_channel.send(embed=log_embed)

    # Delete channel
    await channel.delete(reason=f"Ticket closed by {closer}")


class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketControlView(self.bot))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        ticket = await self.bot.db.get_ticket_by_channel(message.channel.id)
        if ticket and ticket["status"] == "open":
            await self.bot.db.log_message(
                ticket["id"],
                message.author.id,
                str(message.author),
                message.content or "[attachment/embed]"
            )

    @commands.command(name="close")
    async def close_cmd(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_or_mod(ctx.author, config):
            await ctx.send("❌ Only Admin/Mod can close tickets.")
            return
        ticket = await self.bot.db.get_ticket_by_channel(ctx.channel.id)
        if not ticket:
            await ctx.send("❌ This is not a ticket channel.")
            return
        await close_ticket_logic(self.bot, ctx.channel, ctx.author, ticket, config)

    @commands.command(name="add")
    async def add_user(self, ctx: commands.Context, member: discord.Member):
        ticket = await self.bot.db.get_ticket_by_channel(ctx.channel.id)
        if not ticket:
            await ctx.send("❌ This is not a ticket channel.")
            return
        await ctx.channel.set_permissions(member, read_messages=True, send_messages=True, attach_files=True)
        await ctx.send(f"✅ {member.mention} has been added to this ticket.")

    @commands.command(name="remove")
    async def remove_user(self, ctx: commands.Context, member: discord.Member):
        ticket = await self.bot.db.get_ticket_by_channel(ctx.channel.id)
        if not ticket:
            await ctx.send("❌ This is not a ticket channel.")
            return
        await ctx.channel.set_permissions(member, overwrite=None)
        await ctx.send(f"✅ {member.mention} has been removed from this ticket.")


async def open_ticket(bot, interaction: discord.Interaction, category: str, modal_answers: dict = None):
    guild = interaction.guild
    config = await bot.db.get_config(guild.id)

    # Check for existing open ticket
    existing = await bot.db.get_open_ticket(guild.id, interaction.user.id)
    if existing:
        await interaction.followup.send(
            f"❌ You already have an open ticket: <#{existing['channel_id']}>",
            ephemeral=True
        )
        return

    # Increment counter
    ticket_number = await bot.db.increment_ticket_counter(guild.id)

    # Calculate deal amount for exchange tickets
    deal_amount_usd = None
    deal_amount_inr = None
    if modal_answers:
        if category == "i2c":
            try:
                inr_amount = float(modal_answers.get("Amount (INR)", "0").replace(",", ""))
                deal_amount_inr = inr_amount
                rate = config.get("rate_i2c") or 101
                deal_amount_usd = inr_amount / rate
            except (ValueError, TypeError):
                pass
        elif category == "c2i":
            try:
                usd_amount = float(modal_answers.get("Amount (USD $)", "0").replace(",", "").replace("$", ""))
                deal_amount_usd = usd_amount
                if usd_amount >= 100:
                    rate = config.get("rate_c2i_above") or 98.5
                else:
                    rate = config.get("rate_c2i_below") or 97.5
                deal_amount_inr = usd_amount * rate
            except (ValueError, TypeError):
                pass
        elif category == "c2c":
            try:
                usd_amount = float(modal_answers.get("Amount Sending (USD $)", "0").replace(",", "").replace("$", ""))
                deal_amount_usd = usd_amount
            except (ValueError, TypeError):
                pass

    # Create channel
    category_obj = None
    if config.get("ticket_category"):
        category_obj = guild.get_channel(config["ticket_category"])

    username_short = interaction.user.name[:8].lower()
    channel_name = f"{category}-{ticket_number:04d}-{username_short}"

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True, manage_messages=True),
    }

    # Add all staff roles
    for group in ("admin_roles", "mod_roles", "staff_roles", "dealer_roles"):
        role_ids = json.loads(config.get(group, "[]"))
        for rid in role_ids:
            role = guild.get_role(rid)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category_obj,
        overwrites=overwrites,
        reason=f"Ticket opened by {interaction.user}"
    )

    # Create ticket in DB
    ticket_id = await bot.db.create_ticket(
        guild.id, channel.id, interaction.user.id, category,
        ticket_number, deal_amount_usd, deal_amount_inr
    )

    # Send pinned embed
    embed = build_ticket_embed(category, interaction.user, ticket_number, modal_answers=modal_answers,
                               deal_amount_usd=deal_amount_usd, deal_amount_inr=deal_amount_inr, config=config)
    view = TicketControlView(bot)
    msg = await channel.send(embed=embed, view=view)
    await msg.pin()

    # Ping exchanger/dealer roles for exchange tickets (i2c, c2i, c2c)
    if category in ("i2c", "c2i", "c2c"):
        ping_roles = []
        for group in ("staff_roles", "dealer_roles"):
            role_ids = json.loads(config.get(group, "[]"))
            for rid in role_ids:
                role = guild.get_role(rid)
                if role:
                    ping_roles.append(role.mention)
        if ping_roles:
            await channel.send(f"🔔 New exchange ticket! {' '.join(ping_roles)}")

    await interaction.followup.send(f"✅ Ticket created: {channel.mention}", ephemeral=True)

    # Log
    log_channel_id = config.get("log_channel")
    if log_channel_id:
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            info = get_category_info(category)
            log_embed = discord.Embed(
                title=f"🎫 Ticket Opened — #{ticket_number:04d}",
                description=f"**Category:** {info['emoji']} {info['label']}\n**User:** {interaction.user.mention}\n**Channel:** {channel.mention}",
                color=discord.Color.green()
            )
            await log_channel.send(embed=log_embed)


async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
