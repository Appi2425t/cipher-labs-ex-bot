import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from database import Database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = os.getenv("DB_PATH", "./data/stake-store.db")


async def get_prefix(bot, message):
    if not message.guild:
        return "."
    try:
        prefix = await bot.db.get_prefix(message.guild.id)
        return commands.when_mentioned_or(prefix)(bot, message)
    except Exception:
        return commands.when_mentioned_or(".")(bot, message)


class CipherLabsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None
        )
        self.db = Database(DB_PATH)

    async def setup_hook(self):
        await self.db.init()
        cog_list = [
            "cogs.tickets",
            "cogs.panel",
            "cogs.exchange",
            "cogs.done",
            "cogs.profile",
            "cogs.setup",
            "cogs.admin",
            "cogs.wallet",
        ]
        for cog in cog_list:
            try:
                await self.load_extension(cog)
                print(f"[COG] Loaded {cog}")
            except Exception as e:
                print(f"[COG] Failed to load {cog}: {e}")

    async def on_ready(self):
        print(f"[BOT] Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Cipher Labs"
        ))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: `{error.param.name}`")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument. Please check your input.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ Channel not found.")
        else:
            print(f"[ERROR] {type(error).__name__}: {error}")


async def main():
    bot = CipherLabsBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
