import discord
from discord.ext import commands
from utils import has_admin_or_mod, has_admin_role, generate_html_transcript
from cogs.tickets import close_ticket_logic
import asyncio
import io
import subprocess
import sys
import os


ROLE_DUMP = [
    # (name, hex_color, permissions_object, hoist, mentionable)
    # Defined lowest → highest; bot reverses so highest is created last
    (
        ".gg/auraxchange", 0x3498DB,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "CC", 0x2ECC71,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "Crypto exchanger", 0x95A5A6,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "Inr exchanger", 0x95A5A6,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "Verified user", 0x9B59B6,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~Ex Client", 0xF1C40F,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~ Special Peeps", 0xE74C3C,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~ Newbie Client ( 50$+ ) ~", 0xB8860B,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~ Exchanger", 0x1ABC9C,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~Tr Exchanger", 0xF1C40F,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~Sr Exchanger", 0xE67E22,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~ Head Exchanger", 0xFF69B4,
        discord.Permissions(send_messages=True, read_messages=True, read_message_history=True, add_reactions=True, use_application_commands=True),
        False, False,
    ),
    (
        "~ JR.MODERATOR", 0x3498DB,
        discord.Permissions(kick_members=True, manage_messages=True, mute_members=True, view_audit_log=True),
        True, False,
    ),
    (
        "~ SR.MODERATOR", 0xE74C3C,
        discord.Permissions(kick_members=True, ban_members=True, manage_messages=True, mute_members=True, deafen_members=True, move_members=True, manage_channels=True, view_audit_log=True),
        True, False,
    ),
    (
        "~ M A N A G E R", 0x2ECC71,
        discord.Permissions(administrator=True),
        True, False,
    ),
]

CHANNEL_DUMP = [
    # (category_name, channel_name, topic, readonly, locked, open)
    # Category None = top-level (no category)
    (None, "discord-titanxch", "discord.gg/titanxch", True, False, False),
    (None, "telegram-titanexc", "t.me/titanexc", True, False, False),
    ("Important", "tos", "📜 Terms of Service", True, True, False),
    ("Important", "announcements", "📢 Announcements", True, True, False),
    ("Important", "giveaways", "🎉 Giveaways", True, True, False),
    ("Important", "apply", "🎫 Apply", False, True, False),
    ("Important", "recovery", "🌿 Recovery", False, True, False),
    ("Important", "support", "🎟️ Support", False, True, False),
    ("Exchange", "exchange", "💵 Exchange", False, True, False),
    ("Exchange", "cash-exchange", "💴 Cash Exchange", False, True, False),
    ("Legitmacy", "exchange-logs", "📋 Exchange Logs", True, True, False),
    ("Chat Area", "general-chat", "💬 General Chat", False, False, True),
    ("Chat Area", "bot-cmds", "🤖 Bot Commands", False, False, True),
]


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📖 Cipher Labs Bot — Commands",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="💱 Exchange",
            value="`.i2c <INR>` — Calculate INR → USD\n`.c2i <USD>` — Calculate USD → INR\n`.rate` — View current rates",
            inline=False
        )
        embed.add_field(
            name="🎫 Tickets",
            value="`.close` — Close current ticket\n`.add @user` — Add user to ticket\n`.remove @user` — Remove user from ticket\n`.done` — Complete a deal (staff)",
            inline=False
        )
        embed.add_field(
            name="👤 Profile",
            value="`.p [@user]` — Quick profile with exchange stats\n`.profile [@user]` — View full profile & stats\n`.mylimit` — View your exchanger limit",
            inline=False
        )
        embed.add_field(
            name="💳 Wallet",
            value="`.setusdt <addr>` — Save USDT slot 1\n`.setusdt2 <addr>` — Save USDT slot 2\n`.setusdt3 <addr>` — Save USDT slot 3\n`.usdt [@user]` — View USDT addresses\n`.setupi <upi>` — Save UPI slot 1\n`.setupi2 <upi>` — Save UPI slot 2\n`.setupi3 <upi>` — Save UPI slot 3\n`.upi [@user]` — View UPI addresses\n`.wallet [@user]` — View all addresses",
            inline=False
        )
        embed.add_field(
            name="⚙️ Setup (Admin)",
            value="`.setup` — View config\n`.setup transcript #ch` — Set transcript channel\n`.setup logs #ch` — Set log channel\n`.setup vouchchannel #ch` — Set vouch channel\n`.setup category <name>` — Set ticket category\n`.setup addrole <group> @role` — Add role to group\n`.setup removerole <group> @role` — Remove role\n`.setup prefix <p>` — Change prefix\n`.setrate <rate>` — Override USD/INR rate\n`.setexchangerate <type> <rate>` — Set exchange rate\n`.setlimit @user <USD>` — Set deal limit\n`.roledump` — Create all 15 server roles at once",
            inline=False
        )
        embed.add_field(
            name="🔧 Admin",
            value="`.admin tickets` — Open ticket count\n`.admin resetcounter` — Reset ticket counter\n`.admin forceclose #channel` — Force close ticket\n`.addrole @user <role>` — Add role to user\n`.roledump` — Create all 15 server roles\n`.channeldump` — Create all channels & categories\n`.delallch` — Delete all channels (except bot-cmds)\n`.update` — Pull git & restart bot\n`.panel create-exchange` — Create exchange panel\n`.panel create-support` — Create support panel\n`.panel list` — List panels\n`.panel delete <id>` — Delete panel\n`.panel send <id> #ch` — Re-send panel",
            inline=False
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="clist")
    async def clist(self, ctx: commands.Context):
        """Lists all available bot commands with usage."""
        embeds = []

        # Page 1: Exchange & Tickets
        embed1 = discord.Embed(
            title="📜 Command List — Page 1/3",
            description="All commands use the `.` prefix",
            color=discord.Color.purple()
        )
        embed1.add_field(
            name="💱 Exchange & Calculator",
            value=(
                "`.i2c <INR>` — Calculate INR → Crypto\n"
                "  └ Usage: `.i2c 5000`\n"
                "`.c2i <USD>` — Calculate Crypto → INR\n"
                "  └ Usage: `.c2i 50`\n"
                "`.calc <i2c|c2i> <amount>` — Universal calculator\n"
                "  └ Usage: `.calc i2c 5000` or `.calc c2i 100`\n"
                "`.rate` — View all current exchange rates"
            ),
            inline=False
        )
        embed1.add_field(
            name="🎫 Tickets",
            value=(
                "`.close` — Close current ticket (Admin/Mod)\n"
                "  └ Use inside a ticket channel\n"
                "`.add @user` — Add user to ticket channel\n"
                "  └ Usage: `.add @John`\n"
                "`.remove @user` — Remove user from ticket channel\n"
                "  └ Usage: `.remove @John`\n"
                "`.done` — Complete a deal (Staff only)\n"
                "  └ Use inside a ticket channel, opens a modal"
            ),
            inline=False
        )
        embeds.append(embed1)

        # Page 2: Profile, Wallet
        embed2 = discord.Embed(
            title="📜 Command List — Page 2/3",
            color=discord.Color.purple()
        )
        embed2.add_field(
            name="👤 Profile & Limits",
            value=(
                "`.p [@user]` — Quick profile with exchange stats\n"
                "  └ Usage: `.p` or `.p @John`\n"
                "`.profile [@user]` — View full profile & stats\n"
                "  └ Usage: `.profile` or `.profile @John`\n"
                "`.mylimit` — View your exchanger limit\n"
                "  └ Shows total/used/available with bar"
            ),
            inline=False
        )
        embed2.add_field(
            name="💳 Wallet — USDT",
            value=(
                "`.setusdt <address>` — Save USDT slot 1\n"
                "`.setusdt2 <address>` — Save USDT slot 2\n"
                "`.setusdt3 <address>` — Save USDT slot 3\n"
                "`.usdt [@user]` — View USDT slot 1\n"
                "`.usdt2 [@user]` — View USDT slot 2\n"
                "`.usdt3 [@user]` — View USDT slot 3"
            ),
            inline=False
        )
        embed2.add_field(
            name="💳 Wallet — UPI",
            value=(
                "`.setupi <upi_id>` — Save UPI slot 1\n"
                "`.setupi2 <upi_id>` — Save UPI slot 2\n"
                "`.setupi3 <upi_id>` — Save UPI slot 3\n"
                "`.upi [@user]` — View UPI slot 1\n"
                "`.upi2 [@user]` — View UPI slot 2\n"
                "`.upi3 [@user]` — View UPI slot 3\n"
                "`.wallet [@user]` — View all addresses combined\n"
                "`.link <slot> <amount>` — Generate UPI payment link\n"
                "  └ Usage: `.link 1 500`"
            ),
            inline=False
        )
        embed2.add_field(
            name="🔑 Exchange IDs",
            value=(
                "`.setbinance <id>` — Save your Binance ID\n"
                "`.setcwallet <id>` — Save your CWallet ID\n"
                "`.id b [@user]` — View Binance ID\n"
                "`.id c [@user]` — View CWallet ID"
            ),
            inline=False
        )
        embeds.append(embed2)

        # Page 3: Setup & Admin
        embed3 = discord.Embed(
            title="📜 Command List — Page 3/3",
            color=discord.Color.purple()
        )
        embed3.add_field(
            name="⚙️ Setup (Admin Only)",
            value=(
                "`.setup` — View current server config\n"
                "`.setup transcript #channel` — Set transcript channel\n"
                "`.setup logs #channel` — Set log channel\n"
                "`.setup vouchchannel #channel` — Set vouch channel\n"
                "`.setup category <name>` — Set ticket category\n"
                "  └ Usage: `.setup category Tickets`\n"
                "`.setup addrole <group> @role` — Add role to group\n"
                "  └ Groups: admin, mod, staff, dealer\n"
                "  └ Usage: `.setup addrole dealer @Exchanger`\n"
                "`.setup removerole <group> @role` — Remove role\n"
                "`.setup prefix <prefix>` — Change command prefix\n"
                "`.setrate <rate>` — Override USD/INR rate (0 = auto)\n"
                "  └ Usage: `.setrate 85` or `.setrate 0`\n"
                "`.setexchangerate <type> <rate>` — Set exchange rate\n"
                "  └ Types: i2c, c2i_below, c2i_above\n"
                "  └ Usage: `.setexchangerate i2c 103`\n"
                "`.setlimit @user <USD>` — Set exchanger deal limit\n"
                "  └ Usage: `.setlimit @John 500`"
            ),
            inline=False
        )
        embed3.add_field(
            name="🔧 Admin",
            value=(
                "`.admin tickets` — Show open ticket count\n"
                "`.admin resetcounter` — Reset ticket counter to 0\n"
                "`.admin forceclose #channel` — Force close a ticket\n"
                "  └ Usage: `.admin forceclose #i2c-0001-john`\n"
                "`.setdetails @user` — Set exchanger KYC details\n"
                "  └ Usage: `.setdetails @John` (follows prompts)\n"
                "`.viewdetails @user` — View exchanger KYC details\n"
                "  └ Usage: `.viewdetails @John`\n"
                "`.addrole @user <role>` — Add role to user\n"
                "  └ Usage: `.addrole @John ~ Exchanger`\n"
                "`.roledump` — Create all 15 server roles at once\n"
                "`.channeldump` — Create all channels & categories\n"
                "`.delallch` — Delete all channels (keeps bot-cmds)\n"
                "`.update` — Pull git changes & restart bot"
            ),
            inline=False
        )
        embed3.add_field(
            name="🖼️ Panels (Admin Only)",
            value=(
                "`.panel exchange [#channel]` — Post exchange panel\n"
                "  └ Usage: `.panel exchange #exchange`\n"
                "`.panel create-exchange` — Create panel via modal\n"
                "`.panel create-support` — Create support panel\n"
                "`.panel list` — List all panels with IDs\n"
                "`.panel edit <id>` — Edit a panel\n"
                "  └ Usage: `.panel edit 1`\n"
                "`.panel delete <id>` — Delete a panel\n"
                "`.panel send <id> #channel` — Re-send panel\n"
                "  └ Usage: `.panel send 1 #exchange`"
            ),
            inline=False
        )
        embed3.add_field(
            name="📌 Other",
            value=(
                "`.help` — Quick command overview\n"
                "`.clist` — This full command list"
            ),
            inline=False
        )
        embed3.set_footer(text="Cipher Labs • Use . prefix for all commands")
        embeds.append(embed3)

        for embed in embeds:
            await ctx.send(embed=embed)

    @commands.group(name="admin", invoke_without_command=True)
    async def admin_cmd(self, ctx: commands.Context):
        await ctx.send("Usage: `.admin tickets`, `.admin resetcounter`, `.admin forceclose #channel`")

    @admin_cmd.command(name="tickets")
    async def admin_tickets(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_or_mod(ctx.author, config):
            await ctx.send("❌ Admin/Mod only.")
            return
        counts = await self.bot.db.get_open_tickets_by_category(ctx.guild.id)
        if not counts:
            await ctx.send("No open tickets.")
            return
        desc = "\n".join(f"**{cat}:** {count}" for cat, count in counts.items())
        total = sum(counts.values())
        embed = discord.Embed(
            title="🎫 Open Tickets",
            description=f"{desc}\n\n**Total:** {total}",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @admin_cmd.command(name="resetcounter")
    async def admin_resetcounter(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await self.bot.db.reset_ticket_counter(ctx.guild.id)
        await ctx.send("✅ Ticket counter reset to 0.")

    @admin_cmd.command(name="forceclose")
    async def admin_forceclose(self, ctx: commands.Context, channel: discord.TextChannel):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        ticket = await self.bot.db.get_ticket_by_channel(channel.id)
        if not ticket:
            await ctx.send("❌ That channel is not a ticket.")
            return
        await close_ticket_logic(self.bot, channel, ctx.author, ticket, config)
        await ctx.send(f"✅ Force closed ticket in {channel.name}.")

    @commands.command(name="setdetails")
    async def setdetails(self, ctx: commands.Context, member: discord.Member = None):
        """Set exchanger KYC details. Admin only. Usage: .setdetails @user"""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        if not member:
            await ctx.send("❌ Usage: `.setdetails @user`\nThen follow the prompts to enter details and upload documents.")
            return

        # Start collection process
        await ctx.send(
            f"📋 **Setting KYC details for {member.mention}**\n\n"
            f"Please provide the following in your **next message**:\n"
            f"```\n"
            f"Real Name: <full name>\n"
            f"Address: <full address>\n"
            f"```\n"
            f"Type the info exactly like above, or type `cancel` to abort."
        )

        def check_msg(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Step 1: Get name and address
        try:
            msg = await self.bot.wait_for("message", check=check_msg, timeout=120)
        except Exception:
            await ctx.send("❌ Timed out. Please try again.")
            return

        if msg.content.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return

        # Parse name and address
        lines = msg.content.strip().split("\n")
        real_name = ""
        address = ""
        for line in lines:
            if line.lower().startswith("real name:"):
                real_name = line.split(":", 1)[1].strip()
            elif line.lower().startswith("address:"):
                address = line.split(":", 1)[1].strip()

        if not real_name or not address:
            await ctx.send("❌ Could not parse name/address. Make sure to use the format:\n```\nReal Name: John Doe\nAddress: 123 Street, City\n```")
            return

        # Step 2: Aadhar FRONT
        await ctx.send("✅ Got name & address.\n\n📎 **Upload Aadhar card FRONT side** (attach image in your next message).")

        try:
            msg2 = await self.bot.wait_for("message", check=check_msg, timeout=180)
        except Exception:
            await ctx.send("❌ Timed out. Please try again.")
            return
        if msg2.content.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return
        if not msg2.attachments:
            await ctx.send("❌ No image attached. Please try again with `.setdetails @user`")
            return
        aadhar_front_url = msg2.attachments[0].url

        # Step 3: Aadhar BACK
        await ctx.send("✅ Aadhar front saved.\n\n📎 **Upload Aadhar card BACK side** (attach image in your next message).")

        try:
            msg3 = await self.bot.wait_for("message", check=check_msg, timeout=180)
        except Exception:
            await ctx.send("❌ Timed out. Please try again.")
            return
        if msg3.content.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return
        if not msg3.attachments:
            await ctx.send("❌ No image attached. Please try again with `.setdetails @user`")
            return
        aadhar_back_url = msg3.attachments[0].url

        # Step 4: PAN FRONT
        await ctx.send("✅ Aadhar back saved.\n\n📎 **Upload PAN card FRONT side** (attach image in your next message).")

        try:
            msg4 = await self.bot.wait_for("message", check=check_msg, timeout=180)
        except Exception:
            await ctx.send("❌ Timed out. Please try again.")
            return
        if msg4.content.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return
        if not msg4.attachments:
            await ctx.send("❌ No image attached. Please try again with `.setdetails @user`")
            return
        pan_front_url = msg4.attachments[0].url

        # Step 5: PAN BACK
        await ctx.send("✅ PAN front saved.\n\n📎 **Upload PAN card BACK side** (attach image in your next message).")

        try:
            msg5 = await self.bot.wait_for("message", check=check_msg, timeout=180)
        except Exception:
            await ctx.send("❌ Timed out. Please try again.")
            return
        if msg5.content.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return
        if not msg5.attachments:
            await ctx.send("❌ No image attached. Please try again with `.setdetails @user`")
            return
        pan_back_url = msg5.attachments[0].url

        # Save to DB
        await self.bot.db.set_exchanger_details(
            ctx.guild.id, member.id, real_name, address,
            aadhar_front_url, aadhar_back_url, pan_front_url, pan_back_url, ctx.author.id
        )

        # Confirmation embed
        embed = discord.Embed(
            title="✅ Exchanger KYC Details Saved",
            color=discord.Color.green()
        )
        embed.add_field(name="Exchanger", value=member.mention, inline=True)
        embed.add_field(name="Verified By", value=ctx.author.mention, inline=True)
        embed.add_field(name="Real Name", value=real_name, inline=False)
        embed.add_field(name="Address", value=address, inline=False)
        embed.add_field(name="Aadhar Front", value=f"[View]({aadhar_front_url})", inline=True)
        embed.add_field(name="Aadhar Back", value=f"[View]({aadhar_back_url})", inline=True)
        embed.add_field(name="PAN Front", value=f"[View]({pan_front_url})", inline=True)
        embed.add_field(name="PAN Back", value=f"[View]({pan_back_url})", inline=True)
        embed.set_footer(text="Cipher Labs • KYC Verification")
        await ctx.send(embed=embed)

    @commands.command(name="viewdetails")
    async def viewdetails(self, ctx: commands.Context, member: discord.Member = None):
        """View exchanger KYC details. Admin only. Usage: .viewdetails @user"""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        if not member:
            await ctx.send("❌ Usage: `.viewdetails @user`")
            return

        details = await self.bot.db.get_exchanger_details(ctx.guild.id, member.id)
        if not details:
            await ctx.send(f"❌ No KYC details found for {member.mention}.")
            return

        embed = discord.Embed(
            title=f"🔒 KYC Details — {member.display_name}",
            color=discord.Color.orange()
        )
        embed.add_field(name="Real Name", value=details.get("real_name", "N/A"), inline=False)
        embed.add_field(name="Address", value=details.get("address", "N/A"), inline=False)

        aadhar_front = details.get("aadhar_front_url") or details.get("aadhar_url", "")
        aadhar_back = details.get("aadhar_back_url", "")
        pan_front = details.get("pan_front_url") or details.get("pan_url", "")
        pan_back = details.get("pan_back_url", "")

        embed.add_field(
            name="📄 Aadhar Card",
            value=f"Front: {f'[View]({aadhar_front})' if aadhar_front else 'N/A'}\nBack: {f'[View]({aadhar_back})' if aadhar_back else 'N/A'}",
            inline=True
        )
        embed.add_field(
            name="📄 PAN Card",
            value=f"Front: {f'[View]({pan_front})' if pan_front else 'N/A'}\nBack: {f'[View]({pan_back})' if pan_back else 'N/A'}",
            inline=True
        )

        verified_by = details.get("verified_by")
        verified_at = details.get("verified_at", "Unknown")
        embed.add_field(name="Verified By", value=f"<@{verified_by}>" if verified_by else "N/A", inline=True)
        embed.add_field(name="Verified At", value=str(verified_at), inline=True)
        embed.set_footer(text="Cipher Labs • KYC Verification • Admin Only")
        await ctx.send(embed=embed)

    @commands.command(name="roledump")
    @commands.has_permissions(manage_roles=True)
    async def roledump(self, ctx: commands.Context):
        """Create all 15 server roles with correct colors and permissions. Admin only."""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return

        msg = await ctx.send("⏳ Creating roles...")

        existing_roles = [r.name for r in ctx.guild.roles]
        created, skipped, failed = 0, 0, 0

        for name, color, perms, hoist, mentionable in reversed(ROLE_DUMP):
            if name in existing_roles:
                skipped += 1
                continue
            try:
                await ctx.guild.create_role(
                    name=name,
                    color=discord.Color(color),
                    permissions=perms,
                    hoist=hoist,
                    mentionable=mentionable,
                    reason=f"Role dump by {ctx.author}",
                )
                created += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                failed += 1
                print(f"[ROLEDUMP] Failed to create {name}: {e}")

        embed = discord.Embed(
            title="🎉 Role Dump Complete",
            color=discord.Color.green(),
            description=(
                f"✅ Created: **{created}**\n"
                f"⏭️ Skipped: **{skipped}** (already exist)\n"
                f"❌ Failed: **{failed}**"
            ),
        )
        embed.set_footer(text="Cipher Labs • Role Dump")
        await msg.edit(content=None, embed=embed)

    @commands.command(name="channeldump")
    @commands.has_permissions(manage_channels=True)
    async def channeldump(self, ctx: commands.Context):
        """Create all server categories and channels with correct permissions. Admin only."""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return

        msg = await ctx.send("⏳ Creating channels...")

        everyone = ctx.guild.default_role

        # Role lookups for permission overwrites
        role_names = {
            "~ M A N A G E R": None,
            "~ SR.MODERATOR": None,
            "~ JR.MODERATOR": None,
        }
        for r in ctx.guild.roles:
            if r.name in role_names:
                role_names[r.name] = r

        existing_categories = {c.name: c for c in ctx.guild.categories}
        existing_channels = {c.name for c in ctx.guild.channels}

        cat_created, cat_skipped = 0, 0
        ch_created, ch_skipped, ch_failed = 0, 0, 0

        for cat_name, ch_name, topic, readonly, locked, open_ch in CHANNEL_DUMP:
            # Create or find category
            category = None
            if cat_name:
                if cat_name in existing_categories:
                    category = existing_categories[cat_name]
                else:
                    category = await ctx.guild.create_category(
                        cat_name, reason="Channel dump"
                    )
                    existing_categories[cat_name] = category
                    cat_created += 1
                    await asyncio.sleep(0.5)

            # Skip if channel already exists
            if ch_name in existing_channels:
                ch_skipped += 1
                continue

            # Build permission overwrites
            overwrites = {
                everyone: discord.PermissionOverwrite(
                    view_channel=not locked,
                    send_messages=open_ch and not readonly,
                    read_messages=not locked,
                    read_message_history=True,
                )
            }

            # Add staff role overrides for locked channels
            if locked:
                for role_name, role in role_names.items():
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_messages=True,
                            read_message_history=True,
                        )

            try:
                display_name = f"{'🔒 ' if locked else ''}{'📌 ' if readonly and not locked else ''}{ch_name}"
                await ctx.guild.create_text_channel(
                    name=ch_name,
                    category=category,
                    overwrites=overwrites,
                    topic=topic,
                    reason=f"Channel dump by {ctx.author}",
                )
                ch_created += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                ch_failed += 1
                print(f"[CHANNELDUMP] Failed to create {ch_name}: {e}")

        embed = discord.Embed(
            title="🎉 Channel Dump Complete",
            color=discord.Color.blue(),
            description=(
                f"📁 Categories: **{cat_created}** created, **{cat_skipped}** skipped\n"
                f"✅ Channels: **{ch_created}** created\n"
                f"⏭️ Skipped: **{ch_skipped}** (already exist)\n"
                f"❌ Failed: **{ch_failed}**"
            ),
        )
        embed.set_footer(text="Cipher Labs • Channel Dump")
        await msg.edit(content=None, embed=embed)

    @commands.command(name="update")
    @commands.has_permissions(administrator=True)
    async def update(self, ctx: commands.Context):
        """Pull latest code, install deps, and restart the bot. Admin only."""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return

        msg = await ctx.send("🔄 Updating...")

        update_script = os.path.join(os.getcwd(), "update.py")
        if not os.path.exists(update_script):
            await msg.edit(content="❌ update.py not found in project root.")
            return

        try:
            result = subprocess.run(
                [sys.executable, update_script, "--no-restart"],
                capture_output=True, text=True, cwd=os.getcwd(), timeout=120
            )
            output = result.stdout.strip()
        except subprocess.TimeoutExpired:
            await msg.edit(content="❌ Update timed out.")
            return

        embed = discord.Embed(
            title="🔄 Bot Update",
            description=f"```\n{output[:1800]}\n```\n\n♻️ Restarting...",
            color=discord.Color.green() if result.returncode == 0 else discord.Color.orange()
        )
        await msg.edit(content=None, embed=embed)
        await asyncio.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @commands.command(name="delallch")
    @commands.has_permissions(manage_channels=True)
    async def delallch(self, ctx: commands.Context):
        """Delete all channels except bot-cmds. Admin only. Requires confirmation."""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return

        channels = [ch for ch in ctx.guild.channels if ch.name != "bot-cmds"]
        if not channels:
            await ctx.send("❌ No channels to delete (only bot-cmds remains).")
            return

        embed = discord.Embed(
            title="⚠️ Confirm Channel Deletion",
            description=(
                f"This will **delete {len(channels)} channels** and all categories.\n"
                f"`bot-cmds` will be **preserved**.\n\n"
                f"React with ✅ within 30s to confirm, or ❌ to cancel."
            ),
            color=discord.Color.red()
        )
        confirm_msg = await ctx.send(embed=embed)
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ("✅", "❌") and reaction.message.id == confirm_msg.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=30)
        except Exception:
            await confirm_msg.edit(content="❌ Timed out. Cancelled.", embed=None)
            return

        if str(reaction.emoji) == "❌":
            await confirm_msg.edit(content="❌ Cancelled.", embed=None)
            return

        msg = await ctx.send(f"⏳ Deleting {len(channels)} channels...")

        deleted, failed = 0, 0
        for ch in channels:
            try:
                await ch.delete(reason=f"delallch by {ctx.author}")
                deleted += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                failed += 1
                print(f"[DELALLCH] Failed to delete {ch.name}: {e}")

        result = discord.Embed(
            title="🗑️ Channel Deletion Complete",
            description=(
                f"✅ Deleted: **{deleted}**\n"
                f"❌ Failed: **{failed}**"
            ),
            color=discord.Color.green()
        )
        result.set_footer(text="Cipher Labs • Channel Cleanup")
        await msg.edit(content=None, embed=result)

    @commands.command(name="addrole")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx: commands.Context, member: discord.Member = None, *, role_name: str = None):
        """Add a role to a user. Usage: .addrole @user role name"""
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_or_mod(ctx.author, config):
            await ctx.send("❌ Admin/Mod only.")
            return

        if not member or not role_name:
            await ctx.send("❌ Usage: `.addrole @user <role name>`")
            return

        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
        if not role:
            await ctx.send(f"❌ Role `{role_name}` not found.")
            return

        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ That role is equal to or higher than your top role.")
            return

        if role in member.roles:
            await ctx.send(f"❌ {member.mention} already has the `{role.name}` role.")
            return

        try:
            await member.add_roles(role, reason=f"Added by {ctx.author}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to assign that role. Make sure my role is above it.")
            return

        embed = discord.Embed(
            title="✅ Role Added",
            description=f"{member.mention} now has the **{role.name}** role.",
            color=role.color if role.color != discord.Color.default() else discord.Color.green()
        )
        embed.set_footer(text=f"Added by {ctx.author}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
