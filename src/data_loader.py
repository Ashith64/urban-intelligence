"""Data loader module for BISL504 with Streamlit caching and graceful fallbacks."""
from pathlib import Path
import pandas as pd
import streamlit as st

from src.config import (
    NUMBEO_RAW_PATH,
    IQAIR_RAW_PATH,
    TOMTOM_RAW_PATH,
    CITIES_REF_PATH,
    COST_OF_LIVING_PROCESSED_PATH,
    AIR_QUALITY_PROCESSED_PATH,
    TRAFFIC_PROCESSED_PATH,
    FINAL_MERGED_PATH,
)
from src.pipeline import run_pipeline


@st.cache_data
def get_final_merged_data() -> pd.DataFrame:
    """Load the final merged dataset, executing pipeline if needed."""
    if not FINAL_MERGED_PATH.exists():
        run_pipeline()
    return pd.read_csv(FINAL_MERGED_PATH)


@st.cache_data
def get_cost_of_living_data() -> pd.DataFrame:
    """Load processed cost of living dataset."""
    if not COST_OF_LIVING_PROCESSED_PATH.exists():
        run_pipeline()
    return pd.read_csv(COST_OF_LIVING_PROCESSED_PATH)


@st.cache_data
def get_air_quality_data() -> pd.DataFrame:
    """Load processed air quality dataset."""
    if not AIR_QUALITY_PROCESSED_PATH.exists():
        run_pipeline()
    return pd.read_csv(AIR_QUALITY_PROCESSED_PATH)


@st.cache_data
def get_traffic_data() -> pd.DataFrame:
    """Load processed traffic dataset."""
    if not TRAFFIC_PROCESSED_PATH.exists():
        run_pipeline()
    return pd.read_csv(TRAFFIC_PROCESSED_PATH)


@st.cache_data
def get_cities_ref_data() -> pd.DataFrame:
    """Load cities reference scope dataset."""
    return pd.read_csv(CITIES_REF_PATH)


@st.cache_data
def get_raw_datasets() -> dict[str, pd.DataFrame]:
    """Load all four original raw datasets."""
    return {
        "numbeo_raw": pd.read_csv(NUMBEO_RAW_PATH),
        "iqair_raw": pd.read_csv(IQAIR_RAW_PATH),
        "tomtom_raw": pd.read_csv(TOMTOM_RAW_PATH),
        "cities_ref": pd.read_csv(CITIES_REF_PATH),
    }
