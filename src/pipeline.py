"""Data preprocessing and integration pipeline for BISL504."""

from __future__ import annotations

import unicodedata
from typing import Iterable

import numpy as np
import pandas as pd

from src.config import (
    CITY_ALIASES,
    COUNTRY_ALIASES,
    DATA_PROCESSED_DIR,
    DEFAULT_WEIGHT_AIR,
    DEFAULT_WEIGHT_LPP,
    FINAL_MERGED_PATH,
    IQAIR_NUMERIC_COLS,
    NUMBEO_NUMERIC_COLS,
    PROCESSED_AQ_PATH,
    PROCESSED_COL_PATH,
    PROCESSED_TRAFFIC_PATH,
    RAW_CITIES_REF_PATH,
    RAW_IQAIR_PATH,
    RAW_NUMBEO_PATH,
    RAW_TOMTOM_PATH,
    TOMTOM_CC_MAP,
    TOMTOM_NUMERIC_COLS,
    WHO_PM25_GUIDELINE,
)


def strip_accents(text: str | float) -> str | float:
    """Strip diacritical accents and trim whitespace from string values."""
    if not isinstance(text, str):
        return text
    normalized = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    return stripped.strip()


def parse_city_label(label: str, country_map: dict[str, str] | None = None) -> tuple[str, str | None, str]:
    """Parse 'City, [State,] Country' into standardized (City, State, Country)."""
    parts = [strip_accents(p) for p in str(label).split(",")]
    city_raw = parts[0]
    state = parts[1] if len(parts) == 3 else None
    country_raw = parts[-1] if len(parts) >= 2 else ""

    city = CITY_ALIASES.get(city_raw, city_raw)
    if country_map and country_raw in country_map:
        country_raw = country_map[country_raw]
    country = COUNTRY_ALIASES.get(country_raw, country_raw)
    return city, state, country


def flag_iqr_outliers(df: pd.DataFrame, cols: Iterable[str]) -> pd.Series:
    """Flag rows outside 1.5 * IQR for any specified column; returns comma-separated col names."""
    flags = pd.Series("", index=df.index, dtype="object")
    for col in cols:
        series = df[col].dropna()
        if series.empty:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        is_out = (df[col] < lower) | (df[col] > upper)
        flags = np.where(is_out, np.where(flags == "", col, flags + ", " + col), flags)
    return pd.Series(flags, index=df.index, dtype="object")


def add_minmax_norm(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """Add Min-Max normalized `<col>_norm` columns bounded in [0, 1], preserving NaNs."""
    out = df.copy()
    for col in cols:
        s = out[col]
        min_val = s.min(skipna=True)
        max_val = s.max(skipna=True)
        if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
            out[f"{col}_norm"] = np.where(s.notna(), 0.0, np.nan)
        else:
            out[f"{col}_norm"] = (s - min_val) / (max_val - min_val)
    return out


def classify_who_band(pm25: float) -> str:
    """Classify PM2.5 (ug/m3) into WHO 2021 Air Quality Guideline / Interim Target bands."""
    if pm25 <= 5.0:
        return "Meets guideline"
    if pm25 <= 10.0:
        return "Interim 4"
    if pm25 <= 15.0:
        return "Interim 3"
    if pm25 <= 25.0:
        return "Interim 2"
    if pm25 <= 35.0:
        return "Interim 1"
    return "Above interim targets"


def load_reference_cities() -> pd.DataFrame:
    """Load and standardize the authoritative cities reference table."""
    ref = pd.read_csv(RAW_CITIES_REF_PATH)
    ref["City"] = ref["City"].apply(strip_accents)
    ref["Country"] = ref["Country"].apply(strip_accents)
    return ref.drop_duplicates(subset=["City", "Country"]).reset_index(drop=True)


def process_numbeo(ref_pairs: set[tuple[str, str]]) -> pd.DataFrame:
    """Clean, standardize, flag outliers, and scope-check Numbeo raw data."""
    df = pd.read_csv(RAW_NUMBEO_PATH)
    df = df.rename(
        columns={
            "City": "Raw_Label",
            "Cost of Living Index": "Cost_of_Living_Index",
            "Rent Index": "Rent_Index",
            "Cost of Living Plus Rent Index": "Cost_of_Living_Plus_Rent_Index",
            "Groceries Index": "Groceries_Index",
            "Restaurant Price Index": "Restaurant_Price_Index",
            "Local Purchasing Power Index": "Local_Purchasing_Power_Index",
        }
    )
    parsed = df["Raw_Label"].apply(lambda x: parse_city_label(x))
    df["City"] = parsed.apply(lambda t: t[0])
    df["State"] = parsed.apply(lambda t: t[1])
    df["Country"] = parsed.apply(lambda t: t[2])
    df = df.drop_duplicates(subset=["City", "State", "Country"]).reset_index(drop=True)

    df["Outlier_Flags_IQR"] = flag_iqr_outliers(df, NUMBEO_NUMERIC_COLS)
    df = add_minmax_norm(df, NUMBEO_NUMERIC_COLS)

    in_scope = [
        (c, cnt) in ref_pairs and not (c == "Portland" and st != "OR")
        for c, st, cnt in zip(df["City"], df["State"], df["Country"])
    ]
    df["In_Project_Scope"] = in_scope
    return df


def process_iqair(ref_pairs: set[tuple[str, str]]) -> pd.DataFrame:
    """Clean, standardize, flag outliers, and scope-check IQAir raw data."""
    df = pd.read_csv(RAW_IQAIR_PATH)
    df = df.rename(columns={"City_As_Published": "Raw_Label"})
    parsed = df["Raw_Label"].apply(lambda x: parse_city_label(x))
    df["City"] = parsed.apply(lambda t: t[0])
    df["State"] = parsed.apply(lambda t: t[1])
    df["Country"] = parsed.apply(lambda t: t[2])
    df = df.drop_duplicates(subset=["City", "Country"]).reset_index(drop=True)

    df["Outlier_Flags_IQR"] = flag_iqr_outliers(df, IQAIR_NUMERIC_COLS)
    df = add_minmax_norm(df, IQAIR_NUMERIC_COLS)
    df["In_Project_Scope"] = [
        (c, cnt) in ref_pairs for c, cnt in zip(df["City"], df["Country"])
    ]
    return df


def process_tomtom(ref_pairs: set[tuple[str, str]]) -> pd.DataFrame:
    """Clean, standardize, flag congestion outliers, and scope-check TomTom raw data."""
    df = pd.read_csv(RAW_TOMTOM_PATH)
    df = df.rename(columns={"City_As_Published": "Raw_Label"})
    parsed = df["Raw_Label"].apply(lambda x: parse_city_label(x, country_map=TOMTOM_CC_MAP))
    df["City"] = parsed.apply(lambda t: t[0])
    df["State"] = parsed.apply(lambda t: t[1])
    df["Country"] = parsed.apply(lambda t: t[2])
    df = df.drop_duplicates(subset=["City", "Country"]).reset_index(drop=True)

    # Check congestion outliers per SPEC section 4 (Congestion_Level_2025_pct -> 0 outliers)
    df["Outlier_Flags_IQR"] = flag_iqr_outliers(df, ["Congestion_Level_2025_pct"])
    df = add_minmax_norm(df, TOMTOM_NUMERIC_COLS)
    df["In_Project_Scope"] = [
        (c, cnt) in ref_pairs for c, cnt in zip(df["City"], df["Country"])
    ]
    return df


def build_final_merged(
    numbeo_df: pd.DataFrame,
    iqair_df: pd.DataFrame,
    tomtom_df: pd.DataFrame,
    ref_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge in-scope sources and compute final normalized & derived metrics."""
    n_scope = numbeo_df[numbeo_df["In_Project_Scope"]].copy()
    i_scope = iqair_df[iqair_df["In_Project_Scope"]].copy()
    t_scope = tomtom_df[tomtom_df["In_Project_Scope"]].copy()

    # Keep core columns before merging to avoid duplicate suffix clutter
    n_cols = ["City", "Country", "State", "Raw_Label", "Outlier_Flags_IQR"] + NUMBEO_NUMERIC_COLS
    n_sub = n_scope[n_cols].rename(
        columns={"Raw_Label": "Numbeo_Raw_Label", "Outlier_Flags_IQR": "Numbeo_Outlier_Flags_IQR"}
    )

    i_cols = ["City", "Country", "Raw_Label", "Source_Table", "Outlier_Flags_IQR"] + IQAIR_NUMERIC_COLS
    i_sub = i_scope[i_cols].rename(
        columns={"Raw_Label": "IQAir_Raw_Label", "Outlier_Flags_IQR": "IQAir_Outlier_Flags_IQR"}
    )

    t_cols = ["City", "Country", "Raw_Label", "Source", "Outlier_Flags_IQR"] + TOMTOM_NUMERIC_COLS
    t_sub = t_scope[t_cols].rename(
        columns={
            "Raw_Label": "TomTom_Raw_Label",
            "Source": "TomTom_Source",
            "Outlier_Flags_IQR": "TomTom_Outlier_Flags_IQR",
        }
    )

    merged = pd.merge(n_sub, i_sub, on=["City", "Country"], how="inner")
    merged = pd.merge(merged, t_sub, on=["City", "Country"], how="left")
    merged = pd.merge(merged, ref_df, on=["City", "Country"], how="left")

    # Compute Min-Max norms strictly on the final merged set
    merged = add_minmax_norm(
        merged, NUMBEO_NUMERIC_COLS + IQAIR_NUMERIC_COLS + TOMTOM_NUMERIC_COLS
    )

    # Derived metrics per SPEC section 3
    merged["Relative_Net_Income_Index"] = (
        merged["Local_Purchasing_Power_Index"]
        * merged["Cost_of_Living_Plus_Rent_Index"]
        / 100.0
    )
    merged["PM2_5_x_WHO_Guideline"] = merged["PM2_5_2024_ugm3"] / WHO_PM25_GUIDELINE
    merged["PM2_5_WHO_Band"] = merged["PM2_5_2024_ugm3"].apply(classify_who_band)
    merged["Affordability_Air_Score_0_100"] = 100.0 * (
        DEFAULT_WEIGHT_LPP * merged["Local_Purchasing_Power_Index_norm"]
        + DEFAULT_WEIGHT_AIR * (1.0 - merged["PM2_5_2024_ugm3_norm"])
    )

    merged = merged.sort_values(
        by="Affordability_Air_Score_0_100", ascending=False
    ).reset_index(drop=True)
    return merged


def run_pipeline() -> dict[str, pd.DataFrame]:
    """Execute full ETL pipeline and persist processed CSV files."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ref_df = load_reference_cities()
    ref_pairs = set(zip(ref_df["City"], ref_df["Country"]))

    numbeo_df = process_numbeo(ref_pairs)
    iqair_df = process_iqair(ref_pairs)
    tomtom_df = process_tomtom(ref_pairs)
    final_df = build_final_merged(numbeo_df, iqair_df, tomtom_df, ref_df)

    numbeo_df.to_csv(PROCESSED_COL_PATH, index=False)
    iqair_df.to_csv(PROCESSED_AQ_PATH, index=False)
    tomtom_df.to_csv(PROCESSED_TRAFFIC_PATH, index=False)
    final_df.to_csv(FINAL_MERGED_PATH, index=False)

    return {
        "numbeo": numbeo_df,
        "iqair": iqair_df,
        "tomtom": tomtom_df,
        "final": final_df,
    }


if __name__ == "__main__":
    results = run_pipeline()
    print(
        f"Pipeline completed: Numbeo={len(results['numbeo'])} "
        f"(in scope={results['numbeo']['In_Project_Scope'].sum()}), "
        f"IQAir={len(results['iqair'])} "
        f"(in scope={results['iqair']['In_Project_Scope'].sum()}), "
        f"TomTom={len(results['tomtom'])} "
        f"(in scope={results['tomtom']['In_Project_Scope'].sum()}), "
        f"Final={len(results['final'])}"
    )
