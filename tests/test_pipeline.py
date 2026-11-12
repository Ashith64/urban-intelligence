"""Validation and regression tests for the data preprocessing pipeline.

Asserts exact SPEC Section 4 validation figures and invariant properties.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.config import (
    NUMBEO_RAW_PATH,
    IQAIR_RAW_PATH,
    TOMTOM_RAW_PATH,
    CITIES_REF_PATH,
    COST_OF_LIVING_PROCESSED_PATH,
    AIR_QUALITY_PROCESSED_PATH,
    TRAFFIC_PROCESSED_PATH,
    FINAL_MERGED_PATH,
    WHO_ANNUAL_GUIDELINE,
)
from src.pipeline import run_pipeline, strip_accents, parse_location_label


@pytest.fixture(scope="session")
def pipeline_data():
    """Run pipeline and return the resulting processed DataFrames."""
    return run_pipeline()


def test_raw_files_exist():
    """Ensure approved raw source datasets exist and are non-empty."""
    for p in [NUMBEO_RAW_PATH, IQAIR_RAW_PATH, TOMTOM_RAW_PATH, CITIES_REF_PATH]:
        assert p.exists(), f"Raw dataset missing: {p}"
        assert p.stat().st_size > 0, f"Raw dataset empty: {p}"


def test_processed_files_exist(pipeline_data):
    """Ensure all processed CSV files were successfully written to disk."""
    for p in [
        COST_OF_LIVING_PROCESSED_PATH,
        AIR_QUALITY_PROCESSED_PATH,
        TRAFFIC_PROCESSED_PATH,
        FINAL_MERGED_PATH,
    ]:
        assert p.exists(), f"Processed dataset missing: {p}"
        assert p.stat().st_size > 0, f"Processed dataset empty: {p}"


def test_spec_validation_counts(pipeline_data):
    """Assert the exact validation numbers from SPEC Section 4."""
    numbeo = pipeline_data["cost_of_living"]
    iqair = pipeline_data["air_quality"]
    tomtom = pipeline_data["traffic"]
    final = pipeline_data["final_merged"]

    # Numbeo: 536 raw -> 161 in scope, 19 outlier cities
    assert len(numbeo) == 536, f"Expected 536 Numbeo rows, got {len(numbeo)}"
    assert (
        numbeo["In_Project_Scope"].sum() == 161
    ), f"Expected 161 in-scope Numbeo cities, got {numbeo['In_Project_Scope'].sum()}"
    assert (
        numbeo["Outlier_Flags_IQR"].sum() == 19
    ), f"Expected 19 Numbeo outliers, got {numbeo['Outlier_Flags_IQR'].sum()}"

    # IQAir: 124 raw -> 72 in scope, 9 outlier cities
    assert len(iqair) == 124, f"Expected 124 IQAir rows, got {len(iqair)}"
    assert (
        iqair["In_Project_Scope"].sum() == 72
    ), f"Expected 72 in-scope IQAir cities, got {iqair['In_Project_Scope'].sum()}"
    assert (
        iqair["Outlier_Flags_IQR"].sum() == 9
    ), f"Expected 9 IQAir outliers, got {iqair['Outlier_Flags_IQR'].sum()}"

    # TomTom: 22 raw -> 22 in scope, 0 outliers
    assert len(tomtom) == 22, f"Expected 22 TomTom rows, got {len(tomtom)}"
    assert (
        tomtom["In_Project_Scope"].sum() == 22
    ), f"Expected 22 in-scope TomTom cities, got {tomtom['In_Project_Scope'].sum()}"
    assert (
        tomtom["Outlier_Flags_IQR"].sum() == 0
    ), f"Expected 0 TomTom outliers, got {tomtom['Outlier_Flags_IQR'].sum()}"

    # Final: 72 cities, no duplicate (City, Country), 10 cities with real congestion
    assert len(final) == 72, f"Expected 72 merged cities, got {len(final)}"
    duplicates = final.duplicated(subset=["City", "Country"]).sum()
    assert duplicates == 0, f"Found {duplicates} duplicate cities in merged dataset"

    traffic_count = final["Congestion_Level_2025_pct"].notna().sum()
    assert (
        traffic_count == 10
    ), f"Expected exactly 10 cities with congestion data, got {traffic_count}"


def test_final_dataset_integrity(pipeline_data):
    """Verify null constraints, normalization intervals, and derived columns."""
    final = pipeline_data["final_merged"]

    # No nulls in cost or PM2.5 columns
    cost_cols = [
        "Cost_of_Living_Index",
        "Rent_Index",
        "Cost_of_Living_Plus_Rent_Index",
        "Groceries_Index",
        "Restaurant_Price_Index",
        "Local_Purchasing_Power_Index",
        "PM2_5_2024_ugm3",
    ]
    for col in cost_cols:
        null_count = final[col].isna().sum()
        assert null_count == 0, f"Column {col} has {null_count} nulls"

    # All Min-Max normalized columns in [0, 1]
    norm_cols = [c for c in final.columns if c.endswith("_norm")]
    assert len(norm_cols) >= 3
    for col in norm_cols:
        s = final[col].dropna()
        assert (s >= 0.0).all(), f"{col} has values < 0"
        assert (s <= 1.0).all(), f"{col} has values > 1"
        assert np.isclose(s.min(), 0.0), f"{col} min is {s.min()}, expected 0.0"
        assert np.isclose(s.max(), 1.0), f"{col} max is {s.max()}, expected 1.0"


def test_derived_metrics_formulas(pipeline_data):
    """Verify correctness of derived metric computations."""
    final = pipeline_data["final_merged"]

    # Relative_Net_Income_Index = LPP * Cost_of_Living_Plus_Rent / 100
    expected_rni = (
        final["Local_Purchasing_Power_Index"]
        * final["Cost_of_Living_Plus_Rent_Index"]
        / 100.0
    ).round(2)
    assert np.allclose(final["Relative_Net_Income_Index"], expected_rni)

    # PM2_5_x_WHO_Guideline = PM2.5 / 5
    expected_ratio = (final["PM2_5_2024_ugm3"] / WHO_ANNUAL_GUIDELINE).round(2)
    assert np.allclose(final["PM2_5_x_WHO_Guideline"], expected_ratio)

    # Affordability_Air_Score_0_100 bounds [0, 100]
    assert (final["Affordability_Air_Score_0_100"] >= 0.0).all()
    assert (final["Affordability_Air_Score_0_100"] <= 100.0).all()

    # PM2_5_WHO_Band category validity
    valid_bands = {
        "Meets guideline",
        "Interim 4",
        "Interim 3",
        "Interim 2",
        "Interim 1",
        "Above interim targets",
    }
    assert set(final["PM2_5_WHO_Band"].unique()).issubset(valid_bands)


def test_portland_special_case(pipeline_data):
    """Ensure Portland is in scope only when State == OR."""
    numbeo = pipeline_data["cost_of_living"]
    portland_rows = numbeo[numbeo["City"] == "Portland"]
    for _, row in portland_rows.iterrows():
        if row["State"] == "OR":
            assert row["In_Project_Scope"] is True
        else:
            assert row["In_Project_Scope"] is False
