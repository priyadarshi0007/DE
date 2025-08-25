from publicholiday import fetch_public_holidays
from weather_data import fetch_weather_data
from ds_utils import save_df_to_sqlite, run_query
from city_time_interval import latitude, longitude, start_date, end_date, used_city, iso_region, cc, years
import logging
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Starting data extraction and storage process")



# Fetch public holidays
public_holidays = fetch_public_holidays(years, country=cc)
if not public_holidays.empty:
    save_df_to_sqlite(public_holidays, "deproject.db", "public_holidays")
else:
    logging.warning("No public holidays data to save")
    
# Fetch weather data
weather_data = fetch_weather_data(latitude, longitude, start_date, end_date)
if not weather_data.empty:
    save_df_to_sqlite(weather_data, "deproject.db", "weather_data")
else:
    logging.warning("No weather data to save")