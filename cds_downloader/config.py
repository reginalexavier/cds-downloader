"""Default datasets, variables, and request options."""

DAILY_DATASET = "derived-era5-land-daily-statistics"
HOURLY_DATASET = "reanalysis-era5-land"

DAILY_AGGREGATED_VARIABLES = (
    "2m_dewpoint_temperature",
    "2m_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
)

DAILY_ACCUMULATED_VARIABLES = (
    "surface_solar_radiation_downwards",
    "total_precipitation",
)

HOURLY_VARIABLES = DAILY_AGGREGATED_VARIABLES + DAILY_ACCUMULATED_VARIABLES

DAILY_STATISTICS = (
    "daily_mean",
    "daily_minimum",
    "daily_maximum",
)

DEFAULT_AREA = (-15.36, -55.91, -17.24, -53.14)
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_DATA_FORMAT = "netcdf"
DEFAULT_DOWNLOAD_FORMAT = "unarchived"
DEFAULT_ACCUMULATED_TIME = "00:00"
DEFAULT_DAILY_FREQUENCY = "1_hourly"
DEFAULT_TIME_ZONE = "utc+00:00"
