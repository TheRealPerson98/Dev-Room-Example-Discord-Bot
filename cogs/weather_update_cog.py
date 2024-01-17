import discord
from discord.ext import commands, tasks
from utils.weather_helper import get_weather
import datetime
from pytz import timezone
import pytz

class WeatherUpdateCog(commands.Cog, name="weather_update"):
    def __init__(self, bot):
        self.bot = bot
        self.weather_update.start()  # Start the background task

    @tasks.loop(minutes=1)
    async def weather_update(self):
        utc_now = datetime.datetime.now(pytz.utc)

        db = self.bot.db.connection
        db_type = self.bot.db.db_type

        if db_type == "sqlite" or db_type == "mysql":
            cursor = await db.execute("SELECT * FROM weather_sender")
            rows = await cursor.fetchall()
            await cursor.close()
        elif db_type == "mongodb":
            collection = db['weather_sender']
            rows = await collection.find({}).to_list(length=1000)

        for row in rows:
            guild_id, channel_id, _, send_time, timezone_str = row
            try:
                tz = pytz.timezone(timezone_str)
            except pytz.UnknownTimeZoneError:
                continue

            send_time_local = datetime.datetime.strptime(send_time, "%H:%M")
            send_time_local = tz.localize(send_time_local)
            send_time_utc = send_time_local.astimezone(pytz.utc)

            if send_time_utc.time() <= utc_now.time() < (send_time_utc + datetime.timedelta(minutes=1)).time():
                await self.send_weather_update(guild_id, channel_id)





    async def send_weather_update(self, guild_id, channel_id):
        channel = self.bot.get_channel(channel_id)
        print(f"Channel: {channel}")
        if channel:
            city = await self.get_city_for_guild(guild_id)  # Use 'await' here
            if city:
                weather_data = get_weather(city)
                if weather_data:
                    try:
                        embed = self.create_weather_embed(city, weather_data['current'], is_forecast=False)
                        await channel.send(embed=embed)
                    except Exception as e:
                        print(e)



    def create_weather_embed(self, city, weather_data, is_forecast=False, date=None):
        title = f"Weather in {city.title()}"
        if is_forecast and date:
            title = f"Weather Forecast for {city.title()} on {date}"
        
        embed = discord.Embed(title=title, color=discord.Color.blue())

        if is_forecast:
            # For forecast data
            temp = f"{weather_data['avgtemp_c']}°C"
            condition = weather_data['condition']['text']
        else:
            # For current weather data
            temp = f"{weather_data['temp_c']}°C"
            condition = weather_data['condition']['text']

        embed.add_field(name="Temperature", value=temp, inline=False)
        embed.add_field(name="Condition", value=condition, inline=False)

        footer_icon_url = self.bot.config['footer']['icon_url']
        footer_text = self.bot.config['footer']['text']
        embed.set_footer(icon_url=footer_icon_url, text=footer_text)
        return embed
    
    @weather_update.before_loop
    async def before_weather_update(self):
        await self.bot.wait_until_ready()

    async def get_city_for_guild(self, guild_id):
        db = self.bot.db.connection
        db_type = self.bot.db.db_type

        if db_type == "sqlite" or db_type == "mysql":
            query = '''SELECT city FROM weather_sender WHERE guild_id = ?'''
            cursor = await db.execute(query, (guild_id,))
            row = await cursor.fetchone()
            await cursor.close()
            if row:
                return row[0]  # Return the city
            else:
                return None  # Return None if city is not set

        elif db_type == "mongodb":
            collection = db['weather_sender']
            document = await collection.find_one({'guild_id': guild_id})
            if document:
                return document.get('city')  # Return the city
            else:
                return None  # Return None if city is not set



async def setup(bot):
    await bot.add_cog(WeatherUpdateCog(bot))