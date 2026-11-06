"""Unit tests for analytical computations, custom scoring, and dynamic insights."""
import pandas as pd
import pytest

from src.data_loader import get_final_merged_data
from src.analysis import (
    recalculate_affordability_score,
    compute_correlation_matrix,
    filter_dataset,
    get_regional_summary,
    get_city_comparison_table,
)
from src.insights import calculate_home_kpis, generate_automated_insights
from src.charts import render_static_seaborn_pairplot


@pytest.fixture(scope="session")
def merged_df():
    """Load final merged dataset."""
    return get_final_merged_data()


def test_recalculate_affordability_score(merged_df):
    """Test what-if score calculation with dynamic weights."""
    # Test equal weights
    res = recalculate_affordability_score(merged_df, w_lpp=0.5, w_clean_air=0.5)
    assert len(res) == len(merged_df)
    assert "Custom_Score" in res.columns
    assert "Custom_Rank" in res.columns
    assert (res["Custom_Score"] >= 0.0).all()
    assert (res["Custom_Score"] <= 100.0).all()
    assert res["Custom_Rank"].min() == 1

    # Zero weights should default to 50/50 without division error
    zero_w = recalculate_affordability_score(merged_df, w_lpp=0.0, w_clean_air=0.0)
    assert len(zero_w) == len(merged_df)
    assert not zero_w["Custom_Score"].isna().any()


def test_compute_correlation_matrix(merged_df):
    """Test correlation matrix calculation for Pearson and Spearman methods."""
    for method in ["pearson", "spearman"]:
        corr = compute_correlation_matrix(merged_df, method=method)
        assert corr.shape[0] == corr.shape[1]
        assert (corr.values <= 1.001).all()
        assert (corr.values >= -1.001).all()
        # Diagonal should be 1.0
        for i in range(len(corr)):
            assert corr.iloc[i, i] == 1.0


def test_filter_dataset(merged_df):
    """Test multi-criteria filtering."""
    # Filter by region
    eur = filter_dataset(merged_df, regions=["Europe"])
    assert (eur["Region"] == "Europe").all()
    assert len(eur) > 0

    # Filter by LPP range
    lpp_filtered = filter_dataset(merged_df, lpp_min=50.0, lpp_max=100.0)
    assert (lpp_filtered["Local_Purchasing_Power_Index"] >= 50.0).all()
    assert (lpp_filtered["Local_Purchasing_Power_Index"] <= 100.0).all()

    # Search filter
    search_res = filter_dataset(merged_df, search_query="Tokyo")
    assert len(search_res) == 1
    assert search_res.iloc[0]["City"] == "Tokyo"


def test_insights_generation(merged_df):
    """Test automated insight generation without errors and verify dynamic values."""
    kpis = calculate_home_kpis(merged_df)
    assert kpis["total_cities"] == 72
    assert kpis["total_countries"] > 30
    assert kpis["median_lpp"] > 0
    assert kpis["median_pm25"] > 0
    assert 0 <= kpis["share_above_who_pct"] <= 100

    insights = generate_automated_insights(merged_df)
    assert "top_score_city" in insights
    assert "cleanest_city" in insights
    assert "most_polluted_city" in insights
    assert insights["traffic_coverage"] == 10
    assert insights["meets_who_count"] >= 0


def test_static_chart_rendering(merged_df):
    """Verify that static Seaborn/Matplotlib chart renders without throwing errors."""
    fig = render_static_seaborn_pairplot(merged_df)
    assert fig is not None
    import matplotlib.pyplot as plt
    plt.close(fig)
