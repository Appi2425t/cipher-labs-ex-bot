import discord
from discord.ext import commands
from utils import fetch_live_rate, get_rate


class ExchangeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="i2c")
    async def i2c(self, ctx: commands.Context, amount: str = None):
        if not amount:
            await ctx.send("Usage: `.i2c <INR amount>`")
            return
        try:
            inr_amount = float(amount.replace(",", "").replace("₹", ""))
        except ValueError:
            await ctx.send("❌ Invalid amount. Use a number.")
            return

        config = await self.bot.db.get_config(ctx.guild.id)
        rate = config.get("rate_i2c") or 101
        usd = inr_amount / rate

        embed = discord.Embed(
            title="💸 INR → Crypto Calculator",
            color=discord.Color.green()
        )
        embed.add_field(name="You Pay", value=f"₹{inr_amount:,.2f}", inline=True)
        embed.add_field(name="You Receive", value=f"${usd:,.2f}", inline=True)
        embed.add_field(name="Rate", value=f"₹{rate:.2f} per $1", inline=False)
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="c2i")
    async def c2i(self, ctx: commands.Context, amount: str = None):
        if not amount:
            await ctx.send("Usage: `.c2i <USD amount>`")
            return
        try:
            usd_amount = float(amount.replace(",", "").replace("$", ""))
        except ValueError:
            await ctx.send("❌ Invalid amount. Use a number.")
            return

        config = await self.bot.db.get_config(ctx.guild.id)
        if usd_amount >= 100:
            rate = config.get("rate_c2i_above") or 98.5
            tier = "≥ $100"
        else:
            rate = config.get("rate_c2i_below") or 97.5
            tier = "< $100"

        inr = usd_amount * rate

        embed = discord.Embed(
            title="💰 Crypto → INR Calculator",
            color=discord.Color.gold()
        )
        embed.add_field(name="You Pay", value=f"${usd_amount:,.2f}", inline=True)
        embed.add_field(name="You Receive", value=f"₹{inr:,.2f}", inline=True)
        embed.add_field(name="Rate", value=f"₹{rate:.2f} per $1 ({tier})", inline=False)
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="rate")
    async def rate(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        live_rate = await fetch_live_rate()
        override = config.get("rate_override")
        rate_i2c = config.get("rate_i2c") or 101
        rate_c2i_below = config.get("rate_c2i_below") or 97.5
        rate_c2i_above = config.get("rate_c2i_above") or 98.5
        rate_c2c = config.get("rate_c2c") or 100

        rate_source = "🟢 Auto (Live)" if not override or override == 0 else f"🟡 Manual Override: ₹{override:.2f}"

        embed = discord.Embed(
            title="📊 Current Exchange Rates",
            color=discord.Color.blue()
        )
        embed.add_field(name="Live USD/INR", value=f"₹{live_rate:.2f}", inline=True)
        embed.add_field(name="Rate Source", value=rate_source, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="💸 I2C Rate (INR → Crypto)", value=f"₹{rate_i2c:.2f} per $1", inline=True)
        embed.add_field(name="💰 C2I Rate (< $100)", value=f"₹{rate_c2i_below:.2f} per $1", inline=True)
        embed.add_field(name="💰 C2I Rate (≥ $100)", value=f"₹{rate_c2i_above:.2f} per $1", inline=True)
        embed.add_field(name="🔄 C2C Rate", value=f"{rate_c2c:.2f}%", inline=True)
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="calc")
    async def calc(self, ctx: commands.Context, direction: str = None, amount: str = None):
        """Universal calculator. Usage: .calc i2c 5000 OR .calc c2i 50"""
        if not direction or not amount:
            await ctx.send(
                "**📐 Calculator Usage:**\n"
                "`.calc i2c <INR>` — Calculate INR → Crypto\n"
                "`.calc c2i <USD>` — Calculate Crypto → INR\n\n"
                "**Shortcuts:**\n"
                "`.i2c <INR>` — Same as .calc i2c\n"
                "`.c2i <USD>` — Same as .calc c2i"
            )
            return

        direction = direction.lower()
        if direction == "i2c":
            await self.i2c(ctx, amount)
        elif direction == "c2i":
            await self.c2i(ctx, amount)
        else:
            await ctx.send("❌ Invalid type. Use `i2c` or `c2i`.\nExample: `.calc i2c 5000` or `.calc c2i 50`")


async def setup(bot):
    await bot.add_cog(ExchangeCog(bot))
