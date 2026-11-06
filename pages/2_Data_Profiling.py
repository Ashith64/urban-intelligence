"""Page 2: Dataset Profiling, Missingness, and Outlier Analysis."""
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import (
    get_raw_datasets,
    get_cost_of_living_data,
    get_air_quality_data,
    get_traffic_data,
    get_final_merged_data,
)
from src.charts import PLOTLY_LAYOUT_DEFAULTS

st.set_page_config(page_title="Data Profiling - BISL504", page_icon="📊", layout="wide")

st.title("📊 Dataset Profiling & Quality Audit")
st.markdown(
    """
    Comprehensive data profiling across all four approved source datasets. 
    Inspect dimensions, data types, missing value patterns, 1.5×IQR outlier detection, 
    and label standardization audits.
    """
)

raw_data = get_raw_datasets()
numbeo_df = get_cost_of_living_data()
iqair_df = get_air_quality_data()
tomtom_df = get_traffic_data()
final_df = get_final_merged_data()

# 1. Pipeline Summary Metrics
st.subheader("1. Source Datasets & Scope Audit")

summary_records = [
    {
        "Dataset": "Numbeo Cost of Living",
        "Raw Rows": len(raw_data["numbeo_raw"]),
        "Raw Columns": len(raw_data["numbeo_raw"].columns),
        "In Scope": int(numbeo_df["In_Project_Scope"].sum()),
        "IQR Outliers": int(numbeo_df["Outlier_Flags_IQR"].sum()),
        "Scope Retention": f"{(numbeo_df['In_Project_Scope'].sum() / len(numbeo_df)) * 100:.1f}%",
    },
    {
        "Dataset": "IQAir World Air Quality",
        "Raw Rows": len(raw_data["iqair_raw"]),
        "Raw Columns": len(raw_data["iqair_raw"].columns),
        "In Scope": int(iqair_df["In_Project_Scope"].sum()),
        "IQR Outliers": int(iqair_df["Outlier_Flags_IQR"].sum()),
        "Scope Retention": f"{(iqair_df['In_Project_Scope'].sum() / len(iqair_df)) * 100:.1f}%",
    },
    {
        "Dataset": "TomTom Traffic Index",
        "Raw Rows": len(raw_data["tomtom_raw"]),
        "Raw Columns": len(raw_data["tomtom_raw"].columns),
        "In Scope": int(tomtom_df["In_Project_Scope"].sum()),
        "IQR Outliers": int(tomtom_df["Outlier_Flags_IQR"].sum()),
        "Scope Retention": f"{(tomtom_df['In_Project_Scope'].sum() / len(tomtom_df)) * 100:.1f}%",
    },
    {
        "Dataset": "Cities Reference Scope",
        "Raw Rows": len(raw_data["cities_ref"]),
        "Raw Columns": len(raw_data["cities_ref"].columns),
        "In Scope": 161,
        "IQR Outliers": 0,
        "Scope Retention": "100.0%",
    },
    {
        "Dataset": "Final Harmonized Merged",
        "Raw Rows": len(final_df),
        "Raw Columns": len(final_df.columns),
        "In Scope": len(final_df),
        "IQR Outliers": 0,
        "Scope Retention": "100.0%",
    },
]

st.dataframe(pd.DataFrame(summary_records), hide_index=True)

st.markdown("---")

# 2. Missing Value Analysis
st.subheader("2. Missing Value Profiling")
col_miss1, col_miss2 = st.columns([1, 1])

with col_miss1:
    source_choice = st.selectbox(
        "Select dataset to profile missing values:",
        ["Numbeo (Cost of Living)", "IQAir (Air Quality)", "TomTom (Traffic)", "Final Merged"],
    )

    if source_choice == "Numbeo (Cost of Living)":
        target_df = numbeo_df
    elif source_choice == "IQAir (Air Quality)":
        target_df = iqair_df
    elif source_choice == "TomTom (Traffic)":
        target_df = tomtom_df
    else:
        target_df = final_df

    missing_series = target_df.isna().sum()
    missing_pct = (missing_series / len(target_df) * 100).round(1)
    missing_df = pd.DataFrame({"Column": missing_series.index, "Missing Count": missing_series.values, "Missing %": missing_pct.values})
    missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values(by="Missing Count", ascending=False)

    if missing_df.empty:
        st.success(f"No missing values found in **{source_choice}**!")
    else:
        st.dataframe(missing_df, hide_index=True)

with col_miss2:
    if not missing_df.empty:
        fig_miss = px.bar(
            missing_df,
            x="Column",
            y="Missing Count",
            color="Missing %",
            color_continuous_scale="Reds",
            title=f"Missing Value Counts: {source_choice}",
        )
        fig_miss.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        st.plotly_chart(fig_miss, use_container_width=True)
    else:
        st.info("Complete coverage: All required cost of living and particulate matter fields have 0% missingness in the merged scope.")

st.markdown("---")

# 3. Outlier Detection Table
st.subheader("3. Outlier Detection Audit (1.5×IQR Rule)")
st.markdown(
    """
    Outliers are identified using Tukey's fences ($[Q_1 - 1.5 \\times \\text{IQR}, Q_3 + 1.5 \\times \\text{IQR}]$). 
    **Engineering Rule Adherence**: Real observations are flagged but **never deleted, imputed, or capped**, 
    preserving scientific authenticity.
    """
)

tab_numbeo, tab_iqair, tab_tomtom = st.tabs(["Numbeo Outliers (19)", "IQAir Outliers (9)", "TomTom Outliers (0)"])

with tab_numbeo:
    outlier_numbeo = numbeo_df[numbeo_df["Outlier_Flags_IQR"]][
        ["City", "Country", "Cost_of_Living_Index", "Rent_Index", "Local_Purchasing_Power_Index"]
    ]
    st.dataframe(outlier_numbeo, hide_index=True)

with tab_iqair:
    outlier_iqair = iqair_df[iqair_df["Outlier_Flags_IQR"]][
        ["City", "Country", "PM2_5_2024_ugm3"]
    ]
    st.dataframe(outlier_iqair, hide_index=True)

with tab_tomtom:
    outlier_tomtom = tomtom_df[tomtom_df["Outlier_Flags_IQR"]]
    if outlier_tomtom.empty:
        st.success("Zero congestion outliers flagged under the 1.5×IQR rule.")
    else:
        st.dataframe(outlier_tomtom, hide_index=True)

st.markdown("---")

# 4. Before & After Standardization Audit
st.subheader("4. Label Parsing & Alias Normalization Audit")
st.markdown("Examples of raw published strings mapped to standardized entities and project scope.")

sample_cities = ["Tel Aviv-Yafo", "Krakow (Cracow)", "New Delhi", "Dakha", "Bengaluru", "Washington D.C.", "Portland", "Mexico City, MX"]
sample_rows = []
for city_raw in sample_cities:
    # Look up in Numbeo or IQAir or TomTom
    num_match = numbeo_df[numbeo_df["City_Raw"].str.contains(city_raw, regex=False, case=False, na=False)]
    if not num_match.empty:
        r = num_match.iloc[0]
        sample_rows.append({"Source": "Numbeo", "Raw Label": r["City_Raw"], "Parsed City": r["City"], "Country": r["Country"], "In Scope": r["In_Project_Scope"]})
    else:
        iq_match = iqair_df[iqair_df["City_Raw"].str.contains(city_raw, regex=False, case=False, na=False)]
        if not iq_match.empty:
            r = iq_match.iloc[0]
            sample_rows.append({"Source": "IQAir", "Raw Label": r["City_Raw"], "Parsed City": r["City"], "Country": r["Country"], "In Scope": r["In_Project_Scope"]})
        else:
            tt_match = tomtom_df[tomtom_df["City_Raw"].str.contains(city_raw, regex=False, case=False, na=False)]
            if not tt_match.empty:
                r = tt_match.iloc[0]
                sample_rows.append({"Source": "TomTom", "Raw Label": r["City_Raw"], "Parsed City": r["City"], "Country": r["Country"], "In Scope": r["In_Project_Scope"]})

st.dataframe(pd.DataFrame(sample_rows), hide_index=True)

st.markdown("---")

# 5. Validation Check Gates
st.subheader("5. Automated Validation Checkpoints")
checks = [
    ("Numbeo raw dataset contains 536 rows", len(raw_data["numbeo_raw"]) == 536),
    ("Numbeo retains exactly 161 in-scope benchmark cities", numbeo_df["In_Project_Scope"].sum() == 161),
    ("Numbeo has exactly 19 IQR flagged outliers", numbeo_df["Outlier_Flags_IQR"].sum() == 19),
    ("IQAir raw dataset contains 124 rows", len(raw_data["iqair_raw"]) == 124),
    ("IQAir retains exactly 72 in-scope benchmark cities", iqair_df["In_Project_Scope"].sum() == 72),
    ("IQAir has exactly 9 IQR flagged outliers", iqair_df["Outlier_Flags_IQR"].sum() == 9),
    ("TomTom traffic raw dataset contains 22 rows", len(raw_data["tomtom_raw"]) == 22),
    ("TomTom traffic retains exactly 22 in-scope cities", tomtom_df["In_Project_Scope"].sum() == 22),
    ("TomTom has 0 congestion outliers under IQR", tomtom_df["Outlier_Flags_IQR"].sum() == 0),
    ("Final merged dataset yields exactly 72 harmonized cities", len(final_df) == 72),
    ("No duplicate (City, Country) pairs in final dataset", final_df.duplicated(subset=["City", "Country"]).sum() == 0),
    ("Exactly 10 cities have real traffic congestion observations", final_df["Congestion_Level_2025_pct"].notna().sum() == 10),
    ("Zero nulls in cost or PM2.5 metrics in merged dataset", final_df["Local_Purchasing_Power_Index"].isna().sum() == 0 and final_df["PM2_5_2024_ugm3"].isna().sum() == 0),
    ("Min-Max normalized indices strictly bounded in [0, 1]", all((final_df[c] >= 0.0).all() and (final_df[c] <= 1.0).all() for c in final_df.columns if c.endswith("_norm"))),
]

for label, passed in checks:
    icon = "✅" if passed else "❌"
    st.markdown(f"{icon} **{label}**")
