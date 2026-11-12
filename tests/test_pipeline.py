"""Validation and regression tests for the Global Urban Intelligence platform pipeline."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data_loader import get_master_data, get_raw_dataset
from src.pipeline import (
    run_pipeline,
    strip_accents,
    parse_location_string,
    min_max_normalize,
    validate_normalized_columns,
)


@pytest.fixture(scope="session")
def master_df():
    """Load or generate the master global dataset."""
    return get_master_data()


def test_raw_dataset_integrity():
    """Verify raw quality of life dataset is downloaded, non-empty, and has expected schema."""
    raw_df = get_raw_dataset()
    assert len(raw_df) == 238, f"Expected 238 cities in raw dataset, found {len(raw_df)}"
    expected_cols = [
        "City",
        "Quality of Life Index",
        "Purchasing Power Index",
        "Safety Index",
        "Health Care Index",
        "Cost of Living Index",
        "Property Price to Income Ratio",
        "Traffic Commute Time Index",
        "Pollution Index",
        "Climate Index",
    ]
    for col in expected_cols:
        assert col in raw_df.columns, f"Missing column in raw dataset: {col}"


def test_master_dataset_dimensions(master_df):
    """Verify master dataset contains 238 cities and no duplicate (City, Country) pairs."""
    assert len(master_df) == 238, f"Expected 238 cities, got {len(master_df)}"
    assert (
        master_df.duplicated(subset=["City", "Country"]).sum() == 0
    ), "Duplicate (City, Country) pairs found in master dataset"


def test_geolocation_coverage(master_df):
    """Ensure all cities have valid non-null coordinates within geographic bounds."""
    assert master_df["Latitude"].notna().all(), "Missing latitude coordinates found"
    assert master_df["Longitude"].notna().all(), "Missing longitude coordinates found"
    assert (master_df["Latitude"] >= -90.0).all() and (master_df["Latitude"] <= 90.0).all()
    assert (master_df["Longitude"] >= -180.0).all() and (master_df["Longitude"] <= 180.0).all()


def test_macroeconomic_indicators_coverage(master_df):
    """Verify World Bank macroeconomic data is fully populated for all cities."""
    assert master_df["GDP_Per_Capita_USD"].notna().all()
    assert (master_df["GDP_Per_Capita_USD"] > 0).all()
    assert master_df["Life_Expectancy_Years"].notna().all()
    assert (master_df["Life_Expectancy_Years"] >= 40.0).all()


def test_min_max_normalization_bounds(master_df):
    """Assert all normalized columns strictly satisfy bounds in [0.0, 1.0]."""
    val = validate_normalized_columns(master_df, tol=1e-9)
    assert len(val) >= 9, f"Expected at least 9 normalized columns, found {len(val)}"
    for col, info in val.items():
        assert info["valid"], f"Column {col} failed normalization bounds validation: {info}"
        assert info["min"] >= -1e-9, f"{col} min value < 0: {info['min']}"
        assert info["max"] <= 1.0 + 1e-9, f"{col} max value > 1: {info['max']}"


def test_min_max_normalize_edge_cases():
    """Verify min_max_normalize handles constant series, NaNs, and infinities gracefully."""
    const_series = pd.Series([10.0, 10.0, np.nan, 10.0])
    norm_const = min_max_normalize(const_series)
    assert norm_const.iloc[0] == 0.0
    assert norm_const.iloc[1] == 0.0
    assert pd.isna(norm_const.iloc[2])

    all_nan = pd.Series([np.nan, np.nan])
    assert min_max_normalize(all_nan).isna().all()

    inf_series = pd.Series([1.0, 2.0, np.inf, -np.inf, 3.0])
    norm_inf = min_max_normalize(inf_series)
    assert pd.isna(norm_inf.iloc[2])
    assert pd.isna(norm_inf.iloc[3])
    assert norm_inf.iloc[0] == 0.0
    assert norm_inf.iloc[4] == 1.0
