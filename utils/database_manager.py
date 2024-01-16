import os
import aiosqlite
import aiomysql
import motor.motor_asyncio
from utils.config import load_config

class Database:
    def __init__(self):
        self.config = load_config()
        self.db_type = self.config['database']['type']
        self.connection = None

    async def init_db(self):
        if self.db_type == "sqlite":
            os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'database.db')
            db = await aiosqlite.connect(db_path)
            await db.execute('''CREATE TABLE IF NOT EXISTS welcome_messages (
                                guild_id INTEGER PRIMARY KEY,
                                welcome_channel_id INTEGER,
                                is_enabled BOOLEAN DEFAULT TRUE,
                                is_embed BOOLEAN DEFAULT FALSE,
                                message TEXT
                              )''')
            await db.commit()
            self.connection = db

        elif self.db_type == "mysql":
            mysql_config = self.config['database']['mysql']
            pool = await aiomysql.create_pool(
                host=mysql_config['host'],
                port=int(mysql_config['port']),
                user=mysql_config['user'],
                password=mysql_config['password'],
                db=mysql_config['database'],
                loop=self.config['loop']
            )
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('''CREATE TABLE IF NOT EXISTS welcome_messages (
                                            guild_id BIGINT PRIMARY KEY,
                                            welcome_channel_id BIGINT,
                                            is_enabled BOOLEAN DEFAULT TRUE,
                                            is_embed BOOLEAN DEFAULT FALSE,
                                            message TEXT
                                          )''')
                    await conn.commit()
            self.connection = pool

        elif self.db_type == "mongodb":
            mongo_config = self.config['database']['mongodb']
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_config['connection_string'])
            db = client.get_default_database()
            await db.welcome_messages.create_index("guild_id", unique=True)
            self.connection = db

        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    async def close(self):
        if self.db_type in ["sqlite", "mysql"]:
            await self.connection.close()

    # Add additional methods for database operations as needed
