"""Page 8: Interactive Data Explorer and Dataset Exports."""
import streamlit as st
import pandas as pd
from src.data_loader import (
    get_final_merged_data,
    get_cost_of_living_data,
    get_air_quality_data,
    get_traffic_data,
    get_raw_datasets,
)

st.set_page_config(page_title="Data Explorer - BISL504", page_icon="📁", layout="wide")

st.title("📁 Interactive Data Explorer & Export Center")
st.markdown(
    """
    Explore the raw, processed, and final merged datasets. 
    Customize visible columns, filter tabular rows, and download complete CSV files 
    for transparent verification and external modeling.
    """
)

raw_data = get_raw_datasets()
final_df = get_final_merged_data()
col_df = get_cost_of_living_data()
air_df = get_air_quality_data()
traffic_df = get_traffic_data()

dataset_options = {
    "Final Merged Scope (72 Cities)": final_df,
    "Processed Cost of Living (Numbeo)": col_df,
    "Processed Air Quality (IQAir)": air_df,
    "Processed Traffic (TomTom)": traffic_df,
    "Raw Numbeo (536 Rows)": raw_data["numbeo_raw"],
    "Raw IQAir (124 Rows)": raw_data["iqair_raw"],
    "Raw TomTom (22 Rows)": raw_data["tomtom_raw"],
    "Cities Reference (161 Rows)": raw_data["cities_ref"],
}

selected_dataset_label = st.selectbox(
    "Choose dataset to inspect:",
    list(dataset_options.keys()),
    index=0,
)

current_df = dataset_options[selected_dataset_label]

col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    st.metric("Total Records", f"{len(current_df):,}")
with col_stats2:
    st.metric("Total Columns", f"{len(current_df.columns)}")
with col_stats3:
    st.metric("Memory Footprint", f"{current_df.memory_usage(deep=True).sum() / 1024:.1f} KB")

# Column Picker
all_cols = current_df.columns.tolist()
selected_cols = st.multiselect("Select columns to display:", all_cols, default=all_cols)

if not selected_cols:
    st.warning("Please select at least one column to view.")
else:
    # Text search
    search_q = st.text_input("Filter rows by keyword:", placeholder="Type any city, country, or code...")
    display_df = current_df[selected_cols]

    if search_q:
        q = search_q.strip().lower()
        mask = display_df.astype(str).apply(lambda row: row.str.lower().str.contains(q).any(), axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True)

    # Download Button
    csv_bytes = current_df[selected_cols].to_csv(index=False).encode("utf-8")
    sanitized_name = selected_dataset_label.lower().replace(" ", "_").replace("(", "").replace(")", "")
    st.download_button(
        label=f"📥 Download {selected_dataset_label} as CSV",
        data=csv_bytes,
        file_name=f"{sanitized_name}.csv",
        mime="text/csv",
    )
