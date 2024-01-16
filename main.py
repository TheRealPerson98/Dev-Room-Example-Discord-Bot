import os
from dotenv import load_dotenv
from bot import DiscordBot
from utils.config import load_config
from utils.logger import setup_logger


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Load configuration and logger
    config = load_config()
    logger = setup_logger()

    # Initialize and run the bot
    bot = DiscordBot(config=config, logger=logger)
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()