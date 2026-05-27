import aiohttp
import discord
import json
from datetime import datetime

CATEGORY_INFO = {
    "i2c": {"label": "INR → Crypto", "emoji": "💸", "short": "I2C"},
    "c2i": {"label": "Crypto → INR", "emoji": "💰", "short": "C2I"},
    "c2c": {"label": "Crypto → Crypto", "emoji": "🔄", "short": "C2C"},
    "support": {"label": "Support", "emoji": "🎧", "short": "Support"},
    "dispute": {"label": "Dispute / Issue", "emoji": "⚠️", "short": "Dispute"},
}


def get_category_info(value: str) -> dict:
    return CATEGORY_INFO.get(value.lower(), CATEGORY_INFO["support"])


async def fetch_live_rate() -> float:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://open.er-api.com/v6/latest/USD", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rate = data.get("rates", {}).get("INR")
                    if rate:
                        return float(rate)
    except Exception:
        pass

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.frankfurter.app/latest?from=USD&to=INR", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rate = data.get("rates", {}).get("INR")
                    if rate:
                        return float(rate)
    except Exception:
        pass

    return 84.0


async def get_rate(db, guild_id: int) -> float:
    config = await db.get_config(guild_id)
    override = config.get("rate_override")
    if override and override > 0:
        return override
    return await fetch_live_rate()


def has_staff_role(member: discord.Member, config: dict) -> bool:
    if member.guild_permissions.administrator:
        return True
    member_role_ids = [r.id for r in member.roles]
    for group in ("admin_roles", "mod_roles", "staff_roles", "dealer_roles"):
        role_ids = json.loads(config.get(group, "[]"))
        for rid in role_ids:
            if rid in member_role_ids:
                return True
    return False


def has_admin_or_mod(member: discord.Member, config: dict) -> bool:
    if member.guild_permissions.administrator:
        return True
    member_role_ids = [r.id for r in member.roles]
    for group in ("admin_roles", "mod_roles"):
        role_ids = json.loads(config.get(group, "[]"))
        for rid in role_ids:
            if rid in member_role_ids:
                return True
    return False


def has_admin_role(member: discord.Member, config: dict) -> bool:
    if member.guild_permissions.administrator:
        return True
    member_role_ids = [r.id for r in member.roles]
    role_ids = json.loads(config.get("admin_roles", "[]"))
    for rid in role_ids:
        if rid in member_role_ids:
            return True
    return False


def is_exchanger_role(member: discord.Member, config: dict) -> bool:
    member_role_ids = [r.id for r in member.roles]
    for group in ("staff_roles", "dealer_roles"):
        role_ids = json.loads(config.get(group, "[]"))
        for rid in role_ids:
            if rid in member_role_ids:
                return True
    return False


def hex_to_int(hex_str: str) -> int:
    hex_str = hex_str.lstrip("#")
    return int(hex_str, 16)


def build_ticket_embed(category: str, user: discord.Member, ticket_number: int, claimed_by=None, modal_answers: dict = None, deal_amount_usd: float = None, deal_amount_inr: float = None, config: dict = None) -> discord.Embed:
    info = get_category_info(category)
    embed = discord.Embed(
        title=f"{info['emoji']} {info['label']} — Ticket #{ticket_number:04d}",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Category", value=f"{info['emoji']} {info['label']}", inline=True)
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Ticket Number", value=f"#{ticket_number:04d}", inline=True)

    if claimed_by:
        embed.add_field(name="Status", value=f"✅ Claimed by {claimed_by.mention}", inline=False)
    else:
        embed.add_field(name="Status", value="⏳ Unclaimed", inline=False)

    if modal_answers:
        details = "\n".join(f"**{k}:** {v}" for k, v in modal_answers.items())
        embed.add_field(name="Details", value=details, inline=False)

    # Show calculated exchange amounts
    if category == "i2c" and deal_amount_inr and deal_amount_usd:
        rate = config.get("rate_i2c", 101) if config else 101
        embed.add_field(
            name="💰 Exchange Calculation",
            value=f"**Paying:** ₹{deal_amount_inr:,.2f}\n**Receiving:** ${deal_amount_usd:,.2f}\n**Rate:** ₹{rate} per $1",
            inline=False
        )
    elif category == "c2i" and deal_amount_usd and deal_amount_inr:
        if deal_amount_usd >= 100:
            rate = config.get("rate_c2i_above", 98.5) if config else 98.5
        else:
            rate = config.get("rate_c2i_below", 97.5) if config else 97.5
        embed.add_field(
            name="💰 Exchange Calculation",
            value=f"**Paying:** ${deal_amount_usd:,.2f}\n**Receiving:** ₹{deal_amount_inr:,.2f}\n**Rate:** ₹{rate} per $1",
            inline=False
        )
    elif category == "c2c" and deal_amount_usd:
        rate_c2c = config.get("rate_c2c", 100) if config else 100
        fee_pct = round(100 - rate_c2c, 1)
        receive = deal_amount_usd * (rate_c2c / 100)
        embed.add_field(
            name="💰 Exchange Calculation",
            value=f"**Sending:** ${deal_amount_usd:,.2f}\n**Receiving:** ~${receive:,.2f}\n**Fee:** {fee_pct}%",
            inline=False
        )

    embed.set_footer(text=f"Cipher Labs • {info['short']}")
    return embed


def generate_html_transcript(ticket: dict, messages: list, guild) -> str:
    category_info = get_category_info(ticket.get("category", "support"))
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Transcript — Ticket #{ticket.get('ticket_number', 0):04d}</title>
<style>
body {{
    background-color: #36393f;
    color: #dcddde;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 20px;
}}
.header {{
    background-color: #2f3136;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}}
.header h1 {{
    color: #fff;
    margin: 0 0 10px 0;
}}
.header p {{
    margin: 5px 0;
    color: #b9bbbe;
}}
.message {{
    display: flex;
    padding: 8px 16px;
    margin: 2px 0;
}}
.message:hover {{
    background-color: #32353b;
}}
.avatar {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #5865f2;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    margin-right: 12px;
    flex-shrink: 0;
}}
.content {{
    flex: 1;
}}
.author {{
    font-weight: 600;
    color: #fff;
    margin-right: 8px;
}}
.timestamp {{
    color: #72767d;
    font-size: 0.75rem;
}}
.text {{
    color: #dcddde;
    margin-top: 4px;
    word-wrap: break-word;
}}
.footer {{
    margin-top: 20px;
    padding: 15px;
    background-color: #2f3136;
    border-radius: 8px;
    text-align: center;
    color: #72767d;
}}
</style>
</head>
<body>
<div class="header">
    <h1>{category_info['emoji']} Ticket #{ticket.get('ticket_number', 0):04d} — {category_info['label']}</h1>
    <p><strong>Server:</strong> {guild.name if guild else 'Unknown'}</p>
    <p><strong>Category:</strong> {category_info['label']}</p>
    <p><strong>Opened:</strong> {ticket.get('opened_at', 'Unknown')}</p>
    <p><strong>Closed:</strong> {ticket.get('closed_at', datetime.utcnow().isoformat())}</p>
</div>
"""
    for msg in messages:
        author_name = msg.get("author_name", "Unknown")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        initial = author_name[0].upper() if author_name else "?"
        # Escape HTML
        content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        author_name_escaped = author_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html += f"""
<div class="message">
    <div class="avatar">{initial}</div>
    <div class="content">
        <span class="author">{author_name_escaped}</span>
        <span class="timestamp">{timestamp}</span>
        <div class="text">{content}</div>
    </div>
</div>
"""
    html += f"""
<div class="footer">
    <p>Transcript generated by Cipher Labs Bot • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
    <p>Total messages: {len(messages)}</p>
</div>
</body>
</html>"""
    return html
