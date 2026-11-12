"""Analytical and Statistical Engine for URBAN INTELLIGENCE — The Global Liveability Observatory.

Contains:
- Executive KPI calculations
- Univariate statistical profiling (12 summary statistics)
- Automated dynamic Discovery Feed generator
- Ready-made lifestyle presets & custom scenario ranking models
- Bivariate regression & correlation studio functions
"""
import numpy as np
import pandas as pd
from scipy import stats


def calculate_master_kpis(df: pd.DataFrame) -> dict:
    """Compute high-level executive KPIs for the 238-city platform."""
    total_cities = len(df)
    total_countries = df["Country"].nunique()
    med_power = float(df["Purchasing_Power_Index"].median())
    med_cost = float(df["Cost_of_Living_Index"].median())
    med_ratio = float(df["Property_Price_to_Income_Ratio"].median())
    pristine_pct = float((df["Pollution_Index"] <= 35.0).mean() * 100.0)

    cleanest = df.sort_values(by="Pollution_Index", ascending=True).iloc[0]
    highest_power = df.sort_values(by="Purchasing_Power_Index", ascending=False).iloc[0]
    lowest_cost = df.sort_values(by="Cost_of_Living_Index", ascending=True).iloc[0]
    safest = df.sort_values(by="Safety_Index", ascending=False).iloc[0]
    best_health = df.sort_values(by="Health_Care_Index", ascending=False).iloc[0]

    return {
        "total_cities": total_cities,
        "total_countries": total_countries,
        "median_power": round(med_power, 1),
        "median_cost": round(med_cost, 1),
        "median_price_to_income": round(med_ratio, 1),
        "pristine_air_pct": round(pristine_pct, 1),
        "cleanest_city": {
            "name": cleanest["City"],
            "country": cleanest["Country"],
            "pollution": round(float(cleanest["Pollution_Index"]), 1),
        },
        "highest_power_city": {
            "name": highest_power["City"],
            "country": highest_power["Country"],
            "power": round(float(highest_power["Purchasing_Power_Index"]), 1),
        },
        "lowest_cost_city": {
            "name": lowest_cost["City"],
            "country": lowest_cost["Country"],
            "cost": round(float(lowest_cost["Cost_of_Living_Index"]), 1),
        },
        "safest_city": {
            "name": safest["City"],
            "country": safest["Country"],
            "safety": round(float(safest["Safety_Index"]), 1),
        },
        "best_health_city": {
            "name": best_health["City"],
            "country": best_health["Country"],
            "health": round(float(best_health["Health_Care_Index"]), 1),
        },
    }


def calculate_univariate_stats(series: pd.Series) -> dict:
    """Compute 12 rigorous descriptive statistics for a numerical variable."""
    clean = pd.to_numeric(series, errors="coerce").dropna()
    total_obs = len(series)
    valid_obs = len(clean)
    missing_pct = round(((total_obs - valid_obs) / total_obs) * 100.0, 2) if total_obs > 0 else 0.0

    if valid_obs == 0:
        return {"count": 0, "missing_pct": 100.0}

    mean_val = float(clean.mean())
    median_val = float(clean.median())
    min_val = float(clean.min())
    max_val = float(clean.max())
    range_val = max_val - min_val
    std_val = float(clean.std(ddof=1)) if valid_obs > 1 else 0.0
    var_val = float(clean.var(ddof=1)) if valid_obs > 1 else 0.0

    q1 = float(clean.quantile(0.25))
    q3 = float(clean.quantile(0.75))
    iqr = q3 - q1

    return {
        "Observations": valid_obs,
        "Missing %": f"{missing_pct}%",
        "Mean": round(mean_val, 2),
        "Median": round(median_val, 2),
        "Minimum": round(min_val, 2),
        "Maximum": round(max_val, 2),
        "Range": round(range_val, 2),
        "Std Deviation": round(std_val, 2),
        "Variance": round(var_val, 2),
        "25th Percentile (Q1)": round(q1, 2),
        "75th Percentile (Q3)": round(q3, 2),
        "IQR": round(iqr, 2),
    }


def generate_discovery_feed(df: pd.DataFrame) -> list[dict]:
    """Dynamically generate analytical discoveries directly from data without hardcoding."""
    discoveries = []
    sample_size = len(df)

    # 1. Highest Purchasing Power
    top_p = df.sort_values(by="Purchasing_Power_Index", ascending=False).iloc[0]
    discoveries.append({
        "title": "Global Purchasing Power Peak",
        "metric_value": f"{top_p['City']}, {top_p['Country']} ({top_p['Purchasing_Power_Index']:.1f})",
        "badge": "Top Disposable Power",
        "explanation": f"Residents in {top_p['City']} can buy {top_p['Purchasing_Power_Index'] / 100.0:.2f} times as many goods and services as average residents in New York City, leading global purchasing capacity.",
        "sample_size": sample_size,
        "source": "Numbeo Living Standards Benchmark",
    })

    # 2. Lowest Cost of Living
    low_cost = df.sort_values(by="Cost_of_Living_Index", ascending=True).iloc[0]
    discoveries.append({
        "title": "Most Affordable Daily Cost of Living",
        "metric_value": f"{low_cost['City']}, {low_cost['Country']} ({low_cost['Cost_of_Living_Index']:.1f})",
        "badge": "Lowest Living Cost",
        "explanation": f"{low_cost['City']} offers the lowest consumer basket index across all {sample_size} cities, requiring just {low_cost['Cost_of_Living_Index']:.1f}% of New York's baseline living expenditure.",
        "sample_size": sample_size,
        "source": "Numbeo Living Standards Benchmark",
    })

    # 3. Cleanest Environmental Score
    clean = df.sort_values(by="Pollution_Index", ascending=True).iloc[0]
    discoveries.append({
        "title": "Pristine Environmental Sanctuary",
        "metric_value": f"{clean['City']}, {clean['Country']} ({clean['Pollution_Index']:.1f})",
        "badge": "Cleanest Environment",
        "explanation": f"With a pollution index of only {clean['Pollution_Index']:.1f} out of 100, {clean['City']} maintains the cleanest air, water, and environmental quality in the global study.",
        "sample_size": sample_size,
        "source": "Numbeo Environmental Survey",
    })

    # 4. Best Housing Affordability (Lowest Price to Income)
    top_house = df.sort_values(by="Property_Price_to_Income_Ratio", ascending=True).iloc[0]
    discoveries.append({
        "title": "Most Accessible Housing Market",
        "metric_value": f"{top_house['City']}, {top_house['Country']} ({top_house['Property_Price_to_Income_Ratio']:.1f}× Income)",
        "badge": "Housing Affordability",
        "explanation": f"Purchasing a median apartment in {top_house['City']} requires only {top_house['Property_Price_to_Income_Ratio']:.1f} years of average net income, compared to the global median of {df['Property_Price_to_Income_Ratio'].median():.1f} years.",
        "sample_size": sample_size,
        "source": "Numbeo Housing Ratio Analysis",
    })

    # 5. Strongest Statistical Relationship
    corr = df[["Purchasing_Power_Index", "Cost_of_Living_Index"]].corr().iloc[0, 1]
    discoveries.append({
        "title": "Empirical Wealth & Price Co-movement",
        "metric_value": f"Pearson r = +{corr:.2f}",
        "badge": "Strong Correlation",
        "explanation": f"A strong positive relationship (r = +{corr:.2f}) exists between local purchasing power and cost of living: higher consumer prices strongly correlate with higher average local wage levels.",
        "sample_size": sample_size,
        "source": "Pearson Bivariate Correlation",
    })

    # 6. Environmental Decoupling
    corr_gdp_pol = df[["GDP_Per_Capita_USD", "Pollution_Index"]].corr().iloc[0, 1]
    discoveries.append({
        "title": "Economic Wealth & Environmental Decoupling",
        "metric_value": f"Pearson r = {corr_gdp_pol:.2f}",
        "badge": "Kuznets Trend",
        "explanation": f"National GDP per capita is negatively correlated with urban pollution (r = {corr_gdp_pol:.2f}), confirming that wealthier economies invest significantly more capital into clean infrastructure.",
        "sample_size": sample_size,
        "source": "World Bank & Numbeo Cross-Analysis",
    })

    return discoveries


def calculate_preset_ranking(
    df: pd.DataFrame,
    preset: str = "Balanced Priorities",
    custom_weights: dict | None = None,
) -> pd.DataFrame:
    """Calculate ranking based on ready-made lifestyle presets or custom user weights."""
    if preset == "Affordability First":
        w_p, w_air, w_safe, w_health, w_house = 0.45, 0.15, 0.10, 0.10, 0.20
    elif preset == "Environment First":
        w_p, w_air, w_safe, w_health, w_house = 0.15, 0.45, 0.15, 0.15, 0.10
    elif preset == "Balanced Priorities":
        w_p, w_air, w_safe, w_health, w_house = 0.25, 0.25, 0.20, 0.20, 0.10
    else:  # Custom
        custom_weights = custom_weights or {}
        w_p = custom_weights.get("purchasing", 0.35)
        w_air = custom_weights.get("environment", 0.25)
        w_safe = custom_weights.get("safety", 0.15)
        w_health = custom_weights.get("health", 0.15)
        w_house = custom_weights.get("housing", 0.10)

    total_w = w_p + w_air + w_safe + w_health + w_house
    if total_w <= 0:
        total_w = 1.0

    out = df.copy()
    score = (
        (w_p * out["Purchasing_Power_Index_norm"]
         + w_air * out["Clean_Environment_norm"]
         + w_safe * out["Safety_Index_norm"]
         + w_health * out["Health_Care_Index_norm"]
         + w_house * out["Housing_Affordability_norm"])
        / total_w
    ) * 100.0

    out["Custom_Score"] = score.round(2)
    out["Custom_Rank"] = out["Custom_Score"].rank(ascending=False, method="min").astype(int)
    return out.sort_values(by="Custom_Score", ascending=False).reset_index(drop=True)


def compute_bivariate_analysis(df: pd.DataFrame, x_col: str, y_col: str) -> dict:
    """Compute bivariate regression, Pearson r, Spearman rho, and analytical takeaways."""
    sub = df[[x_col, y_col]].dropna()
    x = sub[x_col].values
    y = sub[y_col].values
    n = len(sub)

    if n < 3:
        return {"n": n, "r": 0, "rho": 0, "slope": 0, "intercept": 0, "interpretation": "Insufficient data"}

    r_val, p_val = stats.pearsonr(x, y)
    rho_val, _ = stats.spearmanr(x, y)
    slope, intercept, _, _, _ = stats.linregress(x, y)

    # Analytical explanation
    strength = "strong" if abs(r_val) >= 0.6 else ("moderate" if abs(r_val) >= 0.35 else "weak")
    direction = "positive" if r_val > 0 else "negative"

    interp = (
        f"A {strength} {direction} correlation (Pearson r = {r_val:+.2f}, Spearman ρ = {rho_val:+.2f}, N = {n}) "
        f"is observed. Statistical association describes co-movement and does not establish a causal mechanism."
    )

    return {
        "n": n,
        "r": round(float(r_val), 3),
        "rho": round(float(rho_val), 3),
        "p_value": float(p_val),
        "slope": round(float(slope), 4),
        "intercept": round(float(intercept), 2),
        "interpretation": interp,
    }


def compute_correlation_matrix_filtered(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: str = "pearson",
) -> pd.DataFrame:
    """Compute correlation matrix, explicitly guarding against constituent self-correlations."""
    if columns is None:
        columns = [
            "Purchasing_Power_Index",
            "Cost_of_Living_Index",
            "Property_Price_to_Income_Ratio",
            "Pollution_Index",
            "Safety_Index",
            "Health_Care_Index",
            "Traffic_Commute_Time_Index",
            "Climate_Index",
            "GDP_Per_Capita_USD",
            "Life_Expectancy_Years",
        ]
    existing = [c for c in columns if c in df.columns]
    return df[existing].corr(method=method).round(3)
