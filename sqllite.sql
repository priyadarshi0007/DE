-- SQLite
CREATE INDEX IF NOT EXISTS ix_weather_date  ON weather_data(date);
CREATE INDEX IF NOT EXISTS ix_holiday_date  ON public_holidays(date);

DROP VIEW IF EXISTS vw_weather_with_holidays;

CREATE VIEW vw_weather_with_holidays AS
SELECT
    w.date,
    w.temperature_2m_max,
    w.temperature_2m_min,
    w.precipitation_sum,
    /* Flag: 1 if any holiday exists on this date, else 0 */
    CASE 
      WHEN EXISTS (SELECT 1 FROM public_holidays h WHERE h.date = w.date) 
      THEN 1 ELSE 0 
    END AS is_public_holiday,
    /* Optional: list holiday names if there are multiple (SQLite built-in) */
    (
      SELECT group_concat(h.name, ', ')
      FROM public_holidays h
      WHERE h.date = w.date
    ) AS holiday_names
FROM weather_data w;


SELECT * from vw_weather_with_holidays 
WHERE is_public_holiday = 1
order by date desc limit 10;

--Aggregate: holidays vs non‑holidays
SELECT 
  is_public_holiday,
  AVG(temperature_2m_max) AS avg_tmax,
  AVG(temperature_2m_min) AS avg_tmin,
  AVG(precipitation_sum)  AS avg_precip,
  COUNT(*)                AS days_count
FROM vw_weather_with_holidays
GROUP BY is_public_holiday
ORDER BY is_public_holiday;

--Yearly comparison
SELECT 
  strftime('%Y', date) AS year,
  is_public_holiday,
  AVG(temperature_2m_max) AS avg_tmax,
  AVG(precipitation_sum)  AS avg_precip,
  COUNT(*)                AS days_count
FROM vw_weather_with_holidays
GROUP BY year, is_public_holiday
ORDER BY year, is_public_holiday;

--List just the holiday dates with weather
SELECT 
  date,
  holiday_names,
  temperature_2m_max,
  temperature_2m_min,
  precipitation_sum
FROM vw_weather_with_holidays
WHERE is_public_holiday = 1
ORDER BY date DESC
LIMIT 20;

--DROP TABLE IF EXISTS weather_with_holidays;
SELECT * FROM vw_weather_with_holidays;



