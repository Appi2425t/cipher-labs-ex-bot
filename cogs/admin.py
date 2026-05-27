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


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
