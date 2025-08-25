```mermaid
flowchart TD
    A[User Input: City Name] --> B[city_time_interval.py]
    B -->|Geocode City| C{Success?}
    C -- Yes --> D[Get latitude, longitude, ISO region, country code, years, start_date, end_date]
    C -- No --> E[Fallback City]
    E -->|Geocode Fallback| D

    D --> F[main.py]
    F -->|Validate Inputs| G{Valid?}
    G -- No --> H[Exit with Error]
    G -- Yes --> I[Fetch Public Holidays]
    I -->|publicholiday.py| J[fetch_public_holidays()]
    J --> K[public holidays DataFrame]
    K -->|save_df_to_sqlite| L[SQLite DB: public_holidays table]

    F -->|Fetch Weather Data| M[weather_data.py]
    M --> N[fetch_weather_data()]
    N --> O[weather data DataFrame]
    O -->|save_df_to_sqlite| P[SQLite DB: weather_data table]

    L & P --> Q[_ensure_indexes()]
    Q --> R[Done]
```
