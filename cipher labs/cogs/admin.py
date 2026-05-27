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
