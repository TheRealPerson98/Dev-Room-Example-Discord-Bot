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
            await db.execute('''CREATE TABLE IF NOT EXISTS user_messages (
                                guild_id INTEGER,
                                user_id INTEGER,
                                message_count TEXT,
                                PRIMARY KEY (guild_id, user_id)
                              )''')
            await db.commit()
           # New table for weather sender
            await db.execute('''CREATE TABLE IF NOT EXISTS weather_sender (
                                    guild_id INTEGER,
                                    channel_id INTEGER,
                                    city TEXT,
                                    send_time TEXT,
                                    timezone TEXT,
                                    PRIMARY KEY (guild_id, channel_id)
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
                    await cursor.execute('''CREATE TABLE IF NOT EXISTS user_messages (
                                            guild_id BIGINT,
                                            user_id BIGINT,
                                            message_count TEXT,
                                            PRIMARY KEY (guild_id, user_id)
                                          )''')
                    await conn.commit()
                    await cursor.execute('''CREATE TABLE IF NOT EXISTS weather_sender (
                                                guild_id BIGINT,
                                                channel_id BIGINT,
                                                city TEXT,
                                                send_time TEXT,
                                                timezone TEXT,
                                                PRIMARY KEY (guild_id, channel_id)
                                            )''')
                    await conn.commit()


            self.connection = pool


        elif self.db_type == "mongodb":
            mongo_config = self.config['database']['mongodb']
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_config['connection_string'])
            db = client.get_default_database()

            # Creating index for 'welcome_messages' collection
            await db.welcome_messages.create_index("guild_id", unique=True)

            # Creating index for 'user_messages' collection
            user_messages_collection = db['user_messages']
            await user_messages_collection.create_index([("guild_id", 1), ("user_id", 1)], unique=True)

            # Creating index for 'weather_sender' collection
            weather_sender_collection = db['weather_sender']
            await weather_sender_collection.create_index([("guild_id", 1), ("channel_id", 1)], unique=True)

            self.connection = db


        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    async def close(self):
        if self.db_type in ["sqlite", "mysql"]:
            await self.connection.close()

    # Add additional methods for database operations as needed
