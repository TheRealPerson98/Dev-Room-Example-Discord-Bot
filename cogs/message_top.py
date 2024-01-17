import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

class LeaderboardView(discord.ui.View):
    def __init__(self, cog, guild_id, page=0):
        super().__init__()
        self.cog = cog  # Pass the cog instance instead of bot
        self.guild_id = guild_id
        self.page = page

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.guild_id == self.guild_id

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            embed = await self.cog.get_leaderboard_page(self.guild_id, self.page)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        embed = await self.cog.get_leaderboard_page(self.guild_id, self.page)

        # Directly using interaction.response to edit the message
        await interaction.response.edit_message(embed=embed, view=self)




        
        
class LeaderboardCog(commands.Cog, name="leaderboard"):
    def __init__(self, bot):
        self.bot = bot
        
        
    message_group = discord.app_commands.Group(
            name="message", 
            description="Message counter configurations for your server."
        )

    @message_group.command(name="leaderboard", description="Show top message senders in the server.")
    async def show_leaderboard(self, interaction: discord.Interaction):
        embed = await self.get_leaderboard_page(interaction.guild_id, 0)
        view = LeaderboardView(self, interaction.guild_id)  # Pass self here
        await interaction.response.send_message(embed=embed, view=view)


    @message_group.command(name="remove", description="Remove a user from the leaderboard.")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def remove_leaderboard(self, interaction: discord.Interaction, user: discord.Member):
        # Set the user's message count to zero
        await self.update_user_message_count(interaction.guild_id, user.id, 0, set_count=True)
        embed = discord.Embed(description=f"Removed {user.mention} from the leaderboard.", color=discord.Color.green())
        self.add_footer_to_embed(embed)
        await interaction.response.send_message(embed=embed)

    @message_group.command(name="set", description="Set a specific message count for a user in the leaderboard.")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def set_leaderboard(self, interaction: discord.Interaction, user: discord.Member, count: int):
        # Logic to set message count for a user
        await self.update_user_message_count(interaction.guild_id, user.id, count, set_count=True)
        embed = discord.Embed(description=f"Set message count for {user.mention} to {count}.", color=discord.Color.green())
        self.add_footer_to_embed(embed)
        await interaction.response.send_message(embed=embed)

    @message_group.command(name="give", description="Give a specific amount of messages to a user in the leaderboard.")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def give_leaderboard(self, interaction: discord.Interaction, user: discord.Member, count: int):
        # Logic to increment message count for a user
        await self.update_user_message_count(interaction.guild_id, user.id, count, set_count=False)
        embed = discord.Embed(description=f"Added {count} messages to {user.mention}'s count.", color=discord.Color.green())
        self.add_footer_to_embed(embed)
        await interaction.response.send_message(embed=embed)

    async def update_user_message_count(self, guild_id, user_id, count, set_count=False):
        db = self.bot.db.connection
        db_type = self.bot.db.db_type
        if db_type in ["sqlite", "mysql"]:
            if set_count:
                query = '''REPLACE INTO user_messages (guild_id, user_id, message_count) VALUES (?, ?, ?)'''
            else:
                if db_type == "sqlite":
                    # SQLite compatible UPSERT
                    query = '''INSERT INTO user_messages (guild_id, user_id, message_count) VALUES (?, ?, ?)
                            ON CONFLICT(guild_id, user_id) DO UPDATE SET message_count = message_count + excluded.message_count'''
                elif db_type == "mysql":
                    # MySQL compatible UPSERT
                    query = '''INSERT INTO user_messages (guild_id, user_id, message_count) VALUES (?, ?, ?)
                            ON DUPLICATE KEY UPDATE message_count = message_count + VALUES(message_count)'''
            
            await db.execute(query, (guild_id, user_id, count))
            await db.commit()
        elif db_type == "mongodb":
            collection = db['user_messages']
            if set_count:
                await collection.update_one({'guild_id': guild_id, 'user_id': user_id}, {'$set': {'message_count': count}}, upsert=True)
            else:
                await collection.update_one({'guild_id': guild_id, 'user_id': user_id}, {'$inc': {'message_count': count}}, upsert=True)


    
    def add_footer_to_embed(self, embed):
        footer_icon_url = self.bot.config['footer']['icon_url']
        footer_text = self.bot.config['footer']['text']
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)
    
    async def get_leaderboard_page(self, guild_id, page):
        db = self.bot.db.connection
        db_type = self.bot.db.db_type
        embed = discord.Embed(title="Message Leaderboard", color=discord.Color.blue())
        footer_icon_url = self.bot.config['footer']['icon_url']
        footer_text = self.bot.config['footer']['text']
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)

        if db_type in ["sqlite", "mysql"]:
            query = '''SELECT user_id, message_count FROM user_messages WHERE guild_id = ? ORDER BY message_count DESC LIMIT ?, 10'''
            cursor = await db.execute(query, (guild_id, page * 10))
            rows = await cursor.fetchall()
            await cursor.close()
        elif db_type == "mongodb":
            collection = db['user_messages']
            rows = await collection.find({'guild_id': guild_id}).sort('message_count', -1).skip(page * 10).limit(10).to_list(length=10)

        for idx, row in enumerate(rows, start=page * 10 + 1):
            user = self.bot.get_user(row[0])
            username = user.mention if user else f"ID:{row[0]}"
            embed.add_field(name=f"#{idx}", value=f"{username} - {row[1]} Messages", inline=False)

        return embed

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
