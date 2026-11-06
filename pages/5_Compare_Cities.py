"""Page 5: Multi-City Comparative Analysis."""
import streamlit as st
import pandas as pd
from src.data_loader import get_final_merged_data
from src.analysis import get_city_comparison_table
from src.charts import plot_radar_comparison, plot_grouped_bar_comparison

st.set_page_config(page_title="Compare Cities - BISL504", page_icon="⚖️", layout="wide")

st.title("⚖️ Multi-City Comparative Analysis")
st.markdown(
    """
    Perform head-to-head comparative evaluations between 2 and 5 world cities. 
    Compare standardized radar profiles across economic and environmental dimensions, 
    review grouped metric bars, and examine the side-by-side matrix.
    """
)

df = get_final_merged_data()

all_cities = sorted(df["City"].tolist())
default_selection = [c for c in ["Zurich", "Tokyo", "Delhi", "San Francisco"] if c in all_cities]

selected_cities = st.multiselect(
    "Select 2 to 5 cities for direct comparison:",
    all_cities,
    default=default_selection,
    max_selections=5,
)

if len(selected_cities) < 2:
    st.info("ℹ️ Please select at least 2 cities (up to 5) to display comparative charts.")
else:
    col_radar, col_bar = st.columns([1, 1])

    with col_radar:
        fig_radar = plot_radar_comparison(df, selected_cities)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption("Radar Chart: Normalized scales (0 = lowest across scope, 1 = highest). Clean Air dimension represents (1 - PM2.5 norm).")

    with col_bar:
        fig_bar = plot_grouped_bar_comparison(df, selected_cities)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Grouped Bar Chart: Direct values across Purchasing Power, Cost of Living, Rent, and PM2.5 concentration.")

    st.markdown("---")
    st.subheader("Side-by-Side Indicator Matrix")
    comparison_table = get_city_comparison_table(df, selected_cities)
    st.dataframe(comparison_table, use_container_width=True)
