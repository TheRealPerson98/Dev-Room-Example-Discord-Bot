import discord
from discord.ext import commands

class WelcomeCog(commands.Cog, name="welcome"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id
        welcome_settings = await self.get_welcome_settings(guild_id)

        if welcome_settings and welcome_settings[2]:  # Checking if 'is_enabled' is True
            channel = member.guild.get_channel(welcome_settings[1])  # 'welcome_channel_id'
            if channel:
                number_joined = member.guild.member_count
                message = welcome_settings[4]
                message = message.replace("%username%", member.mention)
                message = message.replace("%guildname%", member.guild.name)
                message = message.replace("%numberjoined%", str(number_joined))

                if welcome_settings[3]:  # 'is_embed'
                    embed = discord.Embed(description=message, color=discord.Color.blue())
                    footer_icon_url = self.bot.config['footer']['icon_url']
                    footer_text = self.bot.config['footer']['text']
                    embed.set_footer(icon_url=footer_icon_url, text=footer_text)
                    await channel.send(embed=embed)
                else:
                    await channel.send(message)

    async def get_welcome_settings(self, guild_id):
        db = self.bot.db.connection
        db_type = self.bot.db.db_type

        if db_type == "sqlite" or db_type == "mysql":
            query = '''SELECT * FROM welcome_messages WHERE guild_id = ?'''
            cursor = await db.execute(query, (guild_id,))
            result = await cursor.fetchone()
            await cursor.close()
            return result
        elif db_type == "mongodb":
            collection = db['welcome_messages']
            result = await collection.find_one({'guild_id': guild_id})
            return result

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
