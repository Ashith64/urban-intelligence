"""Unit tests for analytical computations, custom scoring, and dynamic insights."""
import pandas as pd
import pytest

from src.data_loader import get_master_data
from src.analysis import (
    calculate_master_kpis,
    calculate_univariate_stats,
    generate_discovery_feed,
    calculate_preset_ranking,
    compute_bivariate_analysis,
    compute_correlation_matrix_filtered,
)


@pytest.fixture(scope="session")
def master_df():
    """Load master dataset."""
    return get_master_data()


def test_calculate_master_kpis(master_df):
    """Test executive KPI calculations."""
    kpis = calculate_master_kpis(master_df)
    assert kpis["total_cities"] == 238
    assert kpis["total_countries"] >= 70
    assert kpis["median_power"] > 0
    assert kpis["median_cost"] > 0
    assert 0 <= kpis["pristine_air_pct"] <= 100
    assert "cleanest_city" in kpis
    assert "highest_power_city" in kpis
    assert "lowest_cost_city" in kpis
    assert "safest_city" in kpis
    assert "best_health_city" in kpis


def test_calculate_univariate_stats(master_df):
    """Test 12 summary statistics computation."""
    res = calculate_univariate_stats(master_df["Purchasing_Power_Index"])
    assert res["Observations"] == 238
    assert res["Missing %"] == "0.0%"
    assert res["Mean"] > 0
    assert res["Median"] > 0
    assert res["Minimum"] <= res["Maximum"]
    assert res["Range"] == pytest.approx(res["Maximum"] - res["Minimum"], 0.01)
    assert res["IQR"] > 0


def test_generate_discovery_feed(master_df):
    """Test automated discovery feed generation."""
    feed = generate_discovery_feed(master_df)
    assert len(feed) >= 5
    for item in feed:
        assert "title" in item
        assert "metric_value" in item
        assert "badge" in item
        assert "explanation" in item
        assert item["sample_size"] == 238
        assert "source" in item


def test_calculate_preset_ranking(master_df):
    """Test what-if preset and custom rankings."""
    for preset in ["Affordability First", "Environment First", "Balanced Priorities"]:
        ranked = calculate_preset_ranking(master_df, preset=preset)
        assert len(ranked) == 238
        assert "Custom_Score" in ranked.columns
        assert "Custom_Rank" in ranked.columns
        assert (ranked["Custom_Score"] >= 0.0).all()
        assert (ranked["Custom_Score"] <= 100.0).all()
        assert ranked["Custom_Rank"].min() == 1
        assert ranked["Custom_Rank"].max() <= 238


def test_compute_bivariate_analysis(master_df):
    """Test bivariate statistical analysis."""
    res = compute_bivariate_analysis(master_df, "Purchasing_Power_Index", "Cost_of_Living_Index")
    assert res["n"] == 238
    assert -1.0 <= res["r"] <= 1.0
    assert -1.0 <= res["rho"] <= 1.0
    assert "interpretation" in res
    assert "causal mechanism" in res["interpretation"]


def test_compute_correlation_matrix_filtered(master_df):
    """Test filtered correlation matrix."""
    corr = compute_correlation_matrix_filtered(master_df)
    assert corr.shape[0] == corr.shape[1]
    assert (corr.values <= 1.001).all()
    assert (corr.values >= -1.001).all()
    for i in range(len(corr)):
        assert pytest.approx(corr.iloc[i, i], 0.001) == 1.0
