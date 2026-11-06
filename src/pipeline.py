"""Data preprocessing and harmonization pipeline for BISL504.

Executes cleaning, label parsing, alias mapping, scope validation, outlier flagging,
min-max normalization, merging, and derived metric computation.
"""
import unicodedata
from pathlib import Path
import numpy as np
import pandas as pd

from src.config import (
    CITIES_REF_PATH,
    NUMBEO_RAW_PATH,
    IQAIR_RAW_PATH,
    TOMTOM_RAW_PATH,
    COST_OF_LIVING_PROCESSED_PATH,
    AIR_QUALITY_PROCESSED_PATH,
    TRAFFIC_PROCESSED_PATH,
    FINAL_MERGED_PATH,
    PROCESSED_DATA_DIR,
    CITY_ALIASES,
    COUNTRY_ALIASES,
    WHO_ANNUAL_GUIDELINE,
    PM25_BANDS,
    DEFAULT_WEIGHT_LPP,
    DEFAULT_WEIGHT_PM25,
)


def strip_accents(text: str) -> str:
    """Strip accents and diacritics from a string."""
    if not isinstance(text, str):
        return text
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    ).strip()


def parse_location_label(raw_label: str) -> tuple[str, str | None, str]:
    """Parse raw city string into (City, State, Country) with alias replacement."""
    if not isinstance(raw_label, str):
        return ("", None, "")

    parts = [strip_accents(p.strip()) for p in raw_label.split(",")]
    if len(parts) >= 3:
        city = parts[0]
        state = parts[1]
        country = parts[-1]
    elif len(parts) == 2:
        city = parts[0]
        state = None
        country = parts[1]
    else:
        city = parts[0]
        state = None
        country = ""

    city = CITY_ALIASES.get(city, city)
    country = COUNTRY_ALIASES.get(country, country)
    return city, state, country


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Min-max normalize a numeric series to [0, 1]."""
    s = series.astype(float)
    min_val = s.min()
    max_val = s.max()
    if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
        return pd.Series(0.0, index=series.index)
    return (s - min_val) / (max_val - min_val)


def flag_outliers_iqr(series: pd.Series, factor: float = 1.5) -> pd.Series:
    """Flag outliers using the IQR rule without removing values."""
    s = series.dropna().astype(float)
    if len(s) < 4:
        return pd.Series(False, index=series.index)
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    return (series < lower_bound) | (series > upper_bound)


def assign_pm25_band(val: float) -> str:
    """Assign WHO guideline band to a PM2.5 concentration."""
    if pd.isna(val):
        return "Unknown"
    for low, high, label in PM25_BANDS:
        if low == 0.0 and val <= high:
            return label
        elif low < val <= high:
            return label
    return "Above interim targets"


def load_and_clean_cities_ref() -> pd.DataFrame:
    """Load and standardize cities reference scope dataset."""
    df = pd.read_csv(CITIES_REF_PATH)
    df["City"] = df["City"].apply(strip_accents).map(lambda c: CITY_ALIASES.get(c, c))
    df["Country"] = df["Country"].apply(strip_accents).map(lambda c: COUNTRY_ALIASES.get(c, c))
    return df


def process_numbeo(cities_ref: pd.DataFrame) -> pd.DataFrame:
    """Process Numbeo raw data into standardized cost of living dataset."""
    df = pd.read_csv(NUMBEO_RAW_PATH)
    df = df.drop_duplicates().copy()

    # Rename existing columns
    col_map = {
        "Cost of Living Index": "Cost_of_Living_Index",
        "Rent Index": "Rent_Index",
        "Cost of Living Plus Rent Index": "Cost_of_Living_Plus_Rent_Index",
        "Groceries Index": "Groceries_Index",
        "Restaurant Price Index": "Restaurant_Price_Index",
        "Local Purchasing Power Index": "Local_Purchasing_Power_Index",
    }
    df = df.rename(columns=col_map)
    df["City_Raw"] = df["City"]

    # Parse City, State, Country
    parsed = [parse_location_label(x) for x in df["City_Raw"]]
    df["City"] = [p[0] for p in parsed]
    df["State"] = [p[1] for p in parsed]
    df["Country"] = [p[2] for p in parsed]

    # In project scope check
    scope_set = set(zip(cities_ref["City"], cities_ref["Country"]))
    df["In_Project_Scope"] = [
        (c, cntry) in scope_set for c, cntry in zip(df["City"], df["Country"])
    ]
    # Special case: Portland is in scope only when State == OR
    df.loc[(df["City"] == "Portland") & (df["State"] != "OR"), "In_Project_Scope"] = False

    # Outliers (1.5x IQR across all 6 index columns)
    num_cols = list(col_map.values())
    outlier_mask = pd.Series(False, index=df.index)
    for col in num_cols:
        outlier_mask |= flag_outliers_iqr(df[col])
    df["Outlier_Flags_IQR"] = outlier_mask

    # Normalization
    for col in num_cols:
        df[f"{col}_norm"] = min_max_normalize(df[col])

    return df


def process_iqair(cities_ref: pd.DataFrame) -> pd.DataFrame:
    """Process IQAir raw data into standardized air quality dataset."""
    df = pd.read_csv(IQAIR_RAW_PATH)
    df = df.drop_duplicates().copy()

    df["City_Raw"] = df["City_As_Published"]
    parsed = [parse_location_label(x) for x in df["City_Raw"]]
    df["City"] = [p[0] for p in parsed]
    df["State"] = [p[1] for p in parsed]
    df["Country"] = [p[2] for p in parsed]

    scope_set = set(zip(cities_ref["City"], cities_ref["Country"]))
    df["In_Project_Scope"] = [
        (c, cntry) in scope_set for c, cntry in zip(df["City"], df["Country"])
    ]

    # Outliers (1.5x IQR on PM2.5)
    df["Outlier_Flags_IQR"] = flag_outliers_iqr(df["PM2_5_2024_ugm3"])

    # Normalization
    df["PM2_5_2024_ugm3_norm"] = min_max_normalize(df["PM2_5_2024_ugm3"])

    return df


def process_tomtom(cities_ref: pd.DataFrame) -> pd.DataFrame:
    """Process TomTom raw data into standardized traffic dataset."""
    df = pd.read_csv(TOMTOM_RAW_PATH)
    df = df.drop_duplicates().copy()

    df["City_Raw"] = df["City_As_Published"]
    parsed = [parse_location_label(x) for x in df["City_Raw"]]
    df["City"] = [p[0] for p in parsed]
    df["State"] = [p[1] for p in parsed]
    df["Country"] = [p[2] for p in parsed]

    scope_set = set(zip(cities_ref["City"], cities_ref["Country"]))
    df["In_Project_Scope"] = [
        (c, cntry) in scope_set for c, cntry in zip(df["City"], df["Country"])
    ]

    # Outlier on Congestion_Level_2025_pct
    df["Outlier_Flags_IQR"] = flag_outliers_iqr(df["Congestion_Level_2025_pct"])

    # Normalization on Congestion_Level_2025_pct
    df["Congestion_Level_2025_pct_norm"] = min_max_normalize(df["Congestion_Level_2025_pct"])

    return df


def build_final_merged(
    numbeo_df: pd.DataFrame,
    iqair_df: pd.DataFrame,
    tomtom_df: pd.DataFrame,
    cities_ref: pd.DataFrame,
) -> pd.DataFrame:
    """Build final merged dataset of cities in scope with all derived metrics."""
    # Filter in-scope records
    num_scope = numbeo_df[numbeo_df["In_Project_Scope"]].drop(
        columns=["Rank", "In_Project_Scope", "Outlier_Flags_IQR", "City_Raw"], errors="ignore"
    )
    iq_scope = iqair_df[iqair_df["In_Project_Scope"]].drop(
        columns=["Rank", "In_Project_Scope", "Outlier_Flags_IQR", "City_Raw", "Source_Table"],
        errors="ignore",
    )
    tt_scope = tomtom_df[tomtom_df["In_Project_Scope"]].drop(
        columns=["In_Project_Scope", "Outlier_Flags_IQR", "City_Raw", "Source"], errors="ignore"
    )

    # Inner join Numbeo and IQAir on City + Country
    merged = pd.merge(
        num_scope,
        iq_scope.drop(columns=["State"], errors="ignore"),
        on=["City", "Country"],
        how="inner",
        suffixes=("", "_iqair"),
    )

    # Left join TomTom on City + Country
    merged = pd.merge(
        merged,
        tt_scope.drop(columns=["State"], errors="ignore"),
        on=["City", "Country"],
        how="left",
        suffixes=("", "_tomtom"),
    )

    # Join metadata from cities_reference (Region, Latitude, Longitude)
    merged = pd.merge(
        merged,
        cities_ref[["City", "Country", "Region", "Latitude", "Longitude"]],
        on=["City", "Country"],
        how="inner",
    )

    # Recompute norm columns on final merged set (SPEC requirement: norms on final set)
    merged["Local_Purchasing_Power_Index_norm"] = min_max_normalize(
        merged["Local_Purchasing_Power_Index"]
    )
    merged["PM2_5_2024_ugm3_norm"] = min_max_normalize(merged["PM2_5_2024_ugm3"])
    merged["Cost_of_Living_Index_norm"] = min_max_normalize(merged["Cost_of_Living_Index"])
    merged["Rent_Index_norm"] = min_max_normalize(merged["Rent_Index"])
    merged["Cost_of_Living_Plus_Rent_Index_norm"] = min_max_normalize(
        merged["Cost_of_Living_Plus_Rent_Index"]
    )
    merged["Groceries_Index_norm"] = min_max_normalize(merged["Groceries_Index"])
    merged["Restaurant_Price_Index_norm"] = min_max_normalize(merged["Restaurant_Price_Index"])

    # Traffic norm (for the non-null subset)
    if merged["Congestion_Level_2025_pct"].notna().any():
        traffic_norm = min_max_normalize(merged["Congestion_Level_2025_pct"])
        merged["Congestion_Level_2025_pct_norm"] = traffic_norm

    # Derived metrics
    # Relative_Net_Income_Index = LPP * Cost_of_Living_Plus_Rent / 100
    merged["Relative_Net_Income_Index"] = (
        merged["Local_Purchasing_Power_Index"]
        * merged["Cost_of_Living_Plus_Rent_Index"]
        / 100.0
    ).round(2)

    # PM2_5_x_WHO_Guideline = PM2.5 / 5
    merged["PM2_5_x_WHO_Guideline"] = (
        merged["PM2_5_2024_ugm3"] / WHO_ANNUAL_GUIDELINE
    ).round(2)

    # PM2_5_WHO_Band
    merged["PM2_5_WHO_Band"] = merged["PM2_5_2024_ugm3"].apply(assign_pm25_band)

    # Affordability_Air_Score_0_100 = 100 * (w1 * norm(LPP) + w2 * (1 - norm(PM2.5)))
    w1 = DEFAULT_WEIGHT_LPP
    w2 = DEFAULT_WEIGHT_PM25
    merged["Affordability_Air_Score_0_100"] = (
        100.0
        * (
            w1 * merged["Local_Purchasing_Power_Index_norm"]
            + w2 * (1.0 - merged["PM2_5_2024_ugm3_norm"])
        )
    ).round(2)

    # Sort deterministically
    merged = merged.sort_values(
        by="Affordability_Air_Score_0_100", ascending=False
    ).reset_index(drop=True)

    return merged


def run_pipeline() -> dict[str, pd.DataFrame]:
    """Run end-to-end preprocessing pipeline and save processed CSV files."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    cities_ref = load_and_clean_cities_ref()
    numbeo_df = process_numbeo(cities_ref)
    iqair_df = process_iqair(cities_ref)
    tomtom_df = process_tomtom(cities_ref)
    final_merged = build_final_merged(numbeo_df, iqair_df, tomtom_df, cities_ref)

    numbeo_df.to_csv(COST_OF_LIVING_PROCESSED_PATH, index=False)
    iqair_df.to_csv(AIR_QUALITY_PROCESSED_PATH, index=False)
    tomtom_df.to_csv(TRAFFIC_PROCESSED_PATH, index=False)
    final_merged.to_csv(FINAL_MERGED_PATH, index=False)

    return {
        "cost_of_living": numbeo_df,
        "air_quality": iqair_df,
        "traffic": tomtom_df,
        "final_merged": final_merged,
    }


if __name__ == "__main__":
    results = run_pipeline()
    print("=== Pipeline Execution Complete ===")
    print(f"Numbeo raw: {len(results['cost_of_living'])} | In scope: {results['cost_of_living']['In_Project_Scope'].sum()} | Outliers: {results['cost_of_living']['Outlier_Flags_IQR'].sum()}")
    print(f"IQAir raw: {len(results['air_quality'])} | In scope: {results['air_quality']['In_Project_Scope'].sum()} | Outliers: {results['air_quality']['Outlier_Flags_IQR'].sum()}")
    print(f"TomTom raw: {len(results['traffic'])} | In scope: {results['traffic']['In_Project_Scope'].sum()} | Outliers: {results['traffic']['Outlier_Flags_IQR'].sum()}")
    print(f"Final merged cities: {len(results['final_merged'])} | With congestion data: {results['final_merged']['Congestion_Level_2025_pct'].notna().sum()}")
