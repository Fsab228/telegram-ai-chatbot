"""
Database queries for Telegram AI Chatbot
"""
import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List
from database.models import User, Conversation
from config import Config

logger = logging.getLogger(__name__)


class Database:
    """Database manager for SQLite operations"""
    
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        self.db_path = db_path
    
    async def init_db(self) -> None:
        """Initialize database tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_user_timestamp 
                    ON conversations(user_id, timestamp DESC)
                """)
                
                await db.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def add_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        """Add or update user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO users (user_id, username, first_name, created_at)
                    VALUES (?, ?, ?, COALESCE((SELECT created_at FROM users WHERE user_id = ?), CURRENT_TIMESTAMP))
                """, (user_id, username, first_name, user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            raise
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return User(
                            user_id=row["user_id"],
                            username=row["username"],
                            first_name=row["first_name"],
                            created_at=datetime.fromisoformat(row["created_at"])
                        )
                    return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """Add message to conversation history"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO conversations (user_id, role, content)
                    VALUES (?, ?, ?)
                """, (user_id, role, content))
                await db.commit()
        except Exception as e:
            logger.error(f"Error adding message for user {user_id}: {e}")
            raise
    
    async def get_conversation_history(self, user_id: int, limit: int = Config.CONVERSATION_HISTORY_LIMIT) -> List[Conversation]:
        """Get conversation history for user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT * FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    conversations = []
                    for row in reversed(rows):
                        conversations.append(Conversation(
                            user_id=row["user_id"],
                            role=row["role"],
                            content=row["content"],
                            timestamp=datetime.fromisoformat(row["timestamp"])
                        ))
                    return conversations
        except Exception as e:
            logger.error(f"Error getting conversation history for user {user_id}: {e}")
            return []
    
    async def clear_conversation_history(self, user_id: int) -> None:
        """Clear conversation history for user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
                await db.commit()
                logger.info(f"Cleared conversation history for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing conversation history for user {user_id}: {e}")
            raise
    
    async def get_user_count(self) -> int:
        """Get total number of users"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) as count FROM users") as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    async def get_all_user_ids(self) -> List[int]:
        """Get all user IDs for broadcasting"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT user_id FROM users") as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Error getting all user IDs: {e}")
            return []
    
    async def get_message_count(self) -> int:
        """Get total number of messages"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) as count FROM conversations") as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0
