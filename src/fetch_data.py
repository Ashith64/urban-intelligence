"""Autonomous data fetcher and cache manager for the Global Urban Intelligence Platform.

Downloads and caches:
1. Quality of life and affordability dataset (238 global cities across 10 dimensions)
2. Geolocation coordinates (latitude, longitude, country)
3. World Bank macroeconomic indicators (GDP per capita, life expectancy, urbanization rate)
"""
import io
import json
import urllib.request
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

QOL_URL = "https://raw.githubusercontent.com/manavanandani/Quality_of_Life_Prediction/master/quality_of_life.csv"
GEO_URL = "https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def fetch_quality_of_life_data() -> pd.DataFrame:
    """Download the 238-city multi-index quality of life & affordability dataset."""
    dest_path = RAW_DATA_DIR / "quality_of_life_raw.csv"
    if dest_path.exists():
        print(f"Loading cached quality of life data from {dest_path}")
        return pd.read_csv(dest_path)

    print("Fetching quality of life data from GitHub...")
    req = urllib.request.Request(QOL_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as response:
        content = response.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(content))
        df.to_csv(dest_path, index=False)
        print(f"Saved {len(df)} records to {dest_path}")
        return df


def fetch_cities_geo_lookup() -> dict[str, tuple[float, float, str]]:
    """Download global cities geolocation database and create a lookup dict."""
    dest_path = RAW_DATA_DIR / "cities_geo_sample.json"
    
    print("Fetching geolocation coordinate database...")
    req = urllib.request.Request(GEO_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
        
    geo_dict = {}
    for item in data:
        name = item.get("name", "").strip().lower()
        if name and name not in geo_dict:
            try:
                lat = float(item.get("lat"))
                lng = float(item.get("lng"))
                country_code = item.get("country", "")
                geo_dict[name] = (lat, lng, country_code)
            except (ValueError, TypeError):
                continue
    print(f"Parsed {len(geo_dict)} unique city coordinate mappings.")
    return geo_dict


def fetch_world_bank_macro_indicators() -> pd.DataFrame:
    """Fetch country-level macroeconomic indicators from World Bank Open Data API."""
    dest_path = PROCESSED_DATA_DIR / "country_macro.csv"
    if dest_path.exists():
        print(f"Loading cached World Bank indicators from {dest_path}")
        return pd.read_csv(dest_path)

    print("Fetching macroeconomic indicators from World Bank API...")
    indicators = {
        "NY.GDP.PCAP.CD": "GDP_Per_Capita_USD",
        "SP.DYN.LE00.IN": "Life_Expectancy_Years",
        "SP.URB.TOTL.IN.ZS": "Urban_Population_Pct",
    }
    merged_df = pd.DataFrame()

    for ind, col_name in indicators.items():
        url = f"https://api.worldbank.org/v2/country/all/indicator/{ind}?date=2023&format=json&per_page=300"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if len(payload) > 1 and payload[1]:
                    records = []
                    for entry in payload[1]:
                        records.append({
                            "country_code": entry.get("countryiso3code"),
                            "country_name": entry.get("country", {}).get("value"),
                            col_name: entry.get("value"),
                        })
                    temp_df = pd.DataFrame(records)
                    if merged_df.empty:
                        merged_df = temp_df
                    else:
                        merged_df = pd.merge(merged_df, temp_df[["country_code", col_name]], on="country_code", how="left")
        except Exception as e:
            print(f"Error fetching {ind}: {e}")

    if not merged_df.empty:
        merged_df.to_csv(dest_path, index=False)
        print(f"Saved World Bank indicators to {dest_path}")
    return merged_df


def main():
    qol_df = fetch_quality_of_life_data()
    print("Quality of life dataset shape:", qol_df.shape)
    macro_df = fetch_world_bank_macro_indicators()
    print("Macro dataset shape:", macro_df.shape)


if __name__ == "__main__":
    main()
