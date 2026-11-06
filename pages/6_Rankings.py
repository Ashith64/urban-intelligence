"""Page 6: Dynamic Rankings & What-If Weighting Model."""
import streamlit as st
import pandas as pd
from src.data_loader import get_final_merged_data
from src.analysis import recalculate_affordability_score
from src.charts import plot_rankings_bar

st.set_page_config(page_title="Dynamic Rankings - BISL504", page_icon="🏆", layout="wide")

st.title("🏆 Dynamic Rankings & What-If Simulation")
st.markdown(
    """
    Test personal priorities by adjusting the relative weighting between **Economic Purchasing Power** 
    and **Environmental Clean Air** ($1 - \\text{norm}(\\text{PM}_{2.5})$). 
    Sliders automatically re-normalize to 100%, instantly recalculating scores and ranking tables.
    """
)

df = get_final_merged_data()

st.sidebar.header("What-If Weight Parameters")
w_lpp_raw = st.sidebar.slider("Weight: Local Purchasing Power", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
w_air_raw = st.sidebar.slider("Weight: Clean Air Quality", min_value=0.0, max_value=1.0, value=0.4, step=0.05)
top_n = st.sidebar.slider("Number of Cities to Display (Top-N):", min_value=5, max_value=len(df), value=15, step=5)

# Calculate normalized weights
total_w = w_lpp_raw + w_air_raw
if total_w <= 0:
    w1_pct = 50.0
    w2_pct = 50.0
else:
    w1_pct = (w_lpp_raw / total_w) * 100.0
    w2_pct = (w_air_raw / total_w) * 100.0

col_w1, col_w2, col_w3 = st.columns(3)
with col_w1:
    st.metric("Effective Purchasing Power Weight", f"{w1_pct:.1f}%")
with col_w2:
    st.metric("Effective Clean Air Weight", f"{w2_pct:.1f}%")
with col_w3:
    st.metric("Total Weight Balance", f"{w1_pct + w2_pct:.0f}%")

# Recalculate scores dynamically
ranked_df = recalculate_affordability_score(df, w_lpp=w_lpp_raw, w_clean_air=w_air_raw)

# Render Chart
fig_rank = plot_rankings_bar(ranked_df, score_col="Custom_Score", top_n=top_n)
st.plotly_chart(fig_rank, use_container_width=True)
st.caption(f"Takeaway: Cities with balanced high purchasing power and low PM2.5 dominate the top rankings under current {w1_pct:.0f}/{w2_pct:.0f} weights.")

st.markdown("---")
st.subheader("Dynamic Leaderboard Table")

display_df = ranked_df[
    [
        "Custom_Rank",
        "City",
        "Country",
        "Region",
        "Custom_Score",
        "Local_Purchasing_Power_Index",
        "PM2_5_2024_ugm3",
        "PM2_5_WHO_Band",
        "Cost_of_Living_Index",
        "Rent_Index",
    ]
].rename(
    columns={
        "Custom_Rank": "Rank",
        "Custom_Score": "Simulated Score",
        "Local_Purchasing_Power_Index": "Purchasing Power",
        "PM2_5_2024_ugm3": "PM2.5 (µg/m³)",
        "PM2_5_WHO_Band": "WHO Band",
        "Cost_of_Living_Index": "Cost of Living",
        "Rent_Index": "Rent Index",
    }
)

st.dataframe(display_df, hide_index=True)

# CSV Download
csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Custom Rankings CSV",
    data=csv_data,
    file_name=f"custom_rankings_wLPP{w1_pct:.0f}_wAir{w2_pct:.0f}.csv",
    mime="text/csv",
)
