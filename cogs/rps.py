import discord
from discord.ext import commands
import random
import discord.app_commands as app_commands
import utils.config as config
from utils.config import load_config

class RPSGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    rps_group = app_commands.Group(name="rps", description="Play Rock-Paper-Scissors with the bot.")

    @rps_group.command(name="play", description="Choose rock, paper, or scissors.")
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="Rock", value="rock"),
            app_commands.Choice(name="Paper", value="paper"),
            app_commands.Choice(name="Scissors", value="scissors"),
        ]
    )
    async def play(self, interaction: discord.Interaction, choice: str):
        bot_choice = random.choice(["rock", "paper", "scissors"])
        result = self.determine_winner(choice, bot_choice)

        # Create an embed for the game result
        embed = discord.Embed(title="Rock-Paper-Scissors", description=f"Your choice: {choice.capitalize()}\nBot's choice: {bot_choice.capitalize()}", color=discord.Color.blue())
        embed.add_field(name="Result", value=result)

        # Add appropriate emoji
        emoji_map = {"rock": "✊", "paper": "✋", "scissors": "✌️"}
        embed.add_field(name="Your Choice", value=emoji_map[choice], inline=True)
        embed.add_field(name="Bot's Choice", value=emoji_map[bot_choice], inline=True)
        
        footer_icon_url = self.bot.config['footer']['icon_url']
        footer_text = self.bot.config['footer']['text']
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)
        
        await interaction.response.send_message(embed=embed)

    def determine_winner(self, user_choice, bot_choice):
        if user_choice == bot_choice:
            return "It's a tie!"
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "paper" and bot_choice == "rock") or \
             (user_choice == "scissors" and bot_choice == "paper"):
            return "You win! 🎉"
        else:
            return "You lose! 😢"

    def get_image_for_choice(self, choice):
        config = load_config()
        image_url = config["rps_images"][choice]
        print(f"Image URL for {choice}: {image_url}")  # Log to check the URL
        return image_url

async def setup(bot):
    await bot.add_cog(RPSGame(bot))
