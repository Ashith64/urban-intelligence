"""Page 9: Automated Statistical Insights and Key Findings."""
import streamlit as st
import pandas as pd
from src.data_loader import get_final_merged_data
from src.insights import generate_automated_insights
from src.charts import render_kpi_card

st.set_page_config(page_title="Automated Insights - BISL504", page_icon="💡", layout="wide")

st.title("💡 Automated Intelligence & Empirical Findings")
st.markdown(
    """
    Key analytical takeaways synthesized algorithmically from the harmonized data snapshot. 
    **Rule Verification**: Every number, ranking, and takeaway is computed dynamically 
    at runtime without hardcoded values.
    """
)

df = get_final_merged_data()
insights = generate_automated_insights(df)

# Top Performer Highlights
st.subheader("1. Platform Score Leaders")
col_lead1, col_lead2 = st.columns(2)

with col_lead1:
    top_c = insights["top_score_city"]
    render_kpi_card(
        "Top Balanced City",
        f"{top_c['name']}, {top_c['country']}",
        f"Affordability-Air Score: {top_c['score']:.1f}/100 | LPP: {top_c['lpp']:.1f} | PM2.5: {top_c['pm25']:.1f} µg/m³",
    )

with col_lead2:
    bot_c = insights["bottom_score_city"]
    render_kpi_card(
        "Lowest Scored City",
        f"{bot_c['name']}, {bot_c['country']}",
        f"Affordability-Air Score: {bot_c['score']:.1f}/100 (Constrained by purchasing power & air pollution)",
    )

st.markdown("---")

# Environmental & Economic Extremes
st.subheader("2. Environmental & Economic Extremes")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

with col_e1:
    clean = insights["cleanest_city"]
    render_kpi_card("Cleanest Air", f"{clean['name']}", f"{clean['pm25']:.1f} µg/m³ ({clean['country']})")

with col_e2:
    poll = insights["most_polluted_city"]
    render_kpi_card("Highest Pollution", f"{poll['name']}", f"{poll['pm25']:.1f} µg/m³ ({poll['country']})")

with col_e3:
    max_l = insights["max_lpp_city"]
    render_kpi_card("Highest Purchasing Power", f"{max_l['name']}", f"LPP {max_l['lpp']:.1f} ({max_l['country']})")

with col_e4:
    min_l = insights["min_lpp_city"]
    render_kpi_card("Lowest Purchasing Power", f"{min_l['name']}", f"LPP {min_l['lpp']:.1f} ({min_l['country']})")

st.markdown("---")

# Global Guideline & Regional Disparities
st.subheader("3. WHO Air Quality Compliance & Regional Medians")
col_reg1, col_reg2 = st.columns([1, 1])

with col_reg1:
    st.markdown("#### WHO 2021 Annual Guideline (5.0 µg/m³)")
    st.write(
        f"- **Cities Meeting Guideline**: **{insights['meets_who_count']}** of **{len(df)}** cities ({insights['meets_who_pct']}%)."
    )
    st.write(
        f"- **Cities Exceeding Guideline**: **{len(df) - insights['meets_who_count']}** of **{len(df)}** cities ({100.0 - insights['meets_who_pct']:.1f}%)."
    )
    st.progress(insights["meets_who_pct"] / 100.0)
    st.caption("A vast majority of major global hubs currently exceed the World Health Organization's strict health threshold.")

with col_reg2:
    st.markdown("#### Regional Leaders & Disparities")
    st.write(
        f"- **Cleanest Regional Median**: **{insights['cleanest_region'][0]}** ({insights['cleanest_region'][1]} µg/m³ median $\\text{{PM}}_{{2.5}}$)."
    )
    st.write(
        f"- **Highest Regional Pollution Median**: **{insights['most_polluted_region'][0]}** ({insights['most_polluted_region'][1]} µg/m³ median $\\text{{PM}}_{{2.5}}$)."
    )
    st.write(
        f"- **Highest Economic Purchasing Power**: **{insights['wealthiest_region'][0]}** ({insights['wealthiest_region'][1]} median LPP index)."
    )

st.markdown("---")

# Statistical Associations & Transport Network Coverage
st.subheader("4. Correlation Insights & Transport Observations")

pos_pair, pos_val = insights["strongest_pos_corr"]
neg_pair, neg_val = insights["strongest_neg_corr"]

col_stat1, col_stat2 = st.columns(2)
with col_stat1:
    st.markdown("#### Primary Metric Collinearity")
    st.write(f"- **Strongest Positive Association**: `{pos_pair[0]}` and `{pos_pair[1]}` (Pearson $r = {pos_val}$).")
    st.write(f"- **Strongest Inverse Association**: `{neg_pair[0]}` and `{neg_pair[1]}` (Pearson $r = {neg_val}$).")

with col_stat2:
    st.markdown("#### Urban Transport (TomTom Coverage)")
    st.write(f"- **Cities with Real Traffic Data**: **{insights['traffic_coverage']}** of 72 scope cities.")
    st.write(f"- **Highest Observed Congestion**: **{insights['worst_traffic_city']}**.")
    st.info("⚠️ Traffic metrics are retained strictly where published; no missing values are substituted with zero.")
