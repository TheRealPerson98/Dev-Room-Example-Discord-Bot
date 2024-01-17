import discord
from discord.ext import commands
import asyncio
import sqlite3

class MessageCountCog(commands.Cog, name="message_count"):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # Dictionary to keep track of cooldowns for each user

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot messages and check if the message is in a guild
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        guild_id = message.guild.id

        # Check if user is on cooldown
        if self.is_on_cooldown(user_id, guild_id):
            return

        # Update message count in the database
        await self.update_message_count(guild_id, user_id)

        # Set cooldown for the user
        self.set_cooldown(user_id, guild_id, cooldown=2)  # Cooldown in seconds

    def is_on_cooldown(self, user_id, guild_id):
        key = (user_id, guild_id)
        return key in self.cooldowns and self.cooldowns[key] > asyncio.get_event_loop().time()

    def set_cooldown(self, user_id, guild_id, cooldown):
        key = (user_id, guild_id)
        self.cooldowns[key] = asyncio.get_event_loop().time() + cooldown

    async def update_message_count(self, guild_id, user_id):
        db = self.bot.db.connection
        db_type = self.bot.db.db_type

        if db_type == "sqlite":
            try:
                # Try to insert a new record for the user
                insert_query = '''INSERT INTO user_messages (guild_id, user_id, message_count) VALUES (?, ?, 1)'''
                await db.execute(insert_query, (guild_id, user_id))
            except sqlite3.IntegrityError:
                # If the record exists, increment the message count
                update_query = '''UPDATE user_messages SET message_count = message_count + 1 WHERE guild_id = ? AND user_id = ?'''
                await db.execute(update_query, (guild_id, user_id))
            await db.commit()
        elif db_type == "mysql":
            # MySQL uses ON DUPLICATE KEY UPDATE syntax
            query = '''INSERT INTO user_messages (guild_id, user_id, message_count)
                    VALUES (%s, %s, 1)
                    ON DUPLICATE KEY UPDATE message_count = message_count + 1'''
            await db.execute(query, (guild_id, user_id))
            await db.commit()
        elif db_type == "mongodb":
            # MongoDB uses the update_one method with the $inc operator
            collection = db['user_messages']
            await collection.update_one(
                {'guild_id': guild_id, 'user_id': user_id},
                {'$inc': {'message_count': 1}},
                upsert=True
            )


async def setup(bot):
    await bot.add_cog(MessageCountCog(bot))
