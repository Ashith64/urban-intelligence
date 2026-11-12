"""Data loader module for the Global Urban Intelligence Platform with Streamlit caching."""
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
MASTER_DATASET_PATH = PROCESSED_DATA_DIR / "global_urban_master.csv"
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
QOL_RAW_PATH = RAW_DATA_DIR / "quality_of_life_raw.csv"

from src.pipeline import run_pipeline


@st.cache_data
def get_master_data() -> pd.DataFrame:
    """Load the comprehensive 238-city master dataset with all normalized & derived metrics."""
    if not MASTER_DATASET_PATH.exists():
        run_pipeline()
    return pd.read_csv(MASTER_DATASET_PATH)


@st.cache_data
def get_final_merged_data() -> pd.DataFrame:
    """Alias for backwards compatibility with existing views."""
    return get_master_data()


@st.cache_data
def get_raw_dataset() -> pd.DataFrame:
    """Load the raw quality of life and affordability dataset."""
    if not QOL_RAW_PATH.exists():
        from src.fetch_data import fetch_quality_of_life_data
        return fetch_quality_of_life_data()
    return pd.read_csv(QOL_RAW_PATH)
