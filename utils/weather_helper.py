import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_weather(city, forecast_days=1):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise Exception("Weather API key not found in .env file")

    base_url = f"http://api.weatherapi.com/v1/forecast.json"
    query = f"{city}"
    params = {
        "key": api_key,
        "q": query,
        "days": forecast_days,
        "aqi": "no",
        "alerts": "no"
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

