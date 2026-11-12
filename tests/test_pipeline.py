"""Validation tests for the BISL504 data pipeline (SPEC section 4)."""

import pandas as pd
import pytest

from src.config import (
    FINAL_MERGED_PATH,
    NUMBEO_NUMERIC_COLS,
    PROCESSED_AQ_PATH,
    PROCESSED_COL_PATH,
    PROCESSED_TRAFFIC_PATH,
)
from src.pipeline import run_pipeline


@pytest.fixture(scope="module")
def pipeline_outputs():
    """Run pipeline once for test module and return output DataFrames."""
    return run_pipeline()


def test_processed_files_exist(pipeline_outputs):
    assert PROCESSED_COL_PATH.exists()
    assert PROCESSED_AQ_PATH.exists()
    assert PROCESSED_TRAFFIC_PATH.exists()
    assert FINAL_MERGED_PATH.exists()


def test_raw_and_scope_counts(pipeline_outputs):
    numbeo = pipeline_outputs["numbeo"]
    iqair = pipeline_outputs["iqair"]
    tomtom = pipeline_outputs["tomtom"]
    final = pipeline_outputs["final"]

    assert len(numbeo) == 536
    assert int(numbeo["In_Project_Scope"].sum()) == 161

    assert len(iqair) == 124
    assert int(iqair["In_Project_Scope"].sum()) == 72

    assert len(tomtom) == 22
    assert int(tomtom["In_Project_Scope"].sum()) == 22

    assert len(final) == 72


def test_final_integrity_and_nulls(pipeline_outputs):
    final = pipeline_outputs["final"]

    # No duplicate (City, Country)
    assert final.duplicated(subset=["City", "Country"]).sum() == 0

    # Exactly 10 cities with real congestion data, no imputation with 0
    assert int(final["Congestion_Level_2025_pct"].notna().sum()) == 10
    assert (final["Congestion_Level_2025_pct"] == 0).sum() == 0

    # No nulls in cost or PM2.5 columns or geo columns
    for col in NUMBEO_NUMERIC_COLS + ["PM2_5_2024_ugm3", "Region", "Latitude", "Longitude"]:
        assert final[col].isna().sum() == 0, f"Unexpected null in {col}"


def test_minmax_norm_bounds(pipeline_outputs):
    final = pipeline_outputs["final"]
    norm_cols = [c for c in final.columns if c.endswith("_norm")]
    assert len(norm_cols) > 0
    for col in norm_cols:
        valid = final[col].dropna()
        assert (valid >= 0.0).all() and (valid <= 1.0).all(), f"Out of [0,1] bounds: {col}"


def test_iqr_outlier_counts(pipeline_outputs):
    numbeo = pipeline_outputs["numbeo"]
    iqair = pipeline_outputs["iqair"]
    tomtom = pipeline_outputs["tomtom"]

    assert int((numbeo["Outlier_Flags_IQR"] != "").sum()) == 19
    assert int((iqair["Outlier_Flags_IQR"] != "").sum()) == 9
    assert int((tomtom["Outlier_Flags_IQR"] != "").sum()) == 0


def test_derived_metrics_formulas(pipeline_outputs):
    final = pipeline_outputs["final"]

    expected_rni = (
        final["Local_Purchasing_Power_Index"]
        * final["Cost_of_Living_Plus_Rent_Index"]
        / 100.0
    )
    assert (final["Relative_Net_Income_Index"] - expected_rni).abs().max() < 1e-9

    expected_who_x = final["PM2_5_2024_ugm3"] / 5.0
    assert (final["PM2_5_x_WHO_Guideline"] - expected_who_x).abs().max() < 1e-9

    expected_score = 100.0 * (
        0.6 * final["Local_Purchasing_Power_Index_norm"]
        + 0.4 * (1.0 - final["PM2_5_2024_ugm3_norm"])
    )
    assert (final["Affordability_Air_Score_0_100"] - expected_score).abs().max() < 1e-9
