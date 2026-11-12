"""Central configuration, constants, aliases, and palettes for BISL504."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_NUMBEO_PATH = DATA_RAW_DIR / "numbeo_raw.csv"
RAW_IQAIR_PATH = DATA_RAW_DIR / "iqair_raw.csv"
RAW_TOMTOM_PATH = DATA_RAW_DIR / "tomtom_raw.csv"
RAW_CITIES_REF_PATH = DATA_RAW_DIR / "cities_reference.csv"

PROCESSED_COL_PATH = DATA_PROCESSED_DIR / "cost_of_living_processed.csv"
PROCESSED_AQ_PATH = DATA_PROCESSED_DIR / "air_quality_processed.csv"
PROCESSED_TRAFFIC_PATH = DATA_PROCESSED_DIR / "traffic_processed.csv"
FINAL_MERGED_PATH = DATA_PROCESSED_DIR / "final_merged.csv"

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
    "Washington, D.C.": "Washington",
}

COUNTRY_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "Hong Kong SAR": "Hong Kong",
    "UK": "United Kingdom",
    "Bosnia Herzegovina": "Bosnia and Herzegovina",
}

TOMTOM_CC_MAP = {
    "MX": "Mexico",
    "IN": "India",
    "IE": "Ireland",
    "TR": "Turkey",
    "ID": "Indonesia",
    "BR": "Brazil",
    "NL": "Netherlands",
    "JP": "Japan",
    "FR": "France",
    "US": "United States",
    "UK": "United Kingdom",
}

WHO_PM25_GUIDELINE = 5.0

WHO_BAND_ORDER = [
    "Meets guideline",
    "Interim 4",
    "Interim 3",
    "Interim 2",
    "Interim 1",
    "Above interim targets",
]

DEFAULT_WEIGHT_LPP = 0.6
DEFAULT_WEIGHT_AIR = 0.4

# Okabe-Ito color-blind-safe palette
OKABE_ITO_PALETTE = [
    "#0072B2",  # Blue
    "#E69F00",  # Orange
    "#009E73",  # Bluish green
    "#D55E00",  # Vermilion
    "#CC79A7",  # Reddish purple
    "#56B4E9",  # Sky blue
    "#F0E442",  # Yellow
    "#000000",  # Black
]

WHO_BAND_COLORS = {
    "Meets guideline": "#009E73",
    "Interim 4": "#56B4E9",
    "Interim 3": "#F0E442",
    "Interim 2": "#E69F00",
    "Interim 1": "#D55E00",
    "Above interim targets": "#CC79A7",
}

NUMBEO_NUMERIC_COLS = [
    "Cost_of_Living_Index",
    "Rent_Index",
    "Cost_of_Living_Plus_Rent_Index",
    "Groceries_Index",
    "Restaurant_Price_Index",
    "Local_Purchasing_Power_Index",
]

IQAIR_NUMERIC_COLS = ["PM2_5_2024_ugm3"]

TOMTOM_NUMERIC_COLS = [
    "Congestion_Level_2025_pct",
    "Change_vs_2024_pp",
    "Avg_Speed_kmh",
    "Rush_Hours_Lost_per_Year",
]
