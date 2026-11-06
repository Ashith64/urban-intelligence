"""Automated data-driven statistical insight generator.

All metrics, insights, and rankings are calculated dynamically from data;
no figures or takeaways are hardcoded.
"""
import pandas as pd
from src.config import WHO_ANNUAL_GUIDELINE


def calculate_home_kpis(df: pd.DataFrame) -> dict:
    """Calculate executive high-level KPIs for the homepage."""
    total_cities = len(df)
    total_countries = df["Country"].nunique()
    median_lpp = float(df["Local_Purchasing_Power_Index"].median())
    median_pm25 = float(df["PM2_5_2024_ugm3"].median())
    above_who = (df["PM2_5_2024_ugm3"] > WHO_ANNUAL_GUIDELINE).mean() * 100.0

    return {
        "total_cities": total_cities,
        "total_countries": total_countries,
        "median_lpp": round(median_lpp, 1),
        "median_pm25": round(median_pm25, 1),
        "share_above_who_pct": round(above_who, 1),
    }


def generate_automated_insights(df: pd.DataFrame) -> dict:
    """Generate dynamic textual and statistical findings from the merged dataset."""
    # Top and bottom performers by score
    top_score_city = df.sort_values(by="Affordability_Air_Score_0_100", ascending=False).iloc[0]
    bottom_score_city = df.sort_values(by="Affordability_Air_Score_0_100", ascending=True).iloc[0]

    # Cleanest and most polluted cities
    cleanest_city = df.sort_values(by="PM2_5_2024_ugm3", ascending=True).iloc[0]
    most_polluted_city = df.sort_values(by="PM2_5_2024_ugm3", ascending=False).iloc[0]

    # Highest and lowest purchasing power
    max_lpp_city = df.sort_values(by="Local_Purchasing_Power_Index", ascending=False).iloc[0]
    min_lpp_city = df.sort_values(by="Local_Purchasing_Power_Index", ascending=True).iloc[0]

    # WHO guideline compliance
    meets_who = df[df["PM2_5_2024_ugm3"] <= WHO_ANNUAL_GUIDELINE]
    meets_who_count = len(meets_who)
    meets_who_pct = round((meets_who_count / len(df)) * 100.0, 1)

    # Regional medians
    reg_pm25 = df.groupby("Region")["PM2_5_2024_ugm3"].median().sort_values()
    cleanest_region = reg_pm25.index[0]
    cleanest_reg_val = round(float(reg_pm25.iloc[0]), 1)
    highest_polluted_reg = reg_pm25.index[-1]
    polluted_reg_val = round(float(reg_pm25.iloc[-1]), 1)

    reg_lpp = df.groupby("Region")["Local_Purchasing_Power_Index"].median().sort_values(ascending=False)
    wealthiest_region = reg_lpp.index[0]
    wealthiest_reg_val = round(float(reg_lpp.iloc[0]), 1)

    # Correlation highlights
    numeric_cols = [
        "Cost_of_Living_Index",
        "Rent_Index",
        "Cost_of_Living_Plus_Rent_Index",
        "Groceries_Index",
        "Restaurant_Price_Index",
        "Local_Purchasing_Power_Index",
        "PM2_5_2024_ugm3",
        "Relative_Net_Income_Index",
    ]
    corr = df[numeric_cols].corr(method="pearson")

    # Find highest positive off-diagonal correlation
    corr_unstacked = corr.unstack()
    corr_unstacked = corr_unstacked[corr_unstacked < 0.999]  # ignore self-correlation
    strongest_pos_pair = corr_unstacked.idxmax()
    strongest_pos_val = round(float(corr_unstacked.max()), 3)

    strongest_neg_pair = corr_unstacked.idxmin()
    strongest_neg_val = round(float(corr_unstacked.min()), 3)

    # Traffic data coverage
    traffic_subset = df[df["Congestion_Level_2025_pct"].notna()]
    traffic_count = len(traffic_subset)
    if traffic_count > 0:
        worst_traffic = traffic_subset.sort_values(by="Congestion_Level_2025_pct", ascending=False).iloc[0]
        worst_traffic_city = f"{worst_traffic['City']} ({worst_traffic['Congestion_Level_2025_pct']}%)"
    else:
        worst_traffic_city = "N/A"

    return {
        "top_score_city": {
            "name": top_score_city["City"],
            "country": top_score_city["Country"],
            "score": top_score_city["Affordability_Air_Score_0_100"],
            "lpp": top_score_city["Local_Purchasing_Power_Index"],
            "pm25": top_score_city["PM2_5_2024_ugm3"],
        },
        "bottom_score_city": {
            "name": bottom_score_city["City"],
            "country": bottom_score_city["Country"],
            "score": bottom_score_city["Affordability_Air_Score_0_100"],
        },
        "cleanest_city": {
            "name": cleanest_city["City"],
            "country": cleanest_city["Country"],
            "pm25": cleanest_city["PM2_5_2024_ugm3"],
        },
        "most_polluted_city": {
            "name": most_polluted_city["City"],
            "country": most_polluted_city["Country"],
            "pm25": most_polluted_city["PM2_5_2024_ugm3"],
        },
        "max_lpp_city": {
            "name": max_lpp_city["City"],
            "country": max_lpp_city["Country"],
            "lpp": max_lpp_city["Local_Purchasing_Power_Index"],
        },
        "min_lpp_city": {
            "name": min_lpp_city["City"],
            "country": min_lpp_city["Country"],
            "lpp": min_lpp_city["Local_Purchasing_Power_Index"],
        },
        "meets_who_count": meets_who_count,
        "meets_who_pct": meets_who_pct,
        "cleanest_region": (cleanest_region, cleanest_reg_val),
        "most_polluted_region": (highest_polluted_reg, polluted_reg_val),
        "wealthiest_region": (wealthiest_region, wealthiest_reg_val),
        "strongest_pos_corr": (strongest_pos_pair, strongest_pos_val),
        "strongest_neg_corr": (strongest_neg_pair, strongest_neg_val),
        "traffic_coverage": traffic_count,
        "worst_traffic_city": worst_traffic_city,
    }
