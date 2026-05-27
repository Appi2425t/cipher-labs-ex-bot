import discord
from discord.ext import commands
from utils import has_admin_or_mod, has_admin_role, generate_html_transcript
from cogs.tickets import close_ticket_logic
import io


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
            value="`.profile [@user]` — View profile & stats\n`.mylimit` — View your exchanger limit",
            inline=False
        )
        embed.add_field(
            name="💳 Wallet",
            value="`.setusdt <addr>` — Save USDT slot 1\n`.setusdt2 <addr>` — Save USDT slot 2\n`.setusdt3 <addr>` — Save USDT slot 3\n`.usdt [@user]` — View USDT addresses\n`.setupi <upi>` — Save UPI slot 1\n`.setupi2 <upi>` — Save UPI slot 2\n`.setupi3 <upi>` — Save UPI slot 3\n`.upi [@user]` — View UPI addresses\n`.wallet [@user]` — View all addresses",
            inline=False
        )
        embed.add_field(
            name="⚙️ Setup (Admin)",
            value="`.setup` — View config\n`.setup transcript #ch` — Set transcript channel\n`.setup logs #ch` — Set log channel\n`.setup vouchchannel #ch` — Set vouch channel\n`.setup category <name>` — Set ticket category\n`.setup addrole <group> @role` — Add role to group\n`.setup removerole <group> @role` — Remove role\n`.setup prefix <p>` — Change prefix\n`.setrate <rate>` — Override USD/INR rate\n`.setexchangerate <type> <rate>` — Set exchange rate\n`.setlimit @user <USD>` — Set deal limit",
            inline=False
        )
        embed.add_field(
            name="🔧 Admin",
            value="`.admin tickets` — Open ticket count\n`.admin resetcounter` — Reset ticket counter\n`.admin forceclose #channel` — Force close ticket\n`.panel create-exchange` — Create exchange panel\n`.panel create-support` — Create support panel\n`.panel list` — List panels\n`.panel delete <id>` — Delete panel\n`.panel send <id> #ch` — Re-send panel",
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
                "`.profile [@user]` — View profile & stats\n"
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
                "`.usdt [@user]` — View all USDT addresses\n"
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
                "`.upi [@user]` — View all UPI addresses\n"
                "`.upi2 [@user]` — View UPI slot 2\n"
                "`.upi3 [@user]` — View UPI slot 3\n"
                "`.wallet [@user]` — View all addresses combined"
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
                "  └ Usage: `.admin forceclose #i2c-0001-john`"
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

        # Step 2: Get Aadhar image
        await ctx.send(f"✅ Got name & address.\n\n📎 Now **upload the Aadhar card image** (attach image in your next message), or type `skip` to skip.")

        try:
            msg2 = await self.bot.wait_for("message", check=check_msg, timeout=120)
        except Exception:
            await ctx.send("❌ Timed out. Please try again.")
            return

        aadhar_url = ""
        if msg2.content.lower() == "skip":
            aadhar_url = "Not provided"
        elif msg2.attachments:
            aadhar_url = msg2.attachments[0].url
        else:
            await ctx.send("❌ No image attached. Please try again with `.setdetails @user`")
            return

        # Step 3: Get PAN image
        await ctx.send(f"✅ Aadhar saved.\n\n📎 Now **upload the PAN card image** (attach image in your next message), or type `skip` to skip.")

        try:
            msg3 = await self.bot.wait_for("message", check=check_msg, timeout=120)
        except Exception:
            await ctx.send("❌ Timed out. Please try again.")
            return

        pan_url = ""
        if msg3.content.lower() == "skip":
            pan_url = "Not provided"
        elif msg3.attachments:
            pan_url = msg3.attachments[0].url
        else:
            await ctx.send("❌ No image attached. Please try again with `.setdetails @user`")
            return

        # Save to DB
        await self.bot.db.set_exchanger_details(
            ctx.guild.id, member.id, real_name, address, aadhar_url, pan_url, ctx.author.id
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
        if aadhar_url and aadhar_url != "Not provided":
            embed.add_field(name="Aadhar", value=f"[View Image]({aadhar_url})", inline=True)
        else:
            embed.add_field(name="Aadhar", value="Not provided", inline=True)
        if pan_url and pan_url != "Not provided":
            embed.add_field(name="PAN", value=f"[View Image]({pan_url})", inline=True)
        else:
            embed.add_field(name="PAN", value="Not provided", inline=True)
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

        aadhar_url = details.get("aadhar_url", "")
        pan_url = details.get("pan_url", "")

        if aadhar_url and aadhar_url != "Not provided":
            embed.add_field(name="Aadhar Card", value=f"[View Image]({aadhar_url})", inline=True)
            embed.set_image(url=aadhar_url)
        else:
            embed.add_field(name="Aadhar Card", value="Not provided", inline=True)

        if pan_url and pan_url != "Not provided":
            embed.add_field(name="PAN Card", value=f"[View Image]({pan_url})", inline=True)
        else:
            embed.add_field(name="PAN Card", value="Not provided", inline=True)

        verified_by = details.get("verified_by")
        verified_at = details.get("verified_at", "Unknown")
        embed.add_field(name="Verified By", value=f"<@{verified_by}>" if verified_by else "N/A", inline=True)
        embed.add_field(name="Verified At", value=str(verified_at), inline=True)
        embed.set_footer(text="Cipher Labs • KYC Verification • Admin Only")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
