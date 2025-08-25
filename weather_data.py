import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from city_time_interval import latitude, longitude, start_date, end_date
import logging

logging.basicConfig(level=logging.INFO, filename='weather_data.log', format="%(asctime)s [%(levelname)s] %(message)s")

def fetch_weather_data(latitude, longitude, start_date, end_date):
    try:
        logging.info("Fetching weather data for lat=%.4f, lon=%.4f, start=%s, end=%s", latitude, longitude, start_date, end_date)
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "America/New_York",
        }
        logging.debug("Calling Open-Meteo API: %s with params %s", url, params)
        responses = openmeteo.weather_api(url, params=params)
        logging.info("Received response with %d datasets", len(responses))
        daily = responses[0].Daily()
        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ),
            "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
            "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
            "precipitation_sum": daily.Variables(2).ValuesAsNumpy()
        }
        daily_dataframe = pd.DataFrame(data=daily_data)
        daily_dataframe["date"] = daily_dataframe["date"].dt.date
        logging.info("Weather DataFrame created with %d rows and %d columns", daily_dataframe.shape[0], daily_dataframe.shape[1])
        daily_dataframe = daily_dataframe.dropna(subset=["temperature_2m_max", "temperature_2m_min", "precipitation_sum"])
        logging.info("After dropping NA values, %d rows remain", daily_dataframe.shape[0])
        return daily_dataframe
    except Exception as e:
        logging.error("Error fetching weather data: %s", e, exc_info=True)
        return pd.DataFrame()
    
logging.info("Starting weather data fetch process")
# df_weather = fetch_weather_data(latitude, longitude, start_date, end_date)
# print(df_weather)
