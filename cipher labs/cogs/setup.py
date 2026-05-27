import discord
from discord.ext import commands
import json
from utils import has_admin_role, has_admin_or_mod, fetch_live_rate


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="setup", invoke_without_command=True)
    async def setup_cmd(self, ctx: commands.Context):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return

        admin_roles = json.loads(config.get("admin_roles", "[]"))
        mod_roles = json.loads(config.get("mod_roles", "[]"))
        staff_roles = json.loads(config.get("staff_roles", "[]"))
        dealer_roles = json.loads(config.get("dealer_roles", "[]"))

        def format_roles(role_ids):
            if not role_ids:
                return "None"
            return ", ".join(f"<@&{r}>" for r in role_ids)

        embed = discord.Embed(title="⚙️ Server Configuration", color=discord.Color.blue())
        embed.add_field(name="Prefix", value=f"`{config.get('prefix', '.')}`", inline=True)
        embed.add_field(name="Log Channel", value=f"<#{config['log_channel']}>" if config.get("log_channel") else "Not set", inline=True)
        embed.add_field(name="Transcript Channel", value=f"<#{config['transcript_channel']}>" if config.get("transcript_channel") else "Not set", inline=True)
        embed.add_field(name="Vouch Channel", value=f"<#{config['vouch_channel']}>" if config.get("vouch_channel") else "Not set", inline=True)
        embed.add_field(name="Ticket Category", value=f"<#{config['ticket_category']}>" if config.get("ticket_category") else "Not set", inline=True)
        embed.add_field(name="Ticket Counter", value=str(config.get("ticket_counter", 0)), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Admin Roles", value=format_roles(admin_roles), inline=True)
        embed.add_field(name="Mod Roles", value=format_roles(mod_roles), inline=True)
        embed.add_field(name="Staff Roles", value=format_roles(staff_roles), inline=True)
        embed.add_field(name="Dealer Roles", value=format_roles(dealer_roles), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Rate Override", value=f"₹{config['rate_override']:.2f}" if config.get("rate_override") else "Auto", inline=True)
        embed.add_field(name="I2C Rate", value=f"₹{config.get('rate_i2c', 101):.2f}", inline=True)
        embed.add_field(name="C2I Below $100", value=f"₹{config.get('rate_c2i_below', 97.5):.2f}", inline=True)
        embed.add_field(name="C2I Above $100", value=f"₹{config.get('rate_c2i_above', 98.5):.2f}", inline=True)
        embed.set_footer(text="Cipher Labs • Configuration")
        await ctx.send(embed=embed)

    @setup_cmd.command(name="transcript")
    async def setup_transcript(self, ctx: commands.Context, channel: discord.TextChannel):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await self.bot.db.update_config(ctx.guild.id, transcript_channel=channel.id)
        await ctx.send(f"✅ Transcript channel set to {channel.mention}")

    @setup_cmd.command(name="logs")
    async def setup_logs(self, ctx: commands.Context, channel: discord.TextChannel):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await self.bot.db.update_config(ctx.guild.id, log_channel=channel.id)
        await ctx.send(f"✅ Log channel set to {channel.mention}")

    @setup_cmd.command(name="vouchchannel")
    async def setup_vouch(self, ctx: commands.Context, channel: discord.TextChannel):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await self.bot.db.update_config(ctx.guild.id, vouch_channel=channel.id)
        await ctx.send(f"✅ Vouch channel set to {channel.mention}")

    @setup_cmd.command(name="category")
    async def setup_category(self, ctx: commands.Context, *, name: str):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        # Find category by name
        category = discord.utils.get(ctx.guild.categories, name=name)
        if not category:
            await ctx.send(f"❌ Category `{name}` not found. Make sure the name matches exactly.")
            return
        await self.bot.db.update_config(ctx.guild.id, ticket_category=category.id)
        await ctx.send(f"✅ Ticket category set to `{category.name}`")

    @setup_cmd.command(name="addrole")
    async def setup_addrole(self, ctx: commands.Context, group: str, role: discord.Role):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        valid_groups = ("admin", "mod", "staff", "dealer")
        if group.lower() not in valid_groups:
            await ctx.send(f"❌ Invalid group. Use: {', '.join(valid_groups)}")
            return
        key = f"{group.lower()}_roles"
        roles = json.loads(config.get(key, "[]"))
        if role.id not in roles:
            roles.append(role.id)
            await self.bot.db.update_config(ctx.guild.id, **{key: json.dumps(roles)})
        await ctx.send(f"✅ {role.mention} added to `{group}` group.")

    @setup_cmd.command(name="removerole")
    async def setup_removerole(self, ctx: commands.Context, group: str, role: discord.Role):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        valid_groups = ("admin", "mod", "staff", "dealer")
        if group.lower() not in valid_groups:
            await ctx.send(f"❌ Invalid group. Use: {', '.join(valid_groups)}")
            return
        key = f"{group.lower()}_roles"
        roles = json.loads(config.get(key, "[]"))
        if role.id in roles:
            roles.remove(role.id)
            await self.bot.db.update_config(ctx.guild.id, **{key: json.dumps(roles)})
        await ctx.send(f"✅ {role.mention} removed from `{group}` group.")

    @setup_cmd.command(name="prefix")
    async def setup_prefix(self, ctx: commands.Context, prefix: str):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await self.bot.db.update_config(ctx.guild.id, prefix=prefix)
        await ctx.send(f"✅ Prefix changed to `{prefix}`")

    @commands.command(name="setrate")
    async def setrate(self, ctx: commands.Context, rate: float):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        if rate == 0:
            await self.bot.db.update_config(ctx.guild.id, rate_override=None)
            await ctx.send("✅ Rate override removed. Using auto (live) rate.")
        else:
            await self.bot.db.update_config(ctx.guild.id, rate_override=rate)
            await ctx.send(f"✅ Rate override set to ₹{rate:.2f}")

    @commands.command(name="setexchangerate")
    async def setexchangerate(self, ctx: commands.Context, rate_type: str, rate: float):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        valid_types = {"i2c": "rate_i2c", "c2i_below": "rate_c2i_below", "c2i_above": "rate_c2i_above"}
        if rate_type.lower() not in valid_types:
            await ctx.send(f"❌ Invalid type. Use: {', '.join(valid_types.keys())}")
            return
        key = valid_types[rate_type.lower()]
        await self.bot.db.update_config(ctx.guild.id, **{key: rate})
        await ctx.send(f"✅ `{rate_type}` rate set to ₹{rate:.2f}")

    @commands.command(name="setlimit")
    async def setlimit(self, ctx: commands.Context, member: discord.Member, limit: float):
        config = await self.bot.db.get_config(ctx.guild.id)
        if not has_admin_role(ctx.author, config):
            await ctx.send("❌ Admin only.")
            return
        await self.bot.db.set_limit(ctx.guild.id, member.id, limit)
        await ctx.send(f"✅ {member.mention}'s deal limit set to **${limit:,.2f}**")


async def setup(bot):
    await bot.add_cog(SetupCog(bot))
