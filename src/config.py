"""Configuration and constants for BISL504 Urban Affordability & Liveability Platform."""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

NUMBEO_RAW_PATH = RAW_DATA_DIR / "numbeo_raw.csv"
IQAIR_RAW_PATH = RAW_DATA_DIR / "iqair_raw.csv"
TOMTOM_RAW_PATH = RAW_DATA_DIR / "tomtom_raw.csv"
CITIES_REF_PATH = RAW_DATA_DIR / "cities_reference.csv"

COST_OF_LIVING_PROCESSED_PATH = PROCESSED_DATA_DIR / "cost_of_living_processed.csv"
AIR_QUALITY_PROCESSED_PATH = PROCESSED_DATA_DIR / "air_quality_processed.csv"
TRAFFIC_PROCESSED_PATH = PROCESSED_DATA_DIR / "traffic_processed.csv"
FINAL_MERGED_PATH = PROCESSED_DATA_DIR / "final_merged.csv"

# City Aliases
CITY_ALIASES = {
    "Tel Aviv-Yafo": "Tel Aviv",
    "Krakow (Cracow)": "Krakow",
    "Lucknow (Lakhnau)": "Lucknow",
    "Jeddah (Jiddah)": "Jeddah",
    "Kiev": "Kyiv",
    "New Delhi": "Delhi",
    "Dakha": "Dhaka",
    "Bengaluru": "Bangalore",
    "Washington D.C.": "Washington",
}

# Country Aliases and ISO codes
COUNTRY_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "Hong Kong SAR": "Hong Kong",
    "UK": "United Kingdom",
    "Bosnia Herzegovina": "Bosnia and Herzegovina",
    "MX": "Mexico",
    "IN": "India",
    "IE": "Ireland",
    "TR": "Turkey",
    "ID": "Indonesia",
    "BR": "Brazil",
    "NL": "Netherlands",
    "JP": "Japan",
    "FR": "France",
}

# WHO PM2.5 Guidelines & Bands
WHO_ANNUAL_GUIDELINE = 5.0
PM25_BANDS = [
    (0.0, 5.0, "Meets guideline"),
    (5.0, 10.0, "Interim 4"),
    (10.0, 15.0, "Interim 3"),
    (15.0, 25.0, "Interim 2"),
    (25.0, 35.0, "Interim 1"),
    (35.0, float("inf"), "Above interim targets"),
]

# Color Palette: Okabe-Ito (color-blind friendly)
OKABE_ITO_PALETTE = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "reddish_purple": "#CC79A7",
}

REGION_COLORS = {
    "Europe": "#0072B2",
    "Asia": "#E69F00",
    "North America": "#56B4E9",
    "Latin America": "#009E73",
    "Oceania": "#CC79A7",
    "Africa": "#D55E00",
    "Middle East": "#F0E442",
}

PM25_BAND_COLORS = {
    "Meets guideline": "#009E73",
    "Interim 4": "#56B4E9",
    "Interim 3": "#F0E442",
    "Interim 2": "#E69F00",
    "Interim 1": "#D55E00",
    "Above interim targets": "#882255",
}

# Default score weights
DEFAULT_WEIGHT_LPP = 0.6
DEFAULT_WEIGHT_PM25 = 0.4
