import discord
from discord.ext import commands
import datetime
import discord.app_commands as app_commands
from utils.config import load_config

class UptimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    uptime_group = app_commands.Group(name="uptime", description="Check how long the bot has been running.")

    @uptime_group.command(name="check", description="Shows the current uptime of the bot.")
    async def check(self, interaction: discord.Interaction):
        current_time = datetime.datetime.utcnow()
        uptime_duration = current_time - self.start_time

        # Create an embed for the uptime result
        embed = discord.Embed(title="Uptime", description=f"The bot has been up for {uptime_duration}", color=discord.Color.green())

        # Load footer settings from config
        config = load_config()
        footer_icon_url = config['footer']['icon_url']
        footer_text = config['footer']['text']
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UptimeCog(bot))
