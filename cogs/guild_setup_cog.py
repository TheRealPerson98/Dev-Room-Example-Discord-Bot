import discord
from discord.ext import commands

class GuildSetupCog(commands.Cog, name="guild_setup"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.populate_guilds()

    async def populate_guilds(self):
        for guild in self.bot.guilds:
            await self.add_guild_to_db(guild.id)

    async def add_guild_to_db(self, guild_id):
        db = self.bot.db.connection
        db_type = self.bot.db.db_type

        if db_type == "sqlite":
            await db.execute('''INSERT OR IGNORE INTO welcome_messages (guild_id) VALUES (?)''', (guild_id,))
            await db.commit()

        elif db_type == "mysql":
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('''INSERT IGNORE INTO welcome_messages (guild_id) VALUES (%s)''', (guild_id,))
                    await conn.commit()

        elif db_type == "mongodb":
            collection = db['welcome_messages']
            await collection.update_one(
                {'guild_id': guild_id},
                {'$setOnInsert': {'guild_id': guild_id}},
                upsert=True
            )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.add_guild_to_db(guild.id)

async def setup(bot):
    await bot.add_cog(GuildSetupCog(bot))
