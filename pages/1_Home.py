"""Page 1: Executive Overview / Home."""
import streamlit as st
from src.data_loader import get_final_merged_data
from src.insights import calculate_home_kpis
from src.charts import render_kpi_card

st.set_page_config(page_title="Urban Affordability & Liveability", page_icon="🏙️", layout="wide")

st.title("🏙️ Urban Affordability & Liveability Intelligence Platform")
st.markdown(
    r"""
    **Purpose**: This platform investigates which global cities successfully balance financial affordability with 
    environmental breathability. By harmonizing cost-of-living indicators, local purchasing power, annual particulate 
    matter ($\text{PM}_{2.5}$) air quality, and urban traffic congestion across 72 benchmark global cities, the dashboard 
    equips researchers, urban planners, and global citizens with evidence-based insights into liveability trade-offs.
    """
)

# Load data and dynamic KPIs
df = get_final_merged_data()
kpis = calculate_home_kpis(df)

st.markdown("### Executive Summary KPIs")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Scope Cities", f"{kpis['total_cities']}", "Standardized global cities")
with col2:
    render_kpi_card("Countries", f"{kpis['total_countries']}", "Sovereign nations represented")
with col3:
    render_kpi_card("Median Purchasing Power", f"{kpis['median_lpp']}", "Base: New York = 100")
with col4:
    render_kpi_card("Median PM2.5", f"{kpis['median_pm25']} µg/m³", "Annual particulate level")
with col5:
    render_kpi_card("Exceeding WHO Guideline", f"{kpis['share_above_who_pct']}%", "Above 5.0 µg/m³ guideline")

st.markdown("---")

# Data-source badges and scope
col_sources, col_guide = st.columns([1, 1])

with col_sources:
    st.subheader("Validated Data Sources")
    st.markdown(
        r"""
        - 🏷️ **Numbeo Cost of Living Index (2025 Snapshot)**: Relative purchasing power, rent, groceries, and living costs normalized against New York City.
        - 🏷️ **IQAir World Air Quality Report (2024)**: Ground-level fine particulate matter ($\text{PM}_{2.5}$) concentrations in $\mu\text{g/m}^3$ primarily from capital cities.
        - 🏷️ **TomTom Traffic Index (2025)**: Congestion percentage and rush hours lost per year across major metropolitan transport networks (10 cities with real data).
        - 🏷️ **Cities Reference Scope**: Curated 161-city global benchmark scope with verified geographical coordinates and regions.
        """
    )
    st.info("💡 **Snapshot Limitation**: Datasets represent real single-period snapshots. No artificial time series or imputed synthetic values are used.")

with col_guide:
    st.subheader("Platform Navigation Guide")
    st.markdown(
        """
        1. **📊 Data Profiling**: Inspect source schemas, missingness patterns, and 1.5×IQR outlier detection.
        2. **🔍 Explore Cities**: Interactive scatter plot of Purchasing Power vs $\text{PM}_{2.5}$ with linked detail drill-down.
        3. **🗺️ Global Map**: Geographic projection with dynamic color encoding and bubble size dimensioning.
        4. **⚖️ Compare Cities**: Head-to-head multi-city radar chart and grouped indicator comparison.
        5. **🏆 Dynamic Rankings**: Interactive what-if scoring adjusting weights between purchasing power and clean air.
        6. **📈 Correlation & Distribution**: Pearson and Spearman matrix heatmaps, regional box plots, and static KDE regression.
        7. **📁 Data Explorer**: Interactive filtered tabular data with direct CSV exports.
        8. **💡 Automated Insights**: Key statistical leaders, regional disparities, and compliance metrics computed dynamically.
        9. **📋 Methodology & Limits**: Mathematical formulas, data transformations, and documented analytical limitations.
        """
    )
