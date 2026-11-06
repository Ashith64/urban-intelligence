"""Page 4: Global Geographic Distribution Map."""
import streamlit as st
from src.data_loader import get_final_merged_data
from src.charts import plot_global_map

st.set_page_config(page_title="Global Map - BISL504", page_icon="🗺️", layout="wide")

st.title("🗺️ Global Geospatial Intelligence Map")
st.markdown(
    """
    Explore the geographic distribution of benchmark global cities. 
    Select the active analytical metric for choropleth/scatter color encoding. 
    Circle size indicates **Cost of Living Index** (larger bubbles signify higher expense).
    """
)

df = get_final_merged_data()

metric_options = {
    "Affordability_Air_Score_0_100": "Affordability-Air Score (0-100)",
    "PM2_5_2024_ugm3": "PM2.5 Concentration (µg/m³)",
    "Local_Purchasing_Power_Index": "Local Purchasing Power Index (NY=100)",
    "Cost_of_Living_Index": "Cost of Living Index (NY=100)",
    "Rent_Index": "Rent Index (NY=100)",
    "Relative_Net_Income_Index": "Relative Net Income Index",
}

col_sel1, col_sel2 = st.columns([2, 1])
with col_sel1:
    selected_metric_key = st.selectbox(
        "Choose metric for circle color encoding:",
        list(metric_options.keys()),
        format_func=lambda k: metric_options[k],
        index=0,
    )
with col_sel2:
    selected_region = st.selectbox(
        "Filter by Geographic Focus:",
        ["All Regions"] + sorted(df["Region"].unique().tolist()),
    )

map_data = df if selected_region == "All Regions" else df[df["Region"] == selected_region]

if map_data.empty:
    st.warning("No cities found in this geographic focus.")
else:
    fig_map = plot_global_map(
        map_data,
        color_metric=selected_metric_key,
        color_label=metric_options[selected_metric_key],
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("Map Legend: Color indicates selected metric value (purple/blue for optimal, yellow for challenging on inverted scales). Bubble diameter reflects relative Cost of Living.")

    st.markdown("---")
    st.subheader(f"Geographic Summary: {metric_options[selected_metric_key]}")
    geo_summary = (
        map_data.groupby("Region")[selected_metric_key]
        .agg(["count", "mean", "median", "min", "max"])
        .round(2)
        .reset_index()
    )
    st.dataframe(geo_summary, hide_index=True)
