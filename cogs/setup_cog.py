import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

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
        await interaction.response.send_message(embed=embed)

    @setup.command(name="welcome_embed", description="Enable or disable the welcome message as embed for your server.")
    async def setup_welcome_embed(self, interaction: discord.Interaction, embed: bool):
        await self.update_welcome_setting(interaction.guild_id, 'is_embed', embed)
        embed = discord.Embed(description=f"Welcome message as embed: {embed}", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @setup.command(name="welcome_channel", description="Set the welcome channel for your server.")
    async def setup_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.update_welcome_setting(interaction.guild_id, 'welcome_channel_id', channel.id)
        embed = discord.Embed(description=f"Welcome channel set to: {channel.mention}", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        
    @setup.command(name="welcome_message", description="Set the welcome message for your server.")
    async def setup_welcome_message(self, interaction: discord.Interaction):
        modal = WelcomeMessageModal(self.bot, interaction.guild_id)
        await interaction.response.send_modal(modal)

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


async def setup(bot):
    await bot.add_cog(SetupCog(bot))
