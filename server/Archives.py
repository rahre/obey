"""
The Archives: Persistent History Module
Theme: Black Knights Archives
"""
import aiosqlite
import datetime
from pathlib import Path

DB_PATH = Path("data/archives.db")

async def init_db():
    """Initializes the SQLite database."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                last_username TEXT,
                last_seen TIMESTAMP,
                last_status TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS username_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                changed_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        await db.commit()

async def update_user(user_id: int, username: str, status: str = None):
    """Updates user info and logs username changes."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Check current record
        async with db.execute("SELECT last_username FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            
            now = datetime.datetime.now()
            
            if row:
                old_username = row[0]
                if old_username != username:
                    # Log history
                    await db.execute("INSERT INTO username_history (user_id, username, changed_at) VALUES (?, ?, ?)", 
                                   (user_id, old_username, now))
                
                await db.execute("UPDATE users SET last_username = ?, last_seen = ?, last_status = ? WHERE user_id = ?",
                               (username, now, status, user_id))
            else:
                await db.execute("INSERT INTO users (user_id, last_username, last_seen, last_status) VALUES (?, ?, ?, ?)",
                               (user_id, username, now, status))
        
        await db.commit()

async def get_history(user_id: int):
    """Retrieves username history for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT username, changed_at FROM username_history WHERE user_id = ? ORDER BY changed_at DESC", (user_id,)) as cursor:
            return await cursor.fetchall()

async def get_user_data(user_id: int):
    """Retrieves basic info for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT last_username, last_seen, last_status FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()
