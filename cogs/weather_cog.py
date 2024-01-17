import discord
from discord.ext import commands
from utils.weather_helper import get_weather  # Adjust the import path if necessary

class WeatherCog(commands.Cog, name="weather"):
    def __init__(self, bot):
        self.bot = bot

    weather_group = discord.app_commands.Group(name="weather", description="Weather information commands.")

    @weather_group.command(name="day", description="Get current weather information for a city and state.")
    async def weather_day(self, interaction: discord.Interaction, city: str):
        current_weather = get_weather(city, forecast_days=1)
        if current_weather and 'current' in current_weather:
            embed = self.create_weather_embed(city, current_weather['current'], is_forecast=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Unable to retrieve current weather information. Please check city and state names.", ephemeral=True)


    @weather_group.command(name="forecast", description="Get a 7-day weather forecast for a city and state.")
    async def weather_forecast(self, interaction: discord.Interaction, city: str):
        forecast_weather = get_weather(city, forecast_days=7)
        if forecast_weather and 'forecast' in forecast_weather:
            first_message = True
            for day in forecast_weather['forecast']['forecastday']:
                embed = self.create_weather_embed(city, day['day'], is_forecast=True, date=day['date'])
                if first_message:
                    await interaction.response.send_message(embed=embed)
                    first_message = False
                else:
                    await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message("Unable to retrieve 7-day forecast. Please check city and state names.", ephemeral=True)



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


async def setup(bot):
    await bot.add_cog(WeatherCog(bot))
