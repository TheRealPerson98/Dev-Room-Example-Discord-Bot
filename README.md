# Example Discord Bot

This Discord bot is designed to provide various functionalities including weather updates and automated messaging. Follow the instructions below to set it up.

## Setup

1. **Clone or Download the Repository**
   - Clone this repository or download and unzip it into a folder on your local machine.

2. **Install Dependencies**
   - Open a terminal in the bot's folder.
   - Run the following command to install required dependencies:
     ```
     pip install -r requirements.txt
     ```

## Discord Token Setup

To run the bot, you will need a Discord Bot Token. Follow these steps to get one:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application and then create a bot within that application.
3. Copy the bot token provided.

## Bot Intents

Before installation, ensure the bot has the following intents enabled:
- PRESENCE INTENT
- SERVER MEMBERS INTENT
- MESSAGE CONTENT INTENT

These can be enabled under the Bot section in your Discord Developer Portal at `https://discord.com/developers/applications/[Your Bot CLIENT ID]/bot`.

## Weather API Key

If you want to use the weather API command:

1. Get a free API key from [WeatherAPI](https://www.weatherapi.com/).
2. Add the API key to your environment variables.

## Configuration

1. Rename `example.env` to `.env`.
2. Add your Discord token and Weather API key to the `.env` file:
```
TOKEN=your_discord_token_here
WEATHER_API_KEY=your_weatherapi_key_here
```

## Starting the Bot

- On Windows:
- Open a command prompt in the bot's folder.
- Run the bot using one of the following commands:
 ```
 python main.py
 ```
 or
 ```
 python3 main.py
 ```
 or
 ```
 py main.py
 ```
- Alternatively, you can run `run.bat` if available.

After you start it the first thing u need to is is run
(prefix from config) sync (guild or global)

## Editing Configurations

- Configuration files are located in the `config` folder.
- Edit the files as needed to customize the bot's behavior.

## Features

- **Database Support**: Allows the use of MySQL, SQLite, and MongoDB for databases.
- **Public Accessibility**: The bot can be set to public.
- **Commands**:
```
/setup setup_weather channel: city: time:
/setup welcome_message
/setup welcome_channel channel:
/setup welcome_enabled enabled:
/setup welcome_embed embed:
/message leaderboard
/message give user: count:
/message remove user: count:
/message set user: count:
/rps play choice:
/uptime check
```
- **Features**:
```
Auto Welcome on join
```


For further information or assistance, feel free to open an issue on this repository.
