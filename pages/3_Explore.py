"""Page 3: Interactive City Exploration with Linked Detail View."""
import pandas as pd
import streamlit as st
import plotly.express as px
from src.data_loader import get_final_merged_data
from src.analysis import filter_dataset
from src.charts import plot_explore_scatter, render_kpi_card, PLOTLY_LAYOUT_DEFAULTS

st.set_page_config(page_title="City Exploration - BISL504", page_icon="🔍", layout="wide")

st.title("🔍 Interactive City Exploration")
st.markdown(
    r"""
    Examine the tension between financial purchasing power and fine particulate matter ($\text{PM}_{2.5}$) 
    air pollution. Filter cities by geographic region, country, air quality band, and economic index. 
    Select any city to drive the linked detail panel below.
    """
)

df = get_final_merged_data()

# Sidebar Filters
st.sidebar.header("Filter Criteria")

all_regions = sorted(df["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Geographic Region:", all_regions, default=all_regions)

# Dynamic country filter based on selected regions
available_countries = sorted(df[df["Region"].isin(selected_regions)]["Country"].unique().tolist())
selected_countries = st.sidebar.multiselect("Country:", available_countries, default=None)

all_bands = [
    "Meets guideline",
    "Interim 4",
    "Interim 3",
    "Interim 2",
    "Interim 1",
    "Above interim targets",
]
available_bands = [b for b in all_bands if b in df["PM2_5_WHO_Band"].unique()]
selected_bands = st.sidebar.multiselect("WHO PM2.5 Guideline Band:", available_bands, default=available_bands)

min_lpp = float(df["Local_Purchasing_Power_Index"].min())
max_lpp = float(df["Local_Purchasing_Power_Index"].max())
lpp_range = st.sidebar.slider(
    "Purchasing Power Index Range (NY=100):",
    min_value=float(int(min_lpp)),
    max_value=float(int(max_lpp) + 1),
    value=(float(int(min_lpp)), float(int(max_lpp) + 1)),
)

search_term = st.sidebar.text_input("Quick City Search:", placeholder="e.g. Zurich, Tokyo, New York")

# Controls above chart
col_ctrl1, col_ctrl2 = st.columns([1, 1])
with col_ctrl1:
    log_y = st.toggle("Logarithmic PM2.5 Scale (Recommended)", value=True)
with col_ctrl2:
    color_by = st.radio("Color Data Points By:", ["Region", "PM2_5_WHO_Band"], horizontal=True)

# Apply filters
filtered_df = filter_dataset(
    df,
    regions=selected_regions,
    countries=selected_countries if selected_countries else None,
    pm25_bands=selected_bands,
    lpp_min=lpp_range[0],
    lpp_max=lpp_range[1],
    search_query=search_term,
)

if filtered_df.empty:
    st.warning("⚠️ No cities match the selected filter criteria. Please broaden your selection in the sidebar.")
else:
    st.info(f"Showing **{len(filtered_df)}** of **{len(df)}** cities matching current filters.")

    # Scatter Chart
    fig = plot_explore_scatter(filtered_df, log_y=log_y, color_by=color_by)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Chart Takeaway: High purchasing power clusters primarily in Europe and North America below 15 µg/m³; higher PM2.5 concentrations above interim targets occur mainly in developing regions.")

    st.markdown("---")

    # Linked Detail Drill-down Panel
    st.subheader("📌 Linked City Detail Inspector")
    city_options = sorted(filtered_df["City"].tolist())
    selected_city = st.selectbox("Select a city to inspect detailed attributes:", city_options, index=0)

    city_row = filtered_df[filtered_df["City"] == selected_city].iloc[0]

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        render_kpi_card("Affordability-Air Score", f"{city_row['Affordability_Air_Score_0_100']:.1f}", f"Rank in scope: #{df[df['Affordability_Air_Score_0_100'] >= city_row['Affordability_Air_Score_0_100']].shape[0]}")
    with d_col2:
        render_kpi_card("Local Purchasing Power", f"{city_row['Local_Purchasing_Power_Index']:.1f}", f"Relative Net Income: {city_row['Relative_Net_Income_Index']:.1f}")
    with d_col3:
        render_kpi_card("PM2.5 (2024)", f"{city_row['PM2_5_2024_ugm3']:.1f} µg/m³", f"{city_row['PM2_5_x_WHO_Guideline']:.1f}× WHO Guideline ({city_row['PM2_5_WHO_Band']})")
    with d_col4:
        traffic_val = f"{city_row['Congestion_Level_2025_pct']:.1f}%" if pd.notna(city_row['Congestion_Level_2025_pct']) else "Not Published"
        render_kpi_card("Traffic Congestion", traffic_val, "TomTom 2025 Index")

    st.markdown("#### Full Profile Summary")
    detail_data = {
        "Metric": [
            "Country",
            "Region",
            "Cost of Living Index (NY=100)",
            "Rent Index (NY=100)",
            "Cost of Living Plus Rent Index",
            "Groceries Index",
            "Restaurant Price Index",
            "Local Purchasing Power Index",
            "PM2.5 Concentration (2024)",
            "WHO Guideline Multiplier",
            "WHO Air Quality Band",
            "Congestion Level (%)",
            "Average Speed (km/h)",
            "Rush Hours Lost per Year",
        ],
        "Value": [
            city_row["Country"],
            city_row["Region"],
            f"{city_row['Cost_of_Living_Index']:.1f}",
            f"{city_row['Rent_Index']:.1f}",
            f"{city_row['Cost_of_Living_Plus_Rent_Index']:.1f}",
            f"{city_row['Groceries_Index']:.1f}",
            f"{city_row['Restaurant_Price_Index']:.1f}",
            f"{city_row['Local_Purchasing_Power_Index']:.1f}",
            f"{city_row['PM2_5_2024_ugm3']:.1f} µg/m³",
            f"{city_row['PM2_5_x_WHO_Guideline']:.2f}×",
            city_row["PM2_5_WHO_Band"],
            f"{city_row['Congestion_Level_2025_pct']:.1f}%" if pd.notna(city_row["Congestion_Level_2025_pct"]) else "N/A",
            f"{city_row['Avg_Speed_kmh']:.1f} km/h" if pd.notna(city_row.get("Avg_Speed_kmh")) else "N/A",
            f"{city_row['Rush_Hours_Lost_per_Year']:.0f} hrs" if pd.notna(city_row.get("Rush_Hours_Lost_per_Year")) else "N/A",
        ],
    }
    st.dataframe(pd.DataFrame(detail_data), hide_index=True)
