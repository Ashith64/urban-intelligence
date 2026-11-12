"""Master Data Preprocessing & Harmonization Pipeline for the Global Urban Intelligence Platform.

Processes:
- 238 Global Cities Quality of Life & Affordability indices
- Geolocation mapping (Latitude, Longitude, Continental Region)
- World Bank Macroeconomic Indicators (GDP per capita, Life Expectancy, Urbanization %)
- Mathematical Min-Max Normalization strictly bounded in [0, 1]
- Derived analytical classifications (Liveability Quadrants, Housing Affordability)
"""
import unicodedata
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

QOL_RAW_PATH = RAW_DATA_DIR / "quality_of_life_raw.csv"
CITIES_REF_PATH = RAW_DATA_DIR / "cities_reference.csv"
COUNTRY_MACRO_PATH = PROCESSED_DATA_DIR / "country_macro.csv"
MASTER_DATASET_PATH = PROCESSED_DATA_DIR / "global_urban_master.csv"

# Aliases for city names to guarantee exact coordinate resolution
CITY_NAME_ALIASES = {
    "quebec city": "quebec",
    "tel aviv-yafo": "tel aviv",
    "nizhny novgorod": "nizhniy novgorod",
    "wroclaw": "wroclaw",
    "lodz": "lodz",
    "krakow": "krakow",
    "gurgaon": "gurugram",
    "kiev": "kyiv",
    "bangalore": "bangalore",
    "thessaloniki": "thessaloniki",
    "sao paulo": "sao paulo",
    "new york": "new york",
}

# Country aliases for World Bank join
COUNTRY_ALIASES = {
    "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "Czech Republic": "Czechia",
    "Egypt": "Egypt, Arab Rep.",
    "Hong Kong": "Hong Kong SAR, China",
    "Iran": "Iran, Islamic Rep.",
    "Russia": "Russian Federation",
    "Slovakia": "Slovak Republic",
    "South Korea": "Korea, Rep.",
    "Turkey": "Turkiye",
    "Venezuela": "Venezuela, RB",
    "Vietnam": "Viet Nam",
}

# Region mapping heuristics for world continents
REGION_COUNTRY_MAP = {
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "Australia": "Oceania",
    "New Zealand": "Oceania",
    "Japan": "Asia",
    "China": "Asia",
    "South Korea": "Asia",
    "Taiwan": "Asia",
    "Singapore": "Asia",
    "Hong Kong": "Asia",
    "Thailand": "Asia",
    "Malaysia": "Asia",
    "Indonesia": "Asia",
    "Philippines": "Asia",
    "Vietnam": "Asia",
    "India": "South Asia",
    "Pakistan": "South Asia",
    "Bangladesh": "South Asia",
    "Sri Lanka": "South Asia",
    "Nepal": "South Asia",
    "United Arab Emirates": "Middle East",
    "Saudi Arabia": "Middle East",
    "Qatar": "Middle East",
    "Israel": "Middle East",
    "Kuwait": "Middle East",
    "Oman": "Middle East",
    "Jordan": "Middle East",
    "Lebanon": "Middle East",
    "Brazil": "South America",
    "Argentina": "South America",
    "Chile": "South America",
    "Colombia": "South America",
    "Peru": "South America",
    "Ecuador": "South America",
    "Uruguay": "South America",
    "Venezuela": "South America",
    "South Africa": "Africa",
    "Egypt": "Africa",
    "Kenya": "Africa",
    "Nigeria": "Africa",
    "Morocco": "Africa",
}


def strip_accents(text: str) -> str:
    """Strip accents and diacritics from a string."""
    if not isinstance(text, str):
        return text
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    ).strip()


def parse_location_string(raw_str: str) -> tuple[str, str | None, str]:
    """Parse City string into (City, State, Country)."""
    parts = [p.strip() for p in raw_str.split(",")]
    if len(parts) >= 3:
        city = parts[0].split("(")[0].strip()
        state = parts[1]
        country = parts[-1]
    elif len(parts) == 2:
        city = parts[0].split("(")[0].strip()
        state = None
        country = parts[1]
    else:
        city = parts[0].split("(")[0].strip()
        state = None
        country = ""
    return city, state, country


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Min-max normalize a numeric series strictly to [0, 1], preserving missing values."""
    s = pd.to_numeric(series, errors="coerce").astype(float)
    s = s.replace([np.inf, -np.inf], np.nan)
    valid = s.dropna()
    if valid.empty:
        return s
    min_val = valid.min()
    max_val = valid.max()
    if max_val == min_val:
        return s.where(s.isna(), 0.0)
    return (s - min_val) / (max_val - min_val)


def validate_normalized_columns(df: pd.DataFrame, tol: float = 1e-9) -> dict[str, dict]:
    """Validate all *_norm columns are strictly within [0, 1] (ignoring NaNs)."""
    norm_cols = [c for c in df.columns if c.endswith("_norm")]
    results = {}
    for col in norm_cols:
        s = df[col].dropna()
        if s.empty:
            results[col] = {"valid": False, "min": None, "max": None, "non_null": 0}
        else:
            cmin = float(s.min())
            cmax = float(s.max())
            is_valid = (cmin >= -tol) and (cmax <= 1.0 + tol)
            results[col] = {"valid": is_valid, "min": cmin, "max": cmax, "non_null": len(s)}
    return results


def build_geolocation_database() -> dict[str, tuple[float, float, str]]:
    """Build a comprehensive coordinate lookup dictionary from reference and open geonames."""
    geo_map = {}

    # 1. First priority: cities_reference.csv (high accuracy curated coordinates)
    if CITIES_REF_PATH.exists():
        ref_df = pd.read_csv(CITIES_REF_PATH)
        for _, row in ref_df.iterrows():
            clean_name = strip_accents(str(row["City"])).lower()
            geo_map[clean_name] = (float(row["Latitude"]), float(row["Longitude"]), str(row.get("Region", "Europe")))

    # Curated coordinates for global cities
    special_coords = {
        "canberra": (-35.2809, 149.1300, "Oceania"),
        "the hague": (52.0705, 4.3007, "Europe"),
        "adelaide": (-34.9285, 138.6007, "Oceania"),
        "raleigh": (35.7796, -78.6382, "North America"),
        "eindhoven": (51.4416, 5.4697, "Europe"),
        "wellington": (-41.2865, 174.7762, "Oceania"),
        "perth": (-31.9505, 115.8605, "Oceania"),
        "brisbane": (-27.4698, 153.0251, "Oceania"),
        "columbus": (39.9612, -82.9988, "North America"),
        "quebec": (46.8139, -71.2080, "North America"),
        "charlotte": (35.2271, -80.8431, "North America"),
        "san antonio": (29.4241, -98.4936, "North America"),
        "austin": (30.2672, -97.7431, "North America"),
        "albuquerque": (35.0844, -106.6504, "North America"),
        "dallas": (32.7767, -96.7970, "North America"),
        "houston": (29.7604, -95.3698, "North America"),
        "tampa": (27.9506, -82.4572, "North America"),
        "orlando": (28.5383, -81.3792, "North America"),
        "cleveland": (41.4993, -81.6944, "North America"),
        "cincinnati": (39.1031, -84.5120, "North America"),
        "indianapolis": (39.7684, -86.1581, "North America"),
        "kansas city": (39.0997, -94.5786, "North America"),
        "omaha": (41.2565, -95.9345, "North America"),
        "tulsa": (36.1540, -95.9928, "North America"),
        "oklahoma city": (35.4676, -97.5164, "North America"),
        "salt lake city": (40.7608, -111.8910, "North America"),
        "boise": (43.6150, -116.2023, "North America"),
        "phoenix": (33.4484, -112.0740, "North America"),
        "tucson": (32.2226, -110.9747, "North America"),
        "las vegas": (36.1699, -115.1398, "North America"),
        "san jose": (37.3382, -121.8863, "North America"),
        "san diego": (32.7157, -117.1611, "North America"),
        "sacramento": (38.5816, -121.4944, "North America"),
        "portland": (45.5152, -122.6784, "North America"),
        "minneapolis": (44.9778, -93.2650, "North America"),
        "madison": (43.0731, -89.4012, "North America"),
        "milwaukee": (43.0389, -87.9065, "North America"),
        "pittsburgh": (40.4406, -79.9959, "North America"),
        "philadelphia": (39.9526, -75.1652, "North America"),
        "baltimore": (39.2904, -76.6122, "North America"),
        "richmond": (37.5407, -77.4360, "North America"),
        "virginia beach": (36.8529, -75.9780, "North America"),
        "nashville": (36.1627, -86.7816, "North America"),
        "memphis": (35.1495, -90.0490, "North America"),
        "louisville": (38.2527, -85.7585, "North America"),
        "birmingham": (33.5186, -86.8104, "North America"),
        "new orleans": (29.9511, -90.0715, "North America"),
        "jacksonville": (30.3322, -81.6557, "North America"),
        "miami": (25.7617, -80.1918, "North America"),
        "atlanta": (33.7490, -84.3880, "North America"),
        "victoria": (48.4284, -123.3656, "North America"),
        "kelowna": (49.8880, -119.4960, "North America"),
        "edmonton": (53.5461, -113.4938, "North America"),
        "calgary": (51.0447, -114.0719, "North America"),
        "saskatoon": (52.1332, -106.6700, "North America"),
        "regina": (50.4547, -104.6067, "North America"),
        "winnipeg": (49.8951, -97.1384, "North America"),
        "halifax": (44.6488, -63.5752, "North America"),
        "london": (51.5074, -0.1278, "Europe"),
        "edinburgh": (55.9533, -3.1883, "Europe"),
        "glasgow": (55.8642, -4.2518, "Europe"),
        "belfast": (54.5973, -5.9301, "Europe"),
        "cardiff": (51.4816, -3.1791, "Europe"),
        "dublin": (53.3498, -6.2603, "Europe"),
        "cork": (51.8985, -8.4756, "Europe"),
        "galway": (53.2707, -9.0568, "Europe"),
        "reykjavik": (64.1466, -21.9426, "Europe"),
        "oslo": (59.9139, 10.7522, "Europe"),
        "bergen": (60.3913, 5.3221, "Europe"),
        "trondheim": (63.4305, 10.3951, "Europe"),
        "stavanger": (58.9690, 5.7331, "Europe"),
        "stockholm": (59.3293, 18.0686, "Europe"),
        "gothenburg": (57.7089, 11.9746, "Europe"),
        "malmo": (55.6050, 13.0038, "Europe"),
        "helsinki": (60.1699, 24.9384, "Europe"),
        "espoo": (60.2055, 24.6559, "Europe"),
        "tampere": (61.4978, 23.7610, "Europe"),
        "turku": (60.4518, 22.2666, "Europe"),
        "copenhagen": (55.6761, 12.5683, "Europe"),
        "aarhus": (56.1629, 10.2039, "Europe"),
        "aalborg": (57.0488, 9.9217, "Europe"),
        "odense": (55.4038, 10.4024, "Europe"),
        "amsterdam": (52.3676, 4.9041, "Europe"),
        "rotterdam": (51.9244, 4.4777, "Europe"),
        "utrecht": (52.0907, 5.1214, "Europe"),
        "groningen": (53.2194, 6.5665, "Europe"),
        "brussels": (50.8503, 4.3517, "Europe"),
        "antwerp": (51.2194, 4.4025, "Europe"),
        "ghent": (51.0543, 3.7174, "Europe"),
        "leuven": (50.8798, 4.7005, "Europe"),
        "zurich": (47.3769, 8.5417, "Europe"),
        "geneva": (46.2044, 6.1432, "Europe"),
        "basel": (47.5596, 7.5886, "Europe"),
        "lausanne": (46.5197, 6.6323, "Europe"),
        "bern": (46.9480, 7.4474, "Europe"),
        "vienna": (48.2082, 16.3738, "Europe"),
        "graz": (47.0707, 15.4395, "Europe"),
        "linz": (48.3069, 14.2858, "Europe"),
        "salzburg": (47.8095, 13.0550, "Europe"),
        "innsbruck": (47.2692, 11.4041, "Europe"),
        "berlin": (52.5200, 13.4050, "Europe"),
        "munich": (48.1351, 11.5820, "Europe"),
        "frankfurt": (50.1109, 8.6821, "Europe"),
        "hamburg": (53.5511, 9.9937, "Europe"),
        "cologne": (50.9375, 6.9603, "Europe"),
        "stuttgart": (48.7758, 9.1829, "Europe"),
        "dusseldorf": (51.2277, 6.7735, "Europe"),
        "leipzig": (51.3397, 12.3731, "Europe"),
        "dresden": (51.0504, 13.7373, "Europe"),
        "nuremberg": (49.4521, 11.0767, "Europe"),
        "paris": (48.8566, 2.3522, "Europe"),
        "lyon": (45.7640, 4.8357, "Europe"),
        "marseille": (43.2965, 5.3698, "Europe"),
        "toulouse": (43.6047, 1.4442, "Europe"),
        "bordeaux": (44.8378, -0.5792, "Europe"),
        "nice": (43.7102, 7.2620, "Europe"),
        "nantes": (47.2184, -1.5536, "Europe"),
        "strasbourg": (48.5734, 7.7521, "Europe"),
        "madrid": (40.4168, -3.7038, "Europe"),
        "barcelona": (41.3851, 2.1734, "Europe"),
        "valencia": (39.4699, -0.3763, "Europe"),
        "seville": (37.3891, -5.9845, "Europe"),
        "malaga": (36.7213, -4.4214, "Europe"),
        "bilbao": (43.2630, -2.9350, "Europe"),
        "rome": (41.9028, 12.4964, "Europe"),
        "milan": (45.4642, 9.1900, "Europe"),
        "florence": (43.7696, 11.2558, "Europe"),
        "bologna": (44.4949, 11.3426, "Europe"),
        "turin": (45.0703, 7.6869, "Europe"),
        "naples": (40.8518, 14.2681, "Europe"),
        "lisbon": (38.7223, -9.1393, "Europe"),
        "porto": (41.1579, -8.6291, "Europe"),
        "prague": (50.0755, 14.4378, "Europe"),
        "brno": (49.1951, 16.6068, "Europe"),
        "warsaw": (52.2297, 21.0122, "Europe"),
        "krakow": (50.0647, 19.9450, "Europe"),
        "wroclaw": (51.1079, 17.0385, "Europe"),
        "gdansk": (54.3520, 18.6466, "Europe"),
        "poznan": (52.4064, 16.9252, "Europe"),
        "lodz": (51.7592, 19.4560, "Europe"),
        "budapest": (47.4979, 19.0402, "Europe"),
        "bratislava": (48.1486, 17.1077, "Europe"),
        "ljubljana": (46.0569, 14.5058, "Europe"),
        "zagreb": (45.8150, 15.9819, "Europe"),
        "split": (43.5081, 16.4402, "Europe"),
        "belgrade": (44.7866, 20.4489, "Europe"),
        "bucharest": (44.4268, 26.1025, "Europe"),
        "cluj-napoca": (46.7712, 23.6236, "Europe"),
        "timisoara": (45.7489, 21.2087, "Europe"),
        "iasi": (47.1585, 27.6014, "Europe"),
        "sofia": (42.6977, 23.3219, "Europe"),
        "varna": (43.2141, 27.9147, "Europe"),
        "athens": (37.9838, 23.7275, "Europe"),
        "thessaloniki": (40.6401, 22.9444, "Europe"),
        "tokyo": (35.6762, 139.6503, "Asia"),
        "osaka": (34.6937, 135.5023, "Asia"),
        "kyoto": (35.0116, 135.7681, "Asia"),
        "seoul": (37.5665, 126.9780, "Asia"),
        "busan": (35.1796, 129.0756, "Asia"),
        "taipei": (25.0330, 121.5654, "Asia"),
        "beijing": (39.9042, 116.4074, "Asia"),
        "shanghai": (31.2304, 121.4737, "Asia"),
        "shenzhen": (22.5431, 114.0579, "Asia"),
        "guangzhou": (23.1291, 113.2644, "Asia"),
        "hong kong": (22.3193, 114.1694, "Asia"),
        "singapore": (1.3521, 103.8198, "Asia"),
        "bangkok": (13.7563, 100.5018, "Asia"),
        "chiang mai": (18.7883, 98.9853, "Asia"),
        "kuala lumpur": (3.1390, 101.6869, "Asia"),
        "penang": (5.4141, 100.3288, "Asia"),
        "jakarta": (-6.2088, 106.8456, "Asia"),
        "bali": (-8.3405, 115.0920, "Asia"),
        "manila": (14.5995, 120.9842, "Asia"),
        "ho chi minh city": (10.8231, 106.6297, "Asia"),
        "hanoi": (21.0285, 105.8542, "Asia"),
        "delhi": (28.6139, 77.2090, "South Asia"),
        "mumbai": (19.0760, 72.8777, "South Asia"),
        "bangalore": (12.9716, 77.5946, "South Asia"),
        "hyderabad": (17.3850, 78.4867, "South Asia"),
        "chennai": (13.0827, 80.2707, "South Asia"),
        "pune": (18.5204, 73.8567, "South Asia"),
        "kolkata": (22.5726, 88.3639, "South Asia"),
        "ahmedabad": (23.0225, 72.5714, "South Asia"),
        "gurgaon": (28.4595, 77.0266, "South Asia"),
        "noida": (28.5355, 77.3910, "South Asia"),
        "dubai": (25.2048, 55.2708, "Middle East"),
        "abu dhabi": (24.4539, 54.3773, "Middle East"),
        "doha": (25.2854, 51.5310, "Middle East"),
        "riyadh": (24.7136, 46.6753, "Middle East"),
        "jeddah": (21.4858, 39.1925, "Middle East"),
        "muscat": (23.5880, 58.3829, "Middle East"),
        "kuwait city": (29.3759, 47.9774, "Middle East"),
        "manama": (26.2285, 50.5860, "Middle East"),
        "tel aviv": (32.0853, 34.7818, "Middle East"),
        "jerusalem": (31.7683, 35.2137, "Middle East"),
        "amman": (31.9454, 35.9284, "Middle East"),
        "cairo": (30.0444, 31.2357, "Africa"),
        "johannesburg": (-26.2041, 28.0473, "Africa"),
        "cape town": (-33.9249, 18.4241, "Africa"),
        "durban": (-29.8587, 31.0218, "Africa"),
        "pretoria": (-25.7479, 28.2293, "Africa"),
        "nairobi": (-1.2921, 36.8219, "Africa"),
        "casablanca": (33.5731, -7.5898, "Africa"),
        "lagos": (6.5244, 3.3792, "Africa"),
        "sao paulo": (-23.5505, -46.6333, "South America"),
        "rio de janeiro": (-22.9068, -43.1729, "South America"),
        "brasilia": (-15.7975, -47.8919, "South America"),
        "curitiba": (-25.4284, -49.2733, "South America"),
        "buenos aires": (-34.6037, -58.3816, "South America"),
        "cordoba": (-31.4201, -64.1888, "South America"),
        "santiago": (-33.4489, -70.6693, "South America"),
        "bogota": (4.7110, -74.0721, "South America"),
        "medellin": (6.2442, -75.5812, "South America"),
        "lima": (-12.0464, -77.0428, "South America"),
        "montevideo": (-34.9011, -56.1645, "South America"),
        "quito": (-0.1807, -78.4678, "South America"),
        "caracas": (10.4806, -66.9036, "South America"),
    }
    for k, v in special_coords.items():
        geo_map[k] = v

    return geo_map


def build_master_dataset() -> pd.DataFrame:
    """Ingest, clean, normalize, and merge all sources into global_urban_master.csv."""
    # 1. Ingest Quality of Life raw data
    qol_df = pd.read_csv(QOL_RAW_PATH)
    qol_df.columns = [c.strip().replace(" ", "_") for c in qol_df.columns]

    # Parse city, state, country
    parsed_locs = [parse_location_string(x) for x in qol_df["City"]]
    qol_df["City_Raw"] = qol_df["City"]
    raw_cities = [p[0] for p in parsed_locs]
    qol_df["State"] = [p[1] for p in parsed_locs]
    qol_df["Country"] = [p[2] for p in parsed_locs]

    # Disambiguate duplicate city names with country/state suffix
    clean_cities = []
    for c, s, cntry in zip(raw_cities, qol_df["State"], qol_df["Country"]):
        if c == "San Jose" and cntry == "United States":
            clean_cities.append("San Jose, CA")
        elif c == "San Jose" and cntry == "Costa Rica":
            clean_cities.append("San Jose, Costa Rica")
        else:
            clean_cities.append(c)
    qol_df["City"] = clean_cities

    # 2. Attach Geolocation & Regional mapping
    geo_map = build_geolocation_database()
    lats, lons, regions = [], [], []

    for _, row in qol_df.iterrows():
        c_name = strip_accents(row["City"]).lower()
        alias_name = CITY_NAME_ALIASES.get(c_name, c_name)
        country = row["Country"]

        if alias_name in geo_map:
            lat, lon, reg = geo_map[alias_name]
        elif c_name in geo_map:
            lat, lon, reg = geo_map[c_name]
        else:
            # Fallback based on country
            lat, lon, reg = 0.0, 0.0, REGION_COUNTRY_MAP.get(country, "Europe")

        # Prioritize country region map if region is Europe default
        final_reg = REGION_COUNTRY_MAP.get(country, reg)
        lats.append(lat)
        lons.append(lon)
        regions.append(final_reg)

    qol_df["Latitude"] = lats
    qol_df["Longitude"] = lons
    qol_df["Region"] = regions

    # 3. Merge World Bank macro data
    if COUNTRY_MACRO_PATH.exists():
        wb_df = pd.read_csv(COUNTRY_MACRO_PATH)
        qol_df["_wb_country"] = qol_df["Country"].map(lambda c: COUNTRY_ALIASES.get(c, c))
        qol_df = pd.merge(
            qol_df,
            wb_df[["country_name", "GDP_Per_Capita_USD", "Life_Expectancy_Years", "Urban_Population_Pct"]],
            left_on="_wb_country",
            right_on="country_name",
            how="left",
        )
        qol_df.drop(columns=["_wb_country", "country_name"], errors="ignore", inplace=True)

    # Impute regional medians for any missing macro data points
    for m_col in ["GDP_Per_Capita_USD", "Life_Expectancy_Years", "Urban_Population_Pct"]:
        if m_col in qol_df.columns:
            qol_df[m_col] = qol_df.groupby("Region")[m_col].transform(lambda x: x.fillna(x.median()))
            qol_df[m_col] = qol_df[m_col].fillna(qol_df[m_col].median())

    # 4. Drop temporary columns
    qol_df.drop(columns=["City_Raw"], errors="ignore", inplace=True)

    # 5. Min-Max Normalization strictly within [0, 1]
    norm_metrics = [
        "Quality_of_Life_Index",
        "Purchasing_Power_Index",
        "Safety_Index",
        "Health_Care_Index",
        "Cost_of_Living_Index",
        "Property_Price_to_Income_Ratio",
        "Traffic_Commute_Time_Index",
        "Pollution_Index",
        "Climate_Index",
    ]
    for col in norm_metrics:
        qol_df[f"{col}_norm"] = min_max_normalize(qol_df[col])

    # Inverted norms for positive interpretation
    qol_df["Clean_Environment_norm"] = 1.0 - qol_df["Pollution_Index_norm"]
    qol_df["Housing_Affordability_norm"] = 1.0 - qol_df["Property_Price_to_Income_Ratio_norm"]

    # 6. Liveability Quadrants
    med_power = qol_df["Purchasing_Power_Index"].median()
    med_pol = qol_df["Pollution_Index"].median()

    def assign_zone(r):
        high_p = r["Purchasing_Power_Index"] >= med_power
        clean_air = r["Pollution_Index"] <= med_pol
        if high_p and clean_air:
            return "★ High Power · Clean Air"
        elif high_p and not clean_air:
            return "High Power · Polluted"
        elif not high_p and clean_air:
            return "Low Power · Clean Air"
        else:
            return "Low Power · Polluted"

    qol_df["Liveability_Zone"] = qol_df.apply(assign_zone, axis=1)

    # 7. Illustrative Composite Score (0 - 100)
    qol_df["Affordability_Air_Composite"] = (
        100.0 * (0.5 * qol_df["Purchasing_Power_Index_norm"] + 0.5 * qol_df["Clean_Environment_norm"])
    ).round(2)

    # Reorder clean columns
    cols_order = [
        "City", "State", "Country", "Region", "Latitude", "Longitude",
        "Quality_of_Life_Index", "Purchasing_Power_Index", "Safety_Index", "Health_Care_Index",
        "Cost_of_Living_Index", "Property_Price_to_Income_Ratio", "Traffic_Commute_Time_Index",
        "Pollution_Index", "Climate_Index", "GDP_Per_Capita_USD", "Life_Expectancy_Years",
        "Urban_Population_Pct", "Liveability_Zone", "Affordability_Air_Composite",
    ]
    # Append norm columns
    for c in qol_df.columns:
        if c.endswith("_norm") and c not in cols_order:
            cols_order.append(c)

    final_df = qol_df[cols_order].copy()
    final_df.sort_values(by="Affordability_Air_Composite", ascending=False, inplace=True)
    final_df.reset_index(drop=True, inplace=True)

    # Save to processed master CSV
    final_df.to_csv(MASTER_DATASET_PATH, index=False)
    print(f"Master dataset successfully built: {MASTER_DATASET_PATH} ({len(final_df)} cities)")
    return final_df


def run_pipeline() -> pd.DataFrame:
    """Run end-to-end data build."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return build_master_dataset()


if __name__ == "__main__":
    df = run_pipeline()
    val = validate_normalized_columns(df)
    pass_cnt = sum(1 for v in val.values() if v["valid"])
    print(f"Validation checks: {pass_cnt}/{len(val)} passed")
