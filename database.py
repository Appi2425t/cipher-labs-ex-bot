import aiosqlite
import json
import os


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("DB_PATH", "./data/stake-store.db")

    async def init(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_config (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT '.',
                    log_channel INTEGER,
                    transcript_channel INTEGER,
                    ticket_category INTEGER,
                    admin_roles TEXT DEFAULT '[]',
                    mod_roles TEXT DEFAULT '[]',
                    staff_roles TEXT DEFAULT '[]',
                    dealer_roles TEXT DEFAULT '[]',
                    ticket_counter INTEGER DEFAULT 0,
                    vouch_channel INTEGER,
                    rate_override REAL,
                    rate_i2c REAL DEFAULT 101,
                    rate_c2i_below REAL DEFAULT 97.5,
                    rate_c2i_above REAL DEFAULT 98.5,
                    rate_c2c REAL DEFAULT 100
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS panels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    title TEXT,
                    description TEXT,
                    color INTEGER DEFAULT 3447003,
                    footer TEXT,
                    thumbnail TEXT,
                    panel_type TEXT DEFAULT 'exchange',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    category TEXT,
                    status TEXT DEFAULT 'open',
                    ticket_number INTEGER,
                    claimed_by INTEGER,
                    deal_amount_usd REAL,
                    deal_amount_inr REAL,
                    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ticket_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    author_name TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS exchanger_limits (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    limit_usd REAL DEFAULT 0,
                    used_usd REAL DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    ticket_id INTEGER NOT NULL,
                    exchanger_id INTEGER NOT NULL,
                    client_id INTEGER NOT NULL,
                    pair TEXT,
                    amount_usd REAL,
                    amount_inr REAL,
                    rate_used REAL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    total_deals INTEGER DEFAULT 0,
                    total_usd REAL DEFAULT 0,
                    total_inr REAL DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id, role)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_wallets (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    usdt1 TEXT,
                    usdt2 TEXT,
                    usdt3 TEXT,
                    upi1 TEXT,
                    upi2 TEXT,
                    upi3 TEXT,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.commit()

    async def _connect(self):
        return aiosqlite.connect(self.db_path)

    # --- Guild Config ---
    async def get_config(self, guild_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            if row:
                return dict(row)
            await db.execute("INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)", (guild_id,))
            await db.commit()
            cursor = await db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            return dict(row)

    async def update_config(self, guild_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)", (guild_id,))
            for key, value in kwargs.items():
                await db.execute(f"UPDATE guild_config SET {key} = ? WHERE guild_id = ?", (value, guild_id))
            await db.commit()

    async def get_prefix(self, guild_id: int) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT prefix FROM guild_config WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            return row[0] if row else "."

    async def increment_ticket_counter(self, guild_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)", (guild_id,))
            await db.execute("UPDATE guild_config SET ticket_counter = ticket_counter + 1 WHERE guild_id = ?", (guild_id,))
            await db.commit()
            cursor = await db.execute("SELECT ticket_counter FROM guild_config WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            return row[0]

    async def reset_ticket_counter(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE guild_config SET ticket_counter = 0 WHERE guild_id = ?", (guild_id,))
            await db.commit()

    # --- Panels ---
    async def create_panel(self, guild_id: int, channel_id: int, message_id: int, title: str, description: str, color: int, footer: str, thumbnail: str, panel_type: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO panels (guild_id, channel_id, message_id, title, description, color, footer, thumbnail, panel_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (guild_id, channel_id, message_id, title, description, color, footer, thumbnail, panel_type)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_panels(self, guild_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM panels WHERE guild_id = ?", (guild_id,))
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_panel(self, panel_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM panels WHERE id = ?", (panel_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def delete_panel(self, panel_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM panels WHERE id = ?", (panel_id,))
            await db.commit()

    # --- Tickets ---
    async def create_ticket(self, guild_id: int, channel_id: int, user_id: int, category: str, ticket_number: int, deal_amount_usd: float = None, deal_amount_inr: float = None) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO tickets (guild_id, channel_id, user_id, category, ticket_number, deal_amount_usd, deal_amount_inr) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (guild_id, channel_id, user_id, category, ticket_number, deal_amount_usd, deal_amount_inr)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_open_ticket(self, guild_id: int, user_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tickets WHERE guild_id = ? AND user_id = ? AND status = 'open'",
                (guild_id, user_id)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_ticket_by_channel(self, channel_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM tickets WHERE channel_id = ?", (channel_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_ticket(self, ticket_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            for key, value in kwargs.items():
                await db.execute(f"UPDATE tickets SET {key} = ? WHERE id = ?", (value, ticket_id))
            await db.commit()

    async def close_ticket(self, ticket_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE tickets SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE id = ?", (ticket_id,))
            await db.commit()

    async def get_open_tickets_by_category(self, guild_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT category, COUNT(*) as cnt FROM tickets WHERE guild_id = ? AND status = 'open' GROUP BY category",
                (guild_id,)
            )
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}

    # --- Ticket Messages ---
    async def log_message(self, ticket_id: int, author_id: int, author_name: str, content: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO ticket_messages (ticket_id, author_id, author_name, content) VALUES (?, ?, ?, ?)",
                (ticket_id, author_id, author_name, content)
            )
            await db.commit()

    async def get_ticket_messages(self, ticket_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM ticket_messages WHERE ticket_id = ? ORDER BY timestamp ASC",
                (ticket_id,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    # --- Exchanger Limits ---
    async def get_limit(self, guild_id: int, user_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM exchanger_limits WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return {"guild_id": guild_id, "user_id": user_id, "limit_usd": 0, "used_usd": 0}

    async def set_limit(self, guild_id: int, user_id: int, limit_usd: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO exchanger_limits (guild_id, user_id, limit_usd) VALUES (?, ?, ?) ON CONFLICT(guild_id, user_id) DO UPDATE SET limit_usd = ?",
                (guild_id, user_id, limit_usd, limit_usd)
            )
            await db.commit()

    async def add_used(self, guild_id: int, user_id: int, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE exchanger_limits SET used_usd = used_usd + ? WHERE guild_id = ? AND user_id = ?",
                (amount, guild_id, user_id)
            )
            await db.commit()

    async def free_used(self, guild_id: int, user_id: int, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE exchanger_limits SET used_usd = MAX(0, used_usd - ?) WHERE guild_id = ? AND user_id = ?",
                (amount, guild_id, user_id)
            )
            await db.commit()

    # --- Deals ---
    async def create_deal(self, guild_id: int, ticket_id: int, exchanger_id: int, client_id: int, pair: str, amount_usd: float, amount_inr: float, rate_used: float) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO deals (guild_id, ticket_id, exchanger_id, client_id, pair, amount_usd, amount_inr, rate_used) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (guild_id, ticket_id, exchanger_id, client_id, pair, amount_usd, amount_inr, rate_used)
            )
            await db.commit()
            return cursor.lastrowid

    # --- User Stats ---
    async def get_user_stats(self, guild_id: int, user_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM user_stats WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def update_user_stats(self, guild_id: int, user_id: int, role: str, amount_usd: float, amount_inr: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO user_stats (guild_id, user_id, role, total_deals, total_usd, total_inr)
                   VALUES (?, ?, ?, 1, ?, ?)
                   ON CONFLICT(guild_id, user_id, role) DO UPDATE SET
                   total_deals = total_deals + 1,
                   total_usd = total_usd + ?,
                   total_inr = total_inr + ?""",
                (guild_id, user_id, role, amount_usd, amount_inr, amount_usd, amount_inr)
            )
            await db.commit()

    # --- Wallets ---
    async def get_wallet(self, guild_id: int, user_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM user_wallets WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return {"guild_id": guild_id, "user_id": user_id, "usdt1": None, "usdt2": None, "usdt3": None, "upi1": None, "upi2": None, "upi3": None}

    async def set_wallet_field(self, guild_id: int, user_id: int, field: str, value: str):
        valid_fields = ("usdt1", "usdt2", "usdt3", "upi1", "upi2", "upi3")
        if field not in valid_fields:
            raise ValueError(f"Invalid wallet field: {field}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""INSERT INTO user_wallets (guild_id, user_id, {field})
                    VALUES (?, ?, ?)
                    ON CONFLICT(guild_id, user_id) DO UPDATE SET {field} = ?""",
                (guild_id, user_id, value, value)
            )
            await db.commit()
