import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
from pytz import all_timezones

class WelcomeMessageModal(Modal):
    def __init__(self, bot, guild_id):
        super().__init__(title="Welcome Message Setup")
        self.bot = bot
        self.guild_id = guild_id
        self.add_item(TextInput(label="Welcome Message", style=discord.TextStyle.paragraph, placeholder="Enter your welcome message here"))

    async def on_submit(self, interaction: discord.Interaction):
        message = self.children[0].value
        await self.update_welcome_message(self.guild_id, message)
        embed = discord.Embed(description="Welcome message updated successfully!", color=discord.Color.green())
        footer_icon_url = self.bot.config['footer']['icon_url']
        footer_text = self.bot.config['footer']['text']
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def update_welcome_message(self, guild_id, message):
        db_type = self.bot.db.db_type
        db = self.bot.db.connection

        if db_type == "sqlite":
            query = f'''UPDATE welcome_messages SET message = ? WHERE guild_id = ?'''
            await db.execute(query, (message, guild_id))
            await db.commit()
        elif db_type == "mysql":
            query = f'''UPDATE welcome_messages SET message = %s WHERE guild_id = %s'''
            await db.execute(query, (message, guild_id))
            await db.commit()
        elif db_type == "mongodb":
            collection = db['welcome_messages']
            await collection.update_one({'guild_id': guild_id}, {'$set': {'message': message}}, upsert=True)

class SetupCog(commands.Cog, name="setup"):
    def __init__(self, bot):
        self.bot = bot

    setup = discord.app_commands.Group(name="setup", description="Setup configurations for your server.")

    @setup.command(name="welcome_enabled", description="Enable or disable the welcome message for your server.")
    async def setup_welcome_enabled(self, interaction: discord.Interaction, enabled: bool):
        await self.update_welcome_setting(interaction.guild_id, 'is_enabled', enabled)
        embed = discord.Embed(description=f"Welcome message enabled: {enabled}", color=discord.Color.green())
        self.add_footer_to_embed(embed)
        await interaction.response.send_message(embed=embed)

    @setup.command(name="welcome_embed", description="Enable or disable the welcome message as embed for your server.")
    async def setup_welcome_embed(self, interaction: discord.Interaction, embed: bool):
        await self.update_welcome_setting(interaction.guild_id, 'is_embed', embed)
        embed = discord.Embed(description=f"Welcome message as embed: {embed}", color=discord.Color.green())
        self.add_footer_to_embed(embed)
        await interaction.response.send_message(embed=embed)

    @setup.command(name="welcome_channel", description="Set the welcome channel for your server.")
    async def setup_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.update_welcome_setting(interaction.guild_id, 'welcome_channel_id', channel.id)
        embed = discord.Embed(description=f"Welcome channel set to: {channel.mention}", color=discord.Color.green())
        self.add_footer_to_embed(embed)
        await interaction.response.send_message(embed=embed)
        
    @setup.command(name="welcome_message", description="Set the welcome message for your server.")
    async def setup_welcome_message(self, interaction: discord.Interaction):
        modal = WelcomeMessageModal(self.bot, interaction.guild_id)
        await interaction.response.send_modal(modal)
        
    @setup.command(name="setup_weather", description="Set up weather updates: City, Time (HH:MM), Timezone (e.g., 'New York 15:00 UTC')")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def set_weather_send_time(self, interaction: discord.Interaction, channel: discord.TextChannel, city: str, time: str):
        if self.is_valid_time_format(time):
            time_parts = time.split(" ")
            send_time = time_parts[0]
            timezone = time_parts[1]
            await self.update_weather_send_time(interaction.guild_id, channel.id, city, send_time, timezone)
            embed = discord.Embed(description=f"Weather updates for {city} set to: {time} in {channel.mention}", color=discord.Color.green())
            self.add_footer_to_embed(embed)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description="Invalid time format. Please use the format 'City HH:MM Timezone' (e.g., 'New York 15:00 UTC').", color=discord.Color.red())
            self.add_footer_to_embed(embed)
            await interaction.response.send_message(embed=embed)

    async def update_weather_send_time(self, guild_id, channel_id, city, send_time, timezone):
        db_type = self.bot.db.db_type
        db = self.bot.db.connection

        if db_type == "sqlite":
            query = '''REPLACE INTO weather_sender (guild_id, channel_id, city, send_time, timezone) VALUES (?, ?, ?, ?, ?)'''
            await db.execute(query, (guild_id, channel_id, city, send_time, timezone))
            await db.commit()
        elif db_type == "mysql":
            query = '''REPLACE INTO weather_sender (guild_id, channel_id, city, send_time, timezone) VALUES (%s, %s, %s, %s, %s)'''
            await db.execute(query, (guild_id, channel_id, city, send_time, timezone))
            await db.commit()
        elif db_type == "mongodb":
            collection = db['weather_sender']
            await collection.update_one({'guild_id': guild_id}, {'$set': {'channel_id': channel_id, 'city': city, 'send_time': send_time, 'timezone': timezone}}, upsert=True)
        
    def is_valid_time_format(self, time_str):
            # Example format: "15:00 UTC"
        parts = time_str.split()
        if len(parts) == 2 and parts[1] in all_timezones:
            time_part = parts[0].split(':')
            if len(time_part) == 2 and time_part[0].isdigit() and time_part[1].isdigit():
                hour = int(time_part[0])
                minute = int(time_part[1])
                return 0 <= hour < 24 and 0 <= minute < 60
            return False


    async def update_welcome_setting(self, guild_id, setting, value):
        db_type = self.bot.db.db_type
        db = self.bot.db.connection

        if db_type == "sqlite":
            query = f'''UPDATE welcome_messages SET {setting} = ? WHERE guild_id = ?'''
            await db.execute(query, (value, guild_id))
            await db.commit()
        elif db_type == "mysql":
            query = f'''UPDATE welcome_messages SET {setting} = %s WHERE guild_id = %s'''
            await db.execute(query, (value, guild_id))
            await db.commit()
        elif db_type == "mongodb":
            collection = db['welcome_messages']
            await collection.update_one({'guild_id': guild_id}, {'$set': {setting: value}}, upsert=True)
            
    def add_footer_to_embed(self, embed):
        footer_icon_url = self.bot.config['footer']['icon_url']
        footer_text = self.bot.config['footer']['text']
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)
        

async def setup(bot):
    await bot.add_cog(SetupCog(bot))
