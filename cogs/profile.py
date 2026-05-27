import discord
from discord.ext import commands
from utils import is_exchanger_role


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        guild_id = ctx.guild.id

        stats = await self.bot.db.get_user_stats(guild_id, member.id)
        limit_data = await self.bot.db.get_limit(guild_id, member.id)
        config = await self.bot.db.get_config(guild_id)

        exchanger_stats = None
        client_stats = None
        for s in stats:
            if s["role"] == "exchanger":
                exchanger_stats = s
            elif s["role"] == "client":
                client_stats = s

        # Determine status
        has_exchanger = exchanger_stats is not None
        has_client = client_stats is not None
        if has_exchanger and has_client:
            status = "Both (Exchanger & Client)"
        elif has_exchanger:
            status = "Exchanger"
        elif has_client:
            status = "Client"
        else:
            status = "New Member"

        embed = discord.Embed(
            title=f"👤 Profile — {member.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Status", value=status, inline=False)

        # Exchanger stats
        if exchanger_stats:
            total_deals = exchanger_stats["total_deals"]
            total_usd = exchanger_stats["total_usd"]
            total_inr = exchanger_stats["total_inr"]
            avg = total_usd / total_deals if total_deals > 0 else 0
            embed.add_field(
                name="📊 Exchanger Stats",
                value=f"Deals: **{total_deals}**\nTotal USD: **${total_usd:,.2f}**\nTotal INR: **₹{total_inr:,.2f}**\nAvg Deal: **${avg:,.2f}**",
                inline=True
            )

        # Limit
        limit_usd = limit_data["limit_usd"]
        used_usd = limit_data["used_usd"]
        available = max(0, limit_usd - used_usd)
        if limit_usd > 0:
            pct = min(10, int((used_usd / limit_usd) * 10))
        else:
            pct = 0
        bar = "🟩" * pct + "⬜" * (10 - pct)
        embed.add_field(
            name="📈 Limit",
            value=f"Total: **${limit_usd:,.2f}**\nIn Use: **${used_usd:,.2f}**\nAvailable: **${available:,.2f}**\n{bar}",
            inline=True
        )

        # Client stats
        if client_stats:
            total_deals = client_stats["total_deals"]
            total_usd = client_stats["total_usd"]
            total_inr = client_stats["total_inr"]
            avg = total_usd / total_deals if total_deals > 0 else 0
            embed.add_field(
                name="🛒 Client Stats",
                value=f"Deals: **{total_deals}**\nTotal USD: **${total_usd:,.2f}**\nTotal INR: **₹{total_inr:,.2f}**\nAvg Deal: **${avg:,.2f}**",
                inline=False
            )

        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="mylimit")
    async def mylimit(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        limit_data = await self.bot.db.get_limit(guild_id, ctx.author.id)

        limit_usd = limit_data["limit_usd"]
        used_usd = limit_data["used_usd"]
        available = max(0, limit_usd - used_usd)
        if limit_usd > 0:
            pct = min(10, int((used_usd / limit_usd) * 10))
        else:
            pct = 0
        bar = "🟩" * pct + "⬜" * (10 - pct)

        embed = discord.Embed(
            title=f"📈 Your Exchanger Limit",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total Limit", value=f"${limit_usd:,.2f}", inline=True)
        embed.add_field(name="In Use", value=f"${used_usd:,.2f}", inline=True)
        embed.add_field(name="Available", value=f"${available:,.2f}", inline=True)
        embed.add_field(name="Usage", value=bar, inline=False)
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
