"""Analytical functions, what-if scoring, filtering, and summary statistics."""
import numpy as np
import pandas as pd


def recalculate_affordability_score(
    df: pd.DataFrame,
    w_lpp: float = 0.6,
    w_clean_air: float = 0.4,
) -> pd.DataFrame:
    """Recalculate the Affordability-Air Score with custom normalized weights.

    Score = 100 * (w_lpp_norm * norm(LPP) + w_air_norm * (1 - norm(PM2.5)))
    """
    total_w = w_lpp + w_clean_air
    if total_w <= 0:
        w1_norm = 0.5
        w2_norm = 0.5
    else:
        w1_norm = w_lpp / total_w
        w2_norm = w_clean_air / total_w

    out = df.copy()
    lpp_norm = out["Local_Purchasing_Power_Index_norm"]
    pm25_norm = out["PM2_5_2024_ugm3_norm"]

    score = 100.0 * (w1_norm * lpp_norm + w2_norm * (1.0 - pm25_norm))
    out["Custom_Score"] = score.round(2)
    out["Custom_Rank"] = out["Custom_Score"].rank(ascending=False, method="min").astype(int)
    return out.sort_values(by="Custom_Score", ascending=False).reset_index(drop=True)


def compute_correlation_matrix(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: str = "pearson",
) -> pd.DataFrame:
    """Compute Pearson or Spearman correlation matrix for numeric columns."""
    if columns is None:
        columns = [
            "Cost_of_Living_Index",
            "Rent_Index",
            "Cost_of_Living_Plus_Rent_Index",
            "Groceries_Index",
            "Restaurant_Price_Index",
            "Local_Purchasing_Power_Index",
            "PM2_5_2024_ugm3",
            "Relative_Net_Income_Index",
        ]
    existing = [c for c in columns if c in df.columns]
    return df[existing].corr(method=method).round(3)


def filter_dataset(
    df: pd.DataFrame,
    regions: list[str] | None = None,
    countries: list[str] | None = None,
    pm25_bands: list[str] | None = None,
    lpp_min: float | None = None,
    lpp_max: float | None = None,
    search_query: str | None = None,
) -> pd.DataFrame:
    """Apply dynamic multi-criteria filters to the merged dataset."""
    filtered = df.copy()

    if regions:
        filtered = filtered[filtered["Region"].isin(regions)]

    if countries:
        filtered = filtered[filtered["Country"].isin(countries)]

    if pm25_bands:
        filtered = filtered[filtered["PM2_5_WHO_Band"].isin(pm25_bands)]

    if lpp_min is not None:
        filtered = filtered[filtered["Local_Purchasing_Power_Index"] >= lpp_min]

    if lpp_max is not None:
        filtered = filtered[filtered["Local_Purchasing_Power_Index"] <= lpp_max]

    if search_query:
        query = search_query.strip().lower()
        filtered = filtered[
            filtered["City"].str.lower().str.contains(query)
            | filtered["Country"].str.lower().str.contains(query)
        ]

    return filtered


def get_regional_summary(df: pd.DataFrame, metric: str = "Local_Purchasing_Power_Index") -> pd.DataFrame:
    """Calculate summary statistics per region for a specified metric."""
    grouped = df.groupby("Region")[metric].agg(["count", "median", "mean", "min", "max", "std"])
    return grouped.round(2).reset_index()


def get_city_comparison_table(df: pd.DataFrame, cities: list[str]) -> pd.DataFrame:
    """Return selected cities transposed for side-by-side comparison."""
    subset = df[df["City"].isin(cities)].copy()
    display_cols = [
        "City",
        "Country",
        "Region",
        "Affordability_Air_Score_0_100",
        "Local_Purchasing_Power_Index",
        "Cost_of_Living_Index",
        "Rent_Index",
        "PM2_5_2024_ugm3",
        "PM2_5_WHO_Band",
        "PM2_5_x_WHO_Guideline",
        "Relative_Net_Income_Index",
        "Congestion_Level_2025_pct",
    ]
    cols = [c for c in display_cols if c in subset.columns]
    table = subset[cols].set_index("City").T
    return table
