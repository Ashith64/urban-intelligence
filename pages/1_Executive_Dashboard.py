"""Page 1 — Executive Dashboard: 10-second overview, Liveability Quadrant, and Standouts."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.data_loader import get_master_data
from src.analysis import calculate_master_kpis
from src.theme import (
    executive_kpi_card, section_header, semantic_badge,
    EMERALD, CHAMPAGNE, CORAL, SILVER, BG,
    TEXT_PRIMARY, TEXT_SECONDARY, SURFACE, SURFACE_ELEVATED, BORDER, REGION_COLORS,
)

df = get_master_data()
kpis = calculate_master_kpis(df)

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, {SURFACE} 0%, #0E131A 100%);
        border: 1px solid {BORDER};
        border-left: 4px solid {CHAMPAGNE};
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 1.6rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    ">
        <div style="font-size: 0.72rem; font-weight: 700; color: {CHAMPAGNE};
                    text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 6px;">
            URBAN INTELLIGENCE · THE GLOBAL LIVEABILITY OBSERVATORY
        </div>
        <h1 style="font-size: 2.2rem; font-weight: 800; margin: 0 0 8px; color: {TEXT_PRIMARY};">
            Where does your money go further?
        </h1>
        <p style="font-size: 1.02rem; color: {TEXT_SECONDARY}; margin: 0 0 14px; max-width: 780px; line-height: 1.5;">
            Explore how affordability, purchasing power and quality of life vary across global cities.
        </p>
        <div style="display:flex; flex-wrap:wrap; gap:18px; font-size:0.76rem; color:{SILVER}; border-top:1px solid {BORDER}; padding-top:10px;">
            <span><strong>Observation Period:</strong> 2024–2025</span>
            <span><strong>Available Cities:</strong> {kpis['total_cities']} metropolises</span>
            <span><strong>Country Coverage:</strong> {kpis['total_countries']} countries & areas</span>
            <span><strong>Sources:</strong> Numbeo · GeoNames · World Bank</span>
            <span><strong>Status:</strong> Processed Offline Cache</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 4 Executive KPI Cards ─────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        executive_kpi_card("Cities Analysed", str(kpis["total_cities"]),
                           f"Across {kpis['total_countries']} countries & areas", CHAMPAGNE, "🏙️"),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        executive_kpi_card("Countries & Areas", str(kpis["total_countries"]),
                           "Represented in verified master database", EMERALD, "🌍"),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        executive_kpi_card("Median Purchasing Power", str(kpis["median_power"]),
                           "Benchmark index (New York = 100)", CHAMPAGNE, "💰"),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        executive_kpi_card("Median House Price Multiple", f"{kpis['median_price_to_income']}×",
                           "Years of net income to purchase an apartment", CORAL, "🏠"),
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top:1.5rem'>", unsafe_allow_html=True)

# ── Main Visualization: The Liveability Quadrant ──────────────────────────────
section_header(
    "The Liveability Quadrant",
    "Balancing purchasing power against environmental quality. Divided into four analytically distinct performance zones."
)

ZONE_MAP = {
    "★ High Power · Clean Air": EMERALD,
    "High Power · Polluted":    CHAMPAGNE,
    "Low Power · Clean Air":    "#68A4C4",
    "Low Power · Polluted":     CORAL,
}

med_p = df["Purchasing_Power_Index"].median()
med_pol = df["Pollution_Index"].median()

fig_quad = px.scatter(
    df,
    x="Purchasing_Power_Index",
    y="Pollution_Index",
    color="Liveability_Zone",
    color_discrete_map=ZONE_MAP,
    size="Cost_of_Living_Index",
    size_max=18,
    hover_name="City",
    hover_data={
        "Country": True,
        "Region": True,
        "Purchasing_Power_Index": ":.1f",
        "Pollution_Index": ":.1f",
        "Cost_of_Living_Index": ":.1f",
        "Liveability_Zone": False,
    },
    labels={
        "Purchasing_Power_Index": "Local Purchasing Power Index (New York = 100)",
        "Pollution_Index": "Pollution Index (Lower is Cleaner)",
        "Cost_of_Living_Index": "Cost of Living",
    },
)

# Reference crosshairs
fig_quad.add_vline(x=med_p, line_color=BORDER, line_width=1.5, line_dash="dash")
fig_quad.add_hline(y=med_pol, line_color=BORDER, line_width=1.5, line_dash="dash")

# Zone highlight annotation
fig_quad.add_annotation(
    x=df["Purchasing_Power_Index"].max() * 0.88,
    y=df["Pollution_Index"].min() + 5,
    text="★ The Sweet Spot<br>(High Power · Clean Air)",
    showarrow=False,
    font=dict(color=EMERALD, size=11),
    bgcolor="rgba(85, 184, 154, 0.12)",
    bordercolor=EMERALD,
    borderwidth=1,
    borderpad=6,
)

fig_quad.update_traces(
    marker=dict(opacity=0.85, line=dict(width=0.5, color=BG)),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "Country: %{customdata[0]}<br>"
        "Region: %{customdata[1]}<br>"
        "Purchasing Power: %{x:.1f} (NY=100)<br>"
        "Pollution Index: %{y:.1f} / 100<br>"
        "Cost of Living: %{customdata[2]:.1f}<br>"
        "Data Source: Numbeo Global Benchmark<extra></extra>"
    ),
)
fig_quad.update_layout(
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, title_text=""),
    margin=dict(l=55, r=20, t=75, b=55),
    yaxis=dict(autorange="reversed"),  # Inverted so cleaner air is near the top
)
st.plotly_chart(fig_quad, use_container_width=True)
st.caption(
    "Note: Y-axis is inverted so that **cleaner air (lower pollution) appears at the top**. "
    "Bubble size represents the Cost of Living Index. Dashed lines mark the global medians."
)

st.markdown("<div style='margin-top:1.5rem'>", unsafe_allow_html=True)

# ── 3 Key Automated Findings ──────────────────────────────────────────────────
section_header("Key Statistical Discoveries", "Dynamically calculated from the 238-city observation benchmark.")

f1, f2, f3 = st.columns(3)
clean = kpis["cleanest_city"]
power = kpis["highest_power_city"]
cost = kpis["lowest_cost_city"]

with f1:
    st.markdown(
        f"""
        <div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:12px; padding:18px; height:130px;">
            <div style="font-size:1.4rem; margin-bottom:4px;">🌿</div>
            <div style="font-size:0.72rem; color:{EMERALD}; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Cleanest Environment</div>
            <div style="font-size:1.15rem; font-weight:800; color:{TEXT_PRIMARY}; margin-top:2px;">{clean['name']}, {clean['country']}</div>
            <div style="font-size:0.8rem; color:{TEXT_SECONDARY};">Pollution Index: {clean['pollution']} / 100 (Cleanest globally)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with f2:
    st.markdown(
        f"""
        <div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:12px; padding:18px; height:130px;">
            <div style="font-size:1.4rem; margin-bottom:4px;">💪</div>
            <div style="font-size:0.72rem; color:{CHAMPAGNE}; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Peak Purchasing Power</div>
            <div style="font-size:1.15rem; font-weight:800; color:{TEXT_PRIMARY}; margin-top:2px;">{power['name']}, {power['country']}</div>
            <div style="font-size:0.8rem; color:{TEXT_SECONDARY};">Purchasing Index: {power['power']} (NY = 100)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with f3:
    st.markdown(
        f"""
        <div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:12px; padding:18px; height:130px;">
            <div style="font-size:1.4rem; margin-bottom:4px;">🏷️</div>
            <div style="font-size:0.72rem; color:{EMERALD}; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Lowest Consumer Basket</div>
            <div style="font-size:1.15rem; font-weight:800; color:{TEXT_PRIMARY}; margin-top:2px;">{cost['name']}, {cost['country']}</div>
            <div style="font-size:0.8rem; color:{TEXT_SECONDARY};">Cost Index: {cost['cost']} (Lowest living expenditure)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top:1.5rem'>", unsafe_allow_html=True)

# ── Regional Liveability Landscape ────────────────────────────────────────────
section_header("Regional Liveability Differences", "Actual empirical disparities across world geographic regions.")

reg_agg = (
    df.groupby("Region")
    .agg(
        Cities=("City", "count"),
        Median_Power=("Purchasing_Power_Index", "median"),
        Median_Pollution=("Pollution_Index", "median"),
        Median_Cost=("Cost_of_Living_Index", "median"),
    )
    .reset_index()
    .sort_values(by="Median_Power", ascending=False)
)

fig_reg = px.scatter(
    reg_agg,
    x="Median_Power",
    y="Median_Pollution",
    size="Cities",
    color="Region",
    color_discrete_map=REGION_COLORS,
    text="Region",
    size_max=45,
    hover_data={"Median_Power": ":.1f", "Median_Pollution": ":.1f", "Cities": True},
    labels={
        "Median_Power": "Median Purchasing Power (NY=100)",
        "Median_Pollution": "Median Pollution Index",
    },
)
fig_reg.update_traces(textposition="top center", textfont=dict(size=11, color=TEXT_PRIMARY))
fig_reg.update_layout(
    height=420,
    showlegend=False,
    margin=dict(l=55, r=25, t=40, b=55),
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(fig_reg, use_container_width=True)
st.caption("Bubble size = number of cities in region. Y-axis is inverted so regions with cleaner environments appear higher.")
