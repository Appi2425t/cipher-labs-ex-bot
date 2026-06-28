import discord
from discord.ext import commands
from discord import ui
import io
from utils import has_staff_role, generate_html_transcript, get_rate


class DoneModal(ui.Modal, title="✅ Complete Deal"):
    pair = ui.TextInput(label="Currency Pair", placeholder="e.g. USDT to INR", required=True)
    amount_usd = ui.TextInput(label="Amount in USD $", placeholder="e.g. 50 (optional if INR filled)", required=False)
    amount_inr = ui.TextInput(label="Amount in INR ₹", placeholder="e.g. 5000 (optional if USD filled)", required=False)

    def __init__(self, bot, ticket, config):
        super().__init__()
        self.bot = bot
        self.ticket = ticket
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        pair = self.pair.value
        usd_str = self.amount_usd.value.replace(",", "").replace("$", "").strip() if self.amount_usd.value else ""
        inr_str = self.amount_inr.value.replace(",", "").replace("₹", "").strip() if self.amount_inr.value else ""

        amount_usd = None
        amount_inr = None
        rate_used = await get_rate(self.bot.db, interaction.guild_id)

        if usd_str:
            try:
                amount_usd = float(usd_str)
            except ValueError:
                pass
        if inr_str:
            try:
                amount_inr = float(inr_str)
            except ValueError:
                pass

        # Calculate missing amount
        if amount_usd and not amount_inr:
            amount_inr = amount_usd * rate_used
        elif amount_inr and not amount_usd:
            amount_usd = amount_inr / rate_used
        elif not amount_usd and not amount_inr:
            await interaction.followup.send("❌ Please provide at least one amount (USD or INR).", ephemeral=True)
            return

        ticket = self.ticket
        exchanger_id = ticket["claimed_by"] or interaction.user.id
        client_id = ticket["user_id"]

        # Record deal
        await self.bot.db.create_deal(
            interaction.guild_id, ticket["id"], exchanger_id, client_id,
            pair, amount_usd, amount_inr, rate_used
        )

        # Update stats
        await self.bot.db.update_user_stats(interaction.guild_id, exchanger_id, "exchanger", amount_usd, amount_inr)
        await self.bot.db.update_user_stats(interaction.guild_id, client_id, "client", amount_usd, amount_inr)

        # Free exchanger limit
        if ticket.get("deal_amount_usd"):
            await self.bot.db.free_used(interaction.guild_id, exchanger_id, ticket["deal_amount_usd"])

        # Mark ticket as done
        await self.bot.db.update_ticket(ticket["id"], status="done")

        # Send 4 embeds
        client = interaction.guild.get_member(client_id)
        client_name = client.name if client else f"User#{client_id}"

        # Embed 1: Thank you
        embed1 = discord.Embed(
            title="✅ Deal Completed!",
            description="Thank you for choosing **Cipher Labs**!\nYour deal has been successfully completed.",
            color=discord.Color.green()
        )
        embed1.add_field(name="Pair", value=pair, inline=True)
        embed1.add_field(name="USD", value=f"${amount_usd:,.2f}", inline=True)
        embed1.add_field(name="INR", value=f"₹{amount_inr:,.2f}", inline=True)

        # Embed 2: Vouch template
        vouch_text = f"`{client_name} +rep legit exchange ✅ {pair}`"
        embed2 = discord.Embed(
            title="📝 Vouch Template",
            description=f"Copy and paste this in the vouch channel:\n\n{vouch_text}",
            color=discord.Color.blue()
        )

        # Embed 3: Vouch channel instruction
        vouch_channel_id = self.config.get("vouch_channel")
        vouch_mention = f"<#{vouch_channel_id}>" if vouch_channel_id else "#vouch-channel"
        embed3 = discord.Embed(
            title="📌 Post Your Vouch",
            description=f"Please paste the vouch template above in {vouch_mention}",
            color=discord.Color.blue()
        )

        # Embed 4: Warning
        embed4 = discord.Embed(
            title="⚠️ Important",
            description="Skipping vouch may result in restrictions on future exchanges.\nPlease vouch to maintain your standing.",
            color=discord.Color.orange()
        )

        await interaction.channel.send(embeds=[embed1, embed2, embed3, embed4])

        # Generate transcript
        messages = await self.bot.db.get_ticket_messages(ticket["id"])
        guild = interaction.guild
        html = generate_html_transcript(ticket, messages, guild)
        html_bytes = html.encode()

        # Post to transcript channel
        transcript_channel_id = self.config.get("transcript_channel")
        if transcript_channel_id:
            transcript_channel = guild.get_channel(transcript_channel_id)
            if transcript_channel:
                t_embed = discord.Embed(
                    title=f"📝 Deal Transcript — Ticket #{ticket['ticket_number']:04d}",
                    description=f"**Pair:** {pair}\n**USD:** ${amount_usd:,.2f}\n**INR:** ₹{amount_inr:,.2f}\n**Exchanger:** <@{exchanger_id}>\n**Client:** <@{client_id}>",
                    color=discord.Color.green()
                )
                file = discord.File(io.BytesIO(html_bytes), filename=f"transcript-{ticket['ticket_number']:04d}.html")
                await transcript_channel.send(embed=t_embed, file=file)

        # DM client
        if client:
            try:
                dm_embed = discord.Embed(
                    title="✅ Deal Summary — Cipher Labs",
                    description=f"**Pair:** {pair}\n**USD:** ${amount_usd:,.2f}\n**INR:** ₹{amount_inr:,.2f}\n**Rate:** ₹{rate_used:.2f}",
                    color=discord.Color.green()
                )
                dm_embed.set_footer(text=f"Server: {guild.name}")
                file = discord.File(io.BytesIO(html_bytes), filename=f"transcript-{ticket['ticket_number']:04d}.html")
                await client.send(embed=dm_embed, file=file)
            except (discord.Forbidden, discord.HTTPException):
                pass

        # DM exchanger
        exchanger = interaction.guild.get_member(exchanger_id)
        if exchanger:
            try:
                dm_embed = discord.Embed(
                    title="✅ Deal Completed — Cipher Labs",
                    description=f"**Pair:** {pair}\n**USD:** ${amount_usd:,.2f}\n**INR:** ₹{amount_inr:,.2f}\n**Rate:** ₹{rate_used:.2f}\n**Client:** {client_name}",
                    color=discord.Color.green()
                )
                dm_embed.set_footer(text=f"Server: {guild.name}")
                file = discord.File(io.BytesIO(html_bytes), filename=f"transcript-{ticket['ticket_number']:04d}.html")
                await exchanger.send(embed=dm_embed, file=file)
            except (discord.Forbidden, discord.HTTPException):
                pass


class DoneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="done")
    async def done(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_staff_role(ctx.author, config):
            await ctx.send("❌ Staff only.")
            return

        ticket = await self.bot.db.get_ticket_by_channel(ctx.channel.id)
        if not ticket:
            await ctx.send("❌ This is not a ticket channel.")
            return

        if ticket["status"] != "open":
            await ctx.send("❌ This ticket is not open.")
            return

        # Send a button to trigger the modal (commands can't send modals directly)
        view = DoneButtonView(self.bot, ticket, config)
        await ctx.send("Click below to complete the deal:", view=view)


class DoneButtonView(ui.View):
    def __init__(self, bot, ticket, config):
        super().__init__(timeout=120)
        self.bot = bot
        self.ticket = ticket
        self.config = config

    @ui.button(label="Complete Deal", style=discord.ButtonStyle.green, emoji="✅")
    async def done_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(DoneModal(self.bot, self.ticket, self.config))


async def setup(bot):
    await bot.add_cog(DoneCog(bot))
