# Discord Role Creator Bot

Automatically creates all server roles with correct colors, permissions, and hierarchy order. Run once — roles are created instantly, then the bot disconnects.

## Setup

```bash
pip install -r requirements.txt
```

### 1. Create a Bot Token

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → name it → **Create**
3. Go to **Bot** tab → click **Add Bot**
4. Enable **SERVER MEMBERS INTENT** and **GUILDS INTENT** under Privileged Gateway Intents
5. Click **Copy** under the token

### 2. Get Your Guild (Server) ID

1. Open Discord → **User Settings** → **Advanced** → enable **Developer Mode**
2. Right-click your server icon → **Copy Server ID**

### 3. Configure `.env`

```env
DISCORD_TOKEN=paste_your_token_here
GUILD_ID=paste_your_server_id_here
```

### 4. Invite the Bot

Create an invite link with these permissions:
- `bot` scope
- **Manage Roles** permission (required to create roles)
- The bot's role must be **above** all roles it tries to create in the hierarchy

Use this URL template (replace `CLIENT_ID` with your bot's application ID):

```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=268435456
```

### 5. Run

```bash
python bot.py
```

The bot connects, creates all roles, prints status for each one, and disconnects automatically.

## Re-running

Already existing roles are **skipped** — safe to run multiple times. No duplicates will be created.

## Roles Created

| Role | Color | Permissions |
|---|---|---|
| `~ M A N A G E R` | Green | Administrator |
| `~ SR.MODERATOR` | Red | Kick, Ban, Manage Messages, Mute, Deafen, Move, Channels, Audit Log |
| `~ JR.MODERATOR` | Blue | Kick, Manage Messages, Mute, Audit Log |
| `~ Head Exchanger` | Pink | Basic |
| `~Sr Exchanger` | Orange | Basic |
| `~Tr Exchanger` | Yellow | Basic |
| `~ Exchanger` | Cyan | Basic |
| `~ Newbie Client ( 50$+ ) ~` | Dark Gold | Basic |
| `~ Special Peeps` | Red | Basic |
| `~Ex Client` | Yellow-Green | Basic |
| `Verified user` | Purple | Basic |
| `.gg/auraxchange` | Light Blue | Basic |
| `Inr exchanger` | Grey | Basic |
| `Crypto exchanger` | Grey | Basic |
| `CC` | Green | Basic |

## Customizing

Edit the `ROLES` list in `bot.py`. Each entry is a tuple:

```python
(Role Name, Hex Color, Permissions Object, Hoist, Mentionable)
```

- **Hex Color**: `0x2ECC71` format
- **Hoist**: `True` to show role separately in member list
- **Mentionable**: `True` if `@role` pings are allowed

Roles are created bottom-to-top — list them from lowest to highest priority.
