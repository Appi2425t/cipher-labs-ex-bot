# 🤖 Cipher Labs Bot

A fully-featured Discord bot for crypto-to-INR exchange servers. Built with Python and discord.py.

---

## ✨ Features

- **Ticket System** — Automated ticket creation with categories (I2C, C2I, C2C, Support, Dispute)
- **Exchange Panels** — Interactive dropdown panels that open modals for ticket creation
- **Rate Calculator** — Live USD/INR rate fetching with configurable exchange rates
- **Deal Completion** — Staff can mark deals as done, auto-generate transcripts, DM summaries
- **Profile & Stats** — Track exchanger/client stats, deal history, and limits
- **Wallet Address Book** — Save up to 3 USDT and 3 UPI addresses per user
- **Exchanger Limit System** — Set and track deal limits for exchangers
- **HTML Transcripts** — Dark-themed Discord-style transcripts for closed tickets
- **Role-Based Permissions** — Admin, Mod, Staff, and Dealer role groups
- **Per-Server Config** — Every setting is guild-specific

---

## 📁 File Structure

```
stake-store-bot/
├── bot.py              # Main entry point
├── database.py         # SQLite database (async via aiosqlite)
├── utils.py            # Shared helpers & utilities
├── requirements.txt    # Python dependencies
├── railway.toml        # Railway deployment config
├── .env.example        # Environment variable template
├── README.md           # This file
└── cogs/
    ├── __init__.py
    ├── tickets.py      # Ticket system (open/close/claim)
    ├── panel.py        # Interactive exchange & support panels
    ├── exchange.py     # Rate calculator (.i2c, .c2i, .rate)
    ├── done.py         # Deal completion workflow
    ├── profile.py      # User profiles & limits
    ├── setup.py        # Server configuration
    ├── admin.py        # Admin utilities & help command
    └── wallet.py       # USDT & UPI address book
```

---

## 🛠️ Tech Stack

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11+ | Runtime |
| discord.py | 2.3.2 | Discord API wrapper |
| aiosqlite | 0.19.0 | Async SQLite database |
| python-dotenv | 1.0.0 | Environment variable loading |
| aiohttp | 3.9.1 | HTTP client for live rates |

---

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd stake-store-bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Discord bot token:

```env
DISCORD_TOKEN=your_bot_token_here
PREFIX=.
DB_PATH=./data/stake-store.db
```

### 5. Run the bot

```bash
python bot.py
```

The bot will automatically create the `data/` folder and SQLite database on first run.

---

## 🌐 Deploy to Railway

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Create a Railway project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Select your repository
4. Railway will auto-detect the `railway.toml` config

### 3. Set environment variables on Railway

In your Railway project dashboard, go to **Variables** and add:

| Variable | Value |
|----------|-------|
| `DISCORD_TOKEN` | Your bot token from [Discord Developer Portal](https://discord.com/developers/applications) |
| `PREFIX` | `.` |
| `DB_PATH` | `./data/stake-store.db` |

### 4. Deploy

Railway will automatically build and deploy. The bot starts with:

```
python bot.py
```

The `railway.toml` is pre-configured:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python bot.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 5
```

---

## 🔑 Discord Bot Setup

### Create the bot application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → Name it **"Cipher Labs"**
3. Go to **Bot** tab → Click **"Add Bot"**
4. Copy the **Token** → paste into your `.env` file

### Enable required intents

In the **Bot** tab, enable:

- ✅ **Presence Intent**
- ✅ **Server Members Intent**
- ✅ **Message Content Intent**

### Generate invite link

Go to **OAuth2** → **URL Generator**:

- Scopes: `bot`
- Bot Permissions:
  - Manage Channels
  - Manage Messages
  - Read Messages/View Channels
  - Send Messages
  - Embed Links
  - Attach Files
  - Read Message History
  - Manage Roles

Use the generated URL to invite the bot to your server.

---

## ⚙️ First-Time Server Configuration

After inviting the bot, run these commands in your server:

```
.setup addrole admin @AdminRole
.setup addrole mod @ModRole
.setup addrole staff @StaffRole
.setup addrole dealer @DealerRole
.setup logs #log-channel
.setup transcript #transcript-channel
.setup vouchchannel #vouch-channel
.setup category Tickets
.setlimit @exchanger 500
```

Then create panels:

```
.panel create-exchange
.panel create-support
```

---

## 📋 Command Reference

### Exchange Commands

| Command | Description |
|---------|-------------|
| `.i2c <INR>` | Calculate INR → USD at I2C rate |
| `.c2i <USD>` | Calculate USD → INR at C2I rate |
| `.rate` | View all current exchange rates |

### Ticket Commands

| Command | Description |
|---------|-------------|
| `.close` | Close current ticket (Admin/Mod) |
| `.add @user` | Add user to ticket channel |
| `.remove @user` | Remove user from ticket channel |
| `.done` | Complete a deal (Staff only, in ticket) |

### Profile Commands

| Command | Description |
|---------|-------------|
| `.profile [@user]` | View profile & stats |
| `.mylimit` | View your exchanger limit |

### Wallet Commands

| Command | Description |
|---------|-------------|
| `.setusdt <address>` | Save USDT address slot 1 |
| `.setusdt2 <address>` | Save USDT address slot 2 |
| `.setusdt3 <address>` | Save USDT address slot 3 |
| `.usdt [@user]` | View USDT addresses |
| `.usdt2 [@user]` | View USDT slot 2 |
| `.usdt3 [@user]` | View USDT slot 3 |
| `.setupi <upi_id>` | Save UPI address slot 1 |
| `.setupi2 <upi_id>` | Save UPI address slot 2 |
| `.setupi3 <upi_id>` | Save UPI address slot 3 |
| `.upi [@user]` | View UPI addresses |
| `.upi2 [@user]` | View UPI slot 2 |
| `.upi3 [@user]` | View UPI slot 3 |
| `.wallet [@user]` | View all saved addresses |

### Setup Commands (Admin)

| Command | Description |
|---------|-------------|
| `.setup` | View current server config |
| `.setup transcript #channel` | Set transcript channel |
| `.setup logs #channel` | Set log channel |
| `.setup vouchchannel #channel` | Set vouch channel |
| `.setup category <name>` | Set ticket category |
| `.setup addrole <group> @role` | Add role to group (admin/mod/staff/dealer) |
| `.setup removerole <group> @role` | Remove role from group |
| `.setup prefix <prefix>` | Change command prefix |
| `.setrate <rate>` | Override USD/INR rate (0 = auto) |
| `.setexchangerate <type> <rate>` | Set exchange rate (i2c/c2i_below/c2i_above) |
| `.setlimit @user <USD>` | Set exchanger deal limit |

### Admin Commands

| Command | Description |
|---------|-------------|
| `.help` | Show full command list |
| `.admin tickets` | Show open ticket count by category |
| `.admin resetcounter` | Reset ticket counter to 0 |
| `.admin forceclose #channel` | Force close any ticket |

### Panel Commands (Admin)

| Command | Description |
|---------|-------------|
| `.panel create-exchange` | Create exchange panel |
| `.panel create-support` | Create support panel |
| `.panel list` | List all panels |
| `.panel delete <id>` | Delete a panel |
| `.panel send <id> #channel` | Re-send panel to channel |

---

## 🗄️ Database

The bot uses SQLite with async access via `aiosqlite`. The database is automatically created at the path specified in `DB_PATH`.

### Tables

- `guild_config` — Per-server settings (prefix, channels, roles, rates)
- `panels` — Stored panel messages for persistence
- `tickets` — Active and closed tickets
- `ticket_messages` — Message log for transcripts
- `exchanger_limits` — Deal limits per exchanger
- `deals` — Completed deal records
- `user_stats` — Aggregated stats per user per role
- `user_wallets` — USDT and UPI addresses (3 slots each)

---

## 🔄 How the Exchange Flow Works

1. **User** clicks a panel dropdown → selects exchange type → fills modal
2. **Bot** creates a private ticket channel with deal details
3. **Staff/Dealer** clicks "Claim" → limit is checked and reserved
4. Exchange happens in the ticket channel
5. **Staff** runs `.done` → fills completion modal
6. **Bot** records the deal, updates stats, frees limit, generates transcript
7. **Bot** DMs both parties with deal summary + transcript file
8. Vouch instructions are posted in the ticket

---

## 📝 Notes

- The bot uses **dot prefix only** (`.`) — no slash commands
- All views (buttons, dropdowns) are **persistent** and survive bot restarts
- Transcripts use **Discord dark-theme** HTML styling
- Rate fetching has **dual fallback**: open.er-api.com → frankfurter.app → 84.0
- Permission checks use the **role group system**, not raw Discord permissions (server admin is always a fallback)

---

## 📄 License

This project is private. All rights reserved.
