from geopy.geocoders import Nominatim
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import logging

# Nominatim requires a descriptive UA with contact info
geolocator = Nominatim(user_agent="DE_Project/1.0")

PRIMARY_CITY = "Boston, MA"  # can be changed as needed
FALLBACK_CITY = "New York, NY"   # always hard-coded fallback

def get_lat_long(city: str) -> tuple[float, float, str]:
    """
    Try the primary city; if it fails, fall back to the hard-coded fallback city.
    Returns (latitude, longitude, used_city). Raises ValueError if both fail.
    """
    try:
        location = geolocator.geocode(city, exactly_one=True, timeout=10)
    except Exception as e:
        logging.error("Error geocoding '%s': %s", city, e)
        location = None

    if location:
        return location.latitude, location.longitude, city

    logging.warning("No result for '%s'. Falling back to '%s'.", city, FALLBACK_CITY)
    try:
        fb_loc = geolocator.geocode(FALLBACK_CITY, exactly_one=True, timeout=10)
    except Exception as e:
        logging.error("Error geocoding fallback '%s': %s", FALLBACK_CITY, e)
        fb_loc = None

    if fb_loc:
        return fb_loc.latitude, fb_loc.longitude, FALLBACK_CITY

    logging.critical("Failed to geocode both '%s' and fallback '%s'.", city, FALLBACK_CITY)
    raise ValueError(f"Could not geocode '{city}' or fallback '{FALLBACK_CITY}'")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

latitude, longitude, used_city = get_lat_long(PRIMARY_CITY)

end_date = date.today() - timedelta(days=1)          # yesterday
start_date = end_date - relativedelta(years=5)       # five years ago

years = list(range(start_date.year, end_date.year + 1))

logging.info("City used: %s | Lat: %.6f | Lon: %.6f | Start: %s | End: %s",
             used_city, latitude, longitude, start_date, end_date)
print(years)