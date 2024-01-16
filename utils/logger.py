import logging
from logging.handlers import RotatingFileHandler
import os

class LoggingFormatter(logging.Formatter):
    """ Custom logging formatter with color and style. """

    # Terminal color codes
    COLORS = {
        logging.DEBUG: "\x1b[32;1m",  # Green, bold
        logging.INFO: "\x1b[34;1m",   # Blue, bold
        logging.WARNING: "\x1b[33;1m", # Yellow, bold
        logging.ERROR: "\x1b[31;1m",   # Red
        logging.CRITICAL: "\x1b[31;1m\x1b[1m", # Red, bold
    }
    RESET = "\x1b[0m"

    def format(self, record):
        levelcolor = self.COLORS.get(record.levelno)
        message = super().format(record)
        return f"{levelcolor}{message}{self.RESET}"

def setup_logger(name="discord_bot", level=logging.INFO):
    """ Sets up a logger with console and file handlers. """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ensure the 'data' folder exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Log file path in the 'data' directory
    log_file_path = os.path.join(data_dir, 'discord_bot.log')

    # Console handler with custom formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LoggingFormatter())
    logger.addHandler(console_handler)

    # File handler with rotating logs
    file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(file_handler)

    return logger
