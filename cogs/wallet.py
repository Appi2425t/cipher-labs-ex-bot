import discord
from discord.ext import commands


class WalletCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- USDT Set Commands ---
    @commands.command(name="setusdt")
    async def setusdt(self, ctx: commands.Context, *, address: str):
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "usdt1", address.strip())
        await ctx.send("✅ USDT address slot 1 saved.")

    @commands.command(name="setusdt2")
    async def setusdt2(self, ctx: commands.Context, *, address: str):
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "usdt2", address.strip())
        await ctx.send("✅ USDT address slot 2 saved.")

    @commands.command(name="setusdt3")
    async def setusdt3(self, ctx: commands.Context, *, address: str):
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "usdt3", address.strip())
        await ctx.send("✅ USDT address slot 3 saved.")

    # --- USDT View Commands ---
    @commands.command(name="usdt")
    async def usdt(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        addr = wallet.get("usdt1") or "Not set"
        embed = discord.Embed(
            title=f"💳 USDT Slot 1 — {target.display_name}",
            description=f"`{addr}`",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="usdt2")
    async def usdt2(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        addr = wallet.get("usdt2") or "Not set"
        embed = discord.Embed(
            title=f"💳 USDT Slot 2 — {target.display_name}",
            description=f"`{addr}`",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="usdt3")
    async def usdt3(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        addr = wallet.get("usdt3") or "Not set"
        embed = discord.Embed(
            title=f"💳 USDT Slot 3 — {target.display_name}",
            description=f"`{addr}`",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    # --- UPI Set Commands ---
    @commands.command(name="setupi")
    async def setupi(self, ctx: commands.Context, *, upi_id: str):
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "upi1", upi_id.strip())
        await ctx.send("✅ UPI address slot 1 saved.")

    @commands.command(name="setupi2")
    async def setupi2(self, ctx: commands.Context, *, upi_id: str):
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "upi2", upi_id.strip())
        await ctx.send("✅ UPI address slot 2 saved.")

    @commands.command(name="setupi3")
    async def setupi3(self, ctx: commands.Context, *, upi_id: str):
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "upi3", upi_id.strip())
        await ctx.send("✅ UPI address slot 3 saved.")

    # --- UPI View Commands ---
    @commands.command(name="upi")
    async def upi(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        addr = wallet.get("upi1") or "Not set"
        embed = discord.Embed(
            title=f"📱 UPI Slot 1 — {target.display_name}",
            description=f"`{addr}`",
            color=discord.Color.green()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="upi2")
    async def upi2(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        addr = wallet.get("upi2") or "Not set"
        embed = discord.Embed(
            title=f"📱 UPI Slot 2 — {target.display_name}",
            description=f"`{addr}`",
            color=discord.Color.green()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @commands.command(name="upi3")
    async def upi3(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        addr = wallet.get("upi3") or "Not set"
        embed = discord.Embed(
            title=f"📱 UPI Slot 3 — {target.display_name}",
            description=f"`{addr}`",
            color=discord.Color.green()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    # --- Combined Wallet ---
    @commands.command(name="wallet")
    async def wallet(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)

        usdt1 = wallet.get("usdt1") or "Not set"
        usdt2 = wallet.get("usdt2") or "Not set"
        usdt3 = wallet.get("usdt3") or "Not set"
        upi1 = wallet.get("upi1") or "Not set"
        upi2 = wallet.get("upi2") or "Not set"
        upi3 = wallet.get("upi3") or "Not set"
        binance = wallet.get("binance_id") or "Not set"
        cwallet = wallet.get("cwallet_id") or "Not set"

        all_empty = all(
            wallet.get(k) is None
            for k in ("usdt1", "usdt2", "usdt3", "upi1", "upi2", "upi3", "binance_id", "cwallet_id")
        )

        embed = discord.Embed(
            title=f"🏦 Wallet — {target.display_name}",
            color=discord.Color.gold()
        )

        if all_empty:
            embed.description = "No addresses saved yet."
        else:
            embed.add_field(
                name="💳 USDT Addresses",
                value=f"**Slot 1:** `{usdt1}`\n**Slot 2:** `{usdt2}`\n**Slot 3:** `{usdt3}`",
                inline=False
            )
            embed.add_field(
                name="📱 UPI Addresses",
                value=f"**Slot 1:** `{upi1}`\n**Slot 2:** `{upi2}`\n**Slot 3:** `{upi3}`",
                inline=False
            )
            embed.add_field(
                name="🔑 Exchange IDs",
                value=f"**🟡 Binance:** `{binance}`\n**💎 CWallet:** `{cwallet}`",
                inline=False
            )

        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    # --- Binance & CWallet ID ---
    @commands.command(name="setbinance")
    async def setbinance(self, ctx: commands.Context, *, binance_id: str):
        """Save your Binance ID. Usage: .setbinance <id>"""
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "binance_id", binance_id.strip())
        await ctx.send("✅ Binance ID saved.")

    @commands.command(name="setcwallet")
    async def setcwallet(self, ctx: commands.Context, *, cwallet_id: str):
        """Save your CWallet ID. Usage: .setcwallet <id>"""
        await self.bot.db.set_wallet_field(ctx.guild.id, ctx.author.id, "cwallet_id", cwallet_id.strip())
        await ctx.send("✅ CWallet ID saved.")

    @commands.group(name="id", invoke_without_command=True)
    async def id_cmd(self, ctx: commands.Context):
        """View exchange IDs. Usage: .id b or .id c"""
        await ctx.send("Usage: `.id b [@user]` — Binance ID\n`.id c [@user]` — CWallet ID")

    @id_cmd.command(name="b")
    async def id_binance(self, ctx: commands.Context, member: discord.Member = None):
        """View Binance ID. Usage: .id b [@user]"""
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        binance = wallet.get("binance_id") or "Not set"
        embed = discord.Embed(
            title=f"🟡 Binance ID — {target.display_name}",
            description=f"`{binance}`",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    @id_cmd.command(name="c")
    async def id_cwallet(self, ctx: commands.Context, member: discord.Member = None):
        """View CWallet ID. Usage: .id c [@user]"""
        target = member or ctx.author
        wallet = await self.bot.db.get_wallet(ctx.guild.id, target.id)
        cwallet = wallet.get("cwallet_id") or "Not set"
        embed = discord.Embed(
            title=f"💎 CWallet ID — {target.display_name}",
            description=f"`{cwallet}`",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Cipher Labs")
        await ctx.send(embed=embed)

    # --- UPI Payment Link ---
    @commands.command(name="link")
    async def link(self, ctx: commands.Context, slot: str = None, amount: str = None):
        """Generate a UPI payment link. Usage: .link <slot 1/2/3> <amount>"""
        if not slot or not amount:
            await ctx.send("❌ Usage: `.link <slot> <amount>`\nExample: `.link 1 500` — generates payment link for your UPI slot 1 with ₹500")
            return

        # Validate slot
        slot = slot.strip()
        if slot not in ("1", "2", "3"):
            await ctx.send("❌ Invalid slot. Use `1`, `2`, or `3`.")
            return

        # Validate amount
        try:
            amt = float(amount.replace(",", "").replace("₹", ""))
            if amt <= 0:
                raise ValueError
        except ValueError:
            await ctx.send("❌ Invalid amount. Use a number like `500` or `1000`.")
            return

        # Get UPI ID from wallet
        field = f"upi{slot}"
        wallet = await self.bot.db.get_wallet(ctx.guild.id, ctx.author.id)
        upi_id = wallet.get(field)

        if not upi_id:
            await ctx.send(f"❌ You don't have a UPI address saved in slot {slot}. Use `.setupi{'2' if slot == '2' else '3' if slot == '3' else ''} <upi_id>` to save one.")
            return

        # Generate UPI payment link
        # Standard UPI deep link format
        upi_link = f"upi://pay?pa={upi_id}&am={amt:.2f}&cu=INR"

        embed = discord.Embed(
            title="📱 UPI Payment Link Generated",
            color=discord.Color.green()
        )
        embed.add_field(name="UPI ID", value=f"`{upi_id}`", inline=True)
        embed.add_field(name="Amount", value=f"₹{amt:,.2f}", inline=True)
        embed.add_field(name="Slot", value=f"#{slot}", inline=True)
        embed.add_field(name="Payment Link", value=f"```\n{upi_link}\n```", inline=False)
        embed.add_field(name="Quick Pay", value=f"[Click to Pay]({upi_link})", inline=False)
        embed.set_footer(text="Cipher Labs • Share this link to receive payment")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WalletCog(bot))
