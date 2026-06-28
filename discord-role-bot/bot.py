import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

ROLES = [
    # (name, hex_color, permissions_object, hoist, mentionable)
    # Defined lowest → highest; bot reverses so highest is created last (top of hierarchy)
    (
        ".gg/auraxchange",
        0x3498DB,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "CC",
        0x2ECC71,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "Crypto exchanger",
        0x95A5A6,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "Inr exchanger",
        0x95A5A6,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "Verified user",
        0x9B59B6,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~Ex Client",
        0xF1C40F,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~ Special Peeps",
        0xE74C3C,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~ Newbie Client ( 50$+ ) ~",
        0xB8860B,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~ Exchanger",
        0x1ABC9C,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~Tr Exchanger",
        0xF1C40F,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~Sr Exchanger",
        0xE67E22,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~ Head Exchanger",
        0xFF69B4,
        discord.Permissions(
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True,
            use_application_commands=True,
        ),
        False,
        False,
    ),
    (
        "~ JR.MODERATOR",
        0x3498DB,
        discord.Permissions(
            kick_members=True,
            manage_messages=True,
            mute_members=True,
            view_audit_log=True,
        ),
        True,
        False,
    ),
    (
        "~ SR.MODERATOR",
        0xE74C3C,
        discord.Permissions(
            kick_members=True,
            ban_members=True,
            manage_messages=True,
            mute_members=True,
            deafen_members=True,
            move_members=True,
            manage_channels=True,
            view_audit_log=True,
        ),
        True,
        False,
    ),
    (
        "~ M A N A G E R",
        0x2ECC71,
        discord.Permissions(administrator=True),
        True,
        False,
    ),
]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found!")
        await bot.close()
        return

    existing_roles = [r.name for r in guild.roles]

    for name, color, perms, hoist, mentionable in reversed(ROLES):
        if name in existing_roles:
            print(f"⏭️ Skipped (already exists): {name}")
            continue
        try:
            await guild.create_role(
                name=name,
                color=discord.Color(color),
                permissions=perms,
                hoist=hoist,
                mentionable=mentionable,
                reason="Auto role setup by bot",
            )
            print(f"✅ Created: {name}")
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"❌ Failed to create {name}: {e}")

    print("\n🎉 All roles created successfully!")
    await bot.close()


bot.run(TOKEN)
