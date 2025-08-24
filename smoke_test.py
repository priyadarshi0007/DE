import requests
from bs4 import BeautifulSoup
import json


def fetch_weather_data(api_key, location, date):
    url = f"https://api.open-meteo.com/v1/forecast?latitude=71.0565&longitude=42.3555&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=EST&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching weather data: {response.status_code}")
    