USE DW_Assignment;
GO

-- =============================================
-- 1. XÓA BẢNG CŨ (Theo đúng thứ tự Fact -> Dim)
-- =============================================
IF OBJECT_ID('dbo.FactAccident', 'U') IS NOT NULL DROP TABLE dbo.FactAccident;
IF OBJECT_ID('dbo.DimLocation', 'U') IS NOT NULL DROP TABLE dbo.DimLocation;
IF OBJECT_ID('dbo.DimWeather', 'U') IS NOT NULL DROP TABLE dbo.DimWeather;
IF OBJECT_ID('dbo.DimTime', 'U') IS NOT NULL DROP TABLE dbo.DimTime;

-- =============================================
-- 2. TẠO LẠI CÁC BẢNG DIM (Bắt buộc có IDENTITY)
-- =============================================

-- BẢNG 1: DimLocation
-- (Đã sửa: Thêm IDENTITY(1,1) để Pentaho dùng Auto Increment)
CREATE TABLE DimLocation (
    LocationKey INT IDENTITY(1,1) PRIMARY KEY, 
    start_lat FLOAT,
    start_lng FLOAT,
    city NVARCHAR(255),
    state NVARCHAR(50),
    zipcode NVARCHAR(20),
    country NVARCHAR(50),
    street NVARCHAR(255),
    county NVARCHAR(100),
    lat_lng_interaction FLOAT,
    geo_density FLOAT
);
-- Tạo Index cho Location (Quan trọng để Lookup nhanh)
CREATE INDEX IDX_Loc_LatLng ON DimLocation(start_lat, start_lng);


-- BẢNG 2: DimWeather
CREATE TABLE DimWeather (
    WeatherKey INT IDENTITY(1,1) PRIMARY KEY,
    weather_conditions NVARCHAR(255),
    fog INT, rain INT, snow INT, hail INT, thunderstorm INT, tornado INT,
    temperature_f FLOAT,
    precipitation_in FLOAT,
    windspeed_mph FLOAT,
    visibility_mi FLOAT,
    humidity_percent FLOAT,
    pressure_in FLOAT,
    temp_humidity FLOAT,
    pressure_temp FLOAT
);
-- Tạo Index cho Weather
CREATE INDEX IDX_Weather_Lookup ON DimWeather(weather_conditions); 


-- BẢNG 3: DimTime
CREATE TABLE DimTime (
    TimeKey INT IDENTITY(1,1) PRIMARY KEY,
    fulldate DATETIME,
    hour INT, day INT, month INT, year INT, 
    second INT, minute INT,
    hour_day INT, hour_month INT
);
-- Tạo Index cho Time
CREATE INDEX IDX_Time_Date ON DimTime(fulldate);


-- =============================================
-- 3. TẠO LẠI BẢNG FACT (Đã loại bỏ cột lỗi)
-- =============================================
CREATE TABLE FactAccident (
    AccidentKey INT IDENTITY(1,1) PRIMARY KEY,
    id VARCHAR(50),
    
    -- Các khóa ngoại (FK) trỏ về Dim
    LocationKey INT, 
    WeatherKey INT,
    TimeKey INT,
    
    -- Các số liệu đo đạc (Measures) - Đã bỏ 3 cột gây lỗi
    severity FLOAT,
    distance_mi FLOAT,
    delayfromfreeflowspeed_mins FLOAT,
    delayfromtypicaltraffic_mins FLOAT,
    congestion_speed NVARCHAR(255),
    
    starttime DATETIME,
    endtime DATETIME
);

USE DW_Assignment;
GO

-- Đổi cột congestion_speed từ FLOAT sang NVARCHAR để chứa được chữ "Moderate"
ALTER TABLE FactAccident
ALTER COLUMN congestion_speed NVARCHAR(255);

Select * 
from FactAccident