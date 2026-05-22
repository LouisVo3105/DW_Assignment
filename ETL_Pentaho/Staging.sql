-- Xóa bảng cũ nếu tồn tại
DROP TABLE IF EXISTS staging_congestion_raw;

CREATE TABLE staging_congestion_raw (
    id TEXT,
    severity TEXT,
    start_lat TEXT,
    start_lng TEXT,
    starttime TEXT,
    endtime TEXT,
    distance_mi TEXT,                   -- Gốc: Distance(mi)
    delay_typical_traffic_mins TEXT,    -- Gốc: DelayFromTypicalTraffic(mins)
    delay_free_flow_speed_mins TEXT,    -- Gốc: DelayFromFreeFlowSpeed(mins)
    congestion_speed TEXT,
    description TEXT,
    street TEXT,
    city TEXT,
    county TEXT,
    state TEXT,
    country TEXT,
    zipcode TEXT,
    local_timezone TEXT,
    weather_station_code TEXT,          -- Gốc: WeatherStation_AirportCode
    weather_timestamp TEXT,
    temperature_f TEXT,                 -- Gốc: Temperature(F)
    wind_chill_f TEXT,                  -- Gốc: WindChill(F)
    humidity_percent TEXT,              -- Gốc: Humidity(%)
    pressure_in TEXT,                   -- Gốc: Pressure(in)
    visibility_mi TEXT,                 -- Gốc: Visibility(mi)
    wind_dir TEXT,
    wind_speed_mph TEXT,                -- Gốc: WindSpeed(mph)
    precipitation_in TEXT,              -- Gốc: Precipitation(in)
    weather_event TEXT,
    weather_conditions TEXT,
    
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT COUNT(*) AS total_rows FROM staging_congestion_raw;

SELECT * FROM staging_congestion_raw LIMIT 100;

-- Kiểm tra xem các số khoa học (chữ e) có vào được không
SELECT id, start_lat, precipitation_in 
FROM staging_congestion_raw 
WHERE start_lat LIKE '%e%' OR precipitation_in LIKE '%e%'
LIMIT 20;

-- Kiểm tra cột thời gian nạp (để chắc chắn đây là dữ liệu mới nạp)
SELECT MAX(loaded_at) as last_load_time FROM staging_congestion_raw;



-- Ép kiểu sang timestamp, dòng nào lỗi thành NULL
ALTER TABLE staging_congestion_raw 
ALTER COLUMN starttime TYPE TIMESTAMP USING starttime::TIMESTAMP,
ALTER COLUMN endtime TYPE TIMESTAMP USING endtime::TIMESTAMP,
ALTER COLUMN weather_timestamp TYPE TIMESTAMP USING weather_timestamp::TIMESTAMP;

-- Xóa dòng NULL (tương đương df.dropna(subset=['starttime', 'endtime']))
DELETE FROM staging_congestion_raw WHERE starttime IS NULL OR endtime IS NULL;




-- Tương đương df['weather_event'].fillna('None')
UPDATE staging_congestion_raw SET weather_event = 'None' WHERE weather_event IS NULL;

-- Tương đương df['precipitation(in)'] fill theo logic median group by weather_event
-- (Dùng Window Function của Postgres thay vì Groupby của Pandas)
WITH MedianData AS (
    SELECT weather_event, 
           PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY CAST(precipitation_in AS FLOAT)) AS median_val
    FROM staging_congestion_raw 
    WHERE precipitation_in IS NOT NULL 
    GROUP BY weather_event
)
UPDATE staging_congestion_raw s
SET precipitation_in = m.median_val
FROM MedianData m
WHERE s.weather_event = m.weather_event 
  AND s.precipitation_in IS NULL;

-- Set về 0 nếu vẫn còn NULL (logic fallback)
UPDATE staging_congestion_raw SET precipitation_in = '0' WHERE precipitation_in IS NULL;


-- ================================================================
-- SCRIPT XỬ LÝ DỮ LIỆU THIẾU (NUMERIC FILLNA MEDIAN)
-- ================================================================

-- 1. Xử lý cột TEMPERATURE_F
WITH MedianCalc AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY CAST(temperature_f AS FLOAT)) AS median_val
    FROM staging_congestion_raw 
    WHERE temperature_f IS NOT NULL AND temperature_f <> '' 
      -- Regex kiểm tra xem có phải số hợp lệ không để tránh lỗi cast
      AND temperature_f ~ '^[+-]?([0-9]*[.])?[0-9]+(e[+-]?[0-9]+)?$' 
)
UPDATE staging_congestion_raw
SET temperature_f = (SELECT median_val FROM MedianCalc)
WHERE temperature_f IS NULL OR temperature_f = '';

-- 2. Xử lý cột HUMIDITY_PERCENT
WITH MedianCalc AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY CAST(humidity_percent AS FLOAT)) AS median_val
    FROM staging_congestion_raw 
    WHERE humidity_percent IS NOT NULL AND humidity_percent <> ''
      AND humidity_percent ~ '^[+-]?([0-9]*[.])?[0-9]+(e[+-]?[0-9]+)?$'
)
UPDATE staging_congestion_raw
SET humidity_percent = (SELECT median_val FROM MedianCalc)
WHERE humidity_percent IS NULL OR humidity_percent = '';

-- 3. Xử lý cột PRESSURE_IN
WITH MedianCalc AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY CAST(pressure_in AS FLOAT)) AS median_val
    FROM staging_congestion_raw 
    WHERE pressure_in IS NOT NULL AND pressure_in <> ''
      AND pressure_in ~ '^[+-]?([0-9]*[.])?[0-9]+(e[+-]?[0-9]+)?$'
)
UPDATE staging_congestion_raw
SET pressure_in = (SELECT median_val FROM MedianCalc)
WHERE pressure_in IS NULL OR pressure_in = '';

-- 4. Xử lý cột VISIBILITY_MI
WITH MedianCalc AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY CAST(visibility_mi AS FLOAT)) AS median_val
    FROM staging_congestion_raw 
    WHERE visibility_mi IS NOT NULL AND visibility_mi <> ''
      AND visibility_mi ~ '^[+-]?([0-9]*[.])?[0-9]+(e[+-]?[0-9]+)?$'
)
UPDATE staging_congestion_raw
SET visibility_mi = (SELECT median_val FROM MedianCalc)
WHERE visibility_mi IS NULL OR visibility_mi = '';

-- 5. Xử lý cột WIND_SPEED_MPH
WITH MedianCalc AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY CAST(wind_speed_mph AS FLOAT)) AS median_val
    FROM staging_congestion_raw 
    WHERE wind_speed_mph IS NOT NULL AND wind_speed_mph <> ''
      AND wind_speed_mph ~ '^[+-]?([0-9]*[.])?[0-9]+(e[+-]?[0-9]+)?$'
)
UPDATE staging_congestion_raw
SET wind_speed_mph = (SELECT median_val FROM MedianCalc)
WHERE wind_speed_mph IS NULL OR wind_speed_mph = '';

-- ================================================================
-- KẾT THÚC XỬ LÝ
-- ================================================================


SELECT COUNT(*) FROM staging_congestion_raw WHERE temperature_f IS NULL;