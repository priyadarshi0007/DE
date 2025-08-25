import requests
import pandas as pd
from city_time_interval import years,iso_region,cc
import logging

logging.basicConfig(
    filename="public_holidays.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def fetch_public_holidays(years, country=cc):
    # Normalize inputs
    country = (country or "").upper()
    years = years if isinstance(years, (list, range)) else [years]
    years = [int(y) for y in years]
    if not years:
        raise ValueError("No years provided")
    logging.error(f"Fetching public holidays for country: {country} and years: {years}")
    all_holidays = {}

    for year in years:
        url = f'https://date.nager.at/api/v3/publicholidays/{year}/{country}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            holidays = response.json()
            if not isinstance(holidays, list):
                logging.warning(f"Unexpected payload for {year}: {type(holidays)}")
                continue
            all_holidays[year] = holidays
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve data for {year}: {e}")

    logging.info(f"Collected years: {sorted(all_holidays.keys())}")
    records = []
    for year, holidays in all_holidays.items():
        for holiday in holidays:
            # Add year column + flatten lists (like 'types')
            if holiday["counties"] is None or iso_region in (holiday["counties"] or []):
                flat = holiday.copy()
                flat["year"] = year
                flat["types"] = ", ".join(flat["types"]) if flat["types"] else None
                flat["counties"] = ", ".join(flat["counties"]) if flat["counties"] else None
                records.append(flat)

    df = pd.DataFrame(records)

    drop_cols = ["launchYear", "types", "counties", "global","fixed","countryCode"]
    df_cleaned = df.drop(columns=drop_cols)
    return df_cleaned   

logging.info(f"Country: {cc} | ISO Region: {iso_region} | Years fetched: {years}")
# df_holidays = fetch_public_holidays(years, country=cc)
# print(df_holidays)
