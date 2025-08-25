from publicholiday import fetch_public_holidays
from weather_data import fetch_weather_data
from ds_utils import save_df_to_sqlite
from city_time_interval import latitude, longitude, start_date, end_date, cc, years
import logging
import sqlite3
import sys
from typing import Iterable

from publicholiday import fetch_public_holidays
from weather_data import fetch_weather_data
from ds_utils import save_df_to_sqlite
from city_time_interval import latitude, longitude, start_date, end_date, cc, years

# ---------- logging ----------
import os
log_file = os.path.join(os.path.dirname(__file__), "pipeline.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename=log_file,
    filemode="a"
)
log = logging.getLogger(__name__)


# ---------- validators & utils ----------
def _validate_inputs(latitude: float, longitude: float, start_date, end_date, years: Iterable[int], cc: str):
  errs = []
  if latitude is None or not (-90 <= float(latitude) <= 90):
    errs.append(f"latitude out of range: {latitude}")
  if longitude is None or not (-180 <= float(longitude) <= 180):
    errs.append(f"longitude out of range: {longitude}")
  if start_date is None or end_date is None:
    errs.append("start_date/end_date required")
  elif start_date > end_date:
    errs.append(f"start_date {start_date} is after end_date {end_date}")
  if not years:
    errs.append("years list is empty")
  else:
    try:
      _ = [int(y) for y in years]
    except Exception:
      errs.append(f"years must be ints; got {years}")
  if not cc or len(str(cc)) != 2:
    errs.append(f"country code must be 2 letters (e.g., 'US'); got {cc}")
  if errs:
    raise ValueError("; ".join(errs))

def _ensure_indexes(db_path: str):
  """Create helpful indexes in SQLite after loads."""
  try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS ix_public_holidays_date ON public_holidays(date);")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_weather_date ON weather_data(date);")
    conn.commit()
  except Exception as e:
    log.warning("Could not create indexes on %s: %s", db_path, e)
  finally:
    try:
      conn.close()
    except Exception:
      pass


# ---------- main ----------
def main():
  log.info("Starting data extraction and storage process")
  # Validate config coming from city_time_interval
  try:
    _validate_inputs(latitude, longitude, start_date, end_date, years, cc)
  except Exception as e:
    log.critical("Configuration validation failed: %s", e)
    sys.exit(1)

  db_path = "deproject.db"
  log.info("Params: city coords lat=%.6f lon=%.6f | window=%s→%s | years=%s | country=%s",
           float(latitude), float(longitude), start_date, end_date, list(years), str(cc).upper())

  # --- Holidays ---
  try:
    log.info("Fetching public holidays for %s over years=%s", str(cc).upper(), list(years))
    public_holidays = fetch_public_holidays(years, country=str(cc).upper())
    if public_holidays is not None and not public_holidays.empty:
      save_df_to_sqlite(public_holidays, db_path, "public_holidays")
      log.info("Saved %d holiday rows to %s.public_holidays", len(public_holidays), db_path)
    else:
      log.warning("No public holidays data to save")
  except Exception as e:
    log.error("Failed to fetch/save public holidays: %s", e, exc_info=True)

  # --- Weather ---
  try:
    log.info("Fetching weather data lat=%.6f lon=%.6f for %s→%s", float(latitude), float(longitude), start_date, end_date)
    weather_data = fetch_weather_data(latitude, longitude, start_date, end_date)
    if weather_data is not None and not weather_data.empty:
      save_df_to_sqlite(weather_data, db_path, "weather_data")
      log.info("Saved %d weather rows to %s.weather_data", len(weather_data), db_path)
    else:
      log.warning("No weather data to save")
  except Exception as e:
    log.error("Failed to fetch/save weather data: %s", e, exc_info=True)

  # --- Indexes (non-fatal) ---
  _ensure_indexes(db_path)
  log.info("Done.")


if __name__ == "__main__":
  main()