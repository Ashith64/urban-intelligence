"""World Bank macro-economic indicator integration for BISL504.

Provides GDP per capita (USD), Life Expectancy (years), and Urban Population (%)
downloaded directly from the World Bank Open Data API with local caching.
"""
from pathlib import Path
import pandas as pd
import streamlit as st

from src.config import PROCESSED_DATA_DIR
from src.data_loader import get_final_merged_data

COUNTRY_MACRO_PATH = PROCESSED_DATA_DIR / "country_macro.csv"

# Alias dictionary to harmonize country names between our dataset and World Bank
WB_COUNTRY_ALIASES = {
    "South Korea": "Korea, Rep.",
    "Czech Republic": "Czechia",
    "Hong Kong": "Hong Kong SAR, China",
    "Slovakia": "Slovak Republic",
    "Russia": "Russian Federation",
    "Vietnam": "Viet Nam",
    "Egypt": "Egypt, Arab Rep.",
}


@st.cache_data
def get_country_macro_data() -> pd.DataFrame:
    """Load cached World Bank macro indicators."""
    if not COUNTRY_MACRO_PATH.exists():
        # Fallback empty dataframe with schema if not yet created
        return pd.DataFrame(columns=[
            "country_code", "country_name", "GDP_Per_Capita_USD",
            "Life_Expectancy_Years", "Urban_Population_Pct"
        ])
    return pd.read_csv(COUNTRY_MACRO_PATH)


@st.cache_data
def get_cities_with_macro_data() -> pd.DataFrame:
    """Merge final city dataset with World Bank country macro indicators."""
    city_df = get_final_merged_data().copy()
    wb_df = get_country_macro_data().copy()

    # Apply WB alias
    city_df["_wb_country"] = city_df["Country"].map(lambda c: WB_COUNTRY_ALIASES.get(c, c))

    merged = pd.merge(
        city_df,
        wb_df[["country_name", "GDP_Per_Capita_USD", "Life_Expectancy_Years", "Urban_Population_Pct"]],
        left_on="_wb_country",
        right_on="country_name",
        how="left",
    )
    merged.drop(columns=["_wb_country", "country_name"], errors="ignore", inplace=True)
    return merged
