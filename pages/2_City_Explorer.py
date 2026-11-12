"""Page 2 — City Explorer: Relationship Explorer, Interactive World Map, and City Passport."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats

from src.data_loader import get_master_data
from src.theme import (
    section_header, semantic_badge,
    EMERALD, CHAMPAGNE, CORAL, SILVER,
    TEXT_PRIMARY, TEXT_SECONDARY, SURFACE, SURFACE_ELEVATED, BORDER,
    REGION_COLORS, BG,
)

df = get_master_data()

st.markdown(
    f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:1.95rem; font-weight:800; margin:0; color:{TEXT_PRIMARY};">🔍 Global City Explorer</h1>
        <p style="color:{TEXT_SECONDARY}; margin:6px 0 0; font-size:0.95rem;">
            Discover, correlate, and profile individual world cities across economic, environmental, and liveability metrics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='color:{CHAMPAGNE}; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;'>FILTERS</div>",
        unsafe_allow_html=True,
    )
    all_regions = sorted(df["Region"].unique())
    sel_regions = st.multiselect("Continent / Region", all_regions, default=all_regions, key="exp_regions")

    avail_countries = sorted(df[df["Region"].isin(sel_regions)]["Country"].unique())
    sel_countries = st.multiselect("Country", avail_countries, default=avail_countries, key="exp_countries")

    city_search = st.text_input("City Search", placeholder="e.g. Zurich, Tokyo, Canberra", key="exp_city_search")

    p_min, p_max = float(df["Purchasing_Power_Index"].min()), float(df["Purchasing_Power_Index"].max())
    p_range = st.slider("Purchasing Power Range", p_min, p_max, (p_min, p_max), step=1.0, key="exp_p_range")

    c_min, c_max = float(df["Cost_of_Living_Index"].min()), float(df["Cost_of_Living_Index"].max())
    c_range = st.slider("Cost of Living Range", c_min, c_max, (c_min, c_max), step=1.0, key="exp_c_range")

    pol_min, pol_max = float(df["Pollution_Index"].min()), float(df["Pollution_Index"].max())
    pol_range = st.slider("Pollution Index Range", pol_min, pol_max, (pol_min, pol_max), step=1.0, key="exp_pol_range")

    with st.expander("Advanced Social Filters (Safety & Health)"):
        safe_min_filter = st.slider("Minimum Safety Score", 0.0, 100.0, 0.0, step=5.0, key="exp_safe_min")
        health_min_filter = st.slider("Minimum Healthcare Score", 0.0, 100.0, 0.0, step=5.0, key="exp_health_min")

# ── Filter Application ────────────────────────────────────────────────────────
fdf = df.copy()
if sel_regions:
    fdf = fdf[fdf["Region"].isin(sel_regions)]
if sel_countries:
    fdf = fdf[fdf["Country"].isin(sel_countries)]

fdf = fdf[
    (fdf["Purchasing_Power_Index"] >= p_range[0]) &
    (fdf["Purchasing_Power_Index"] <= p_range[1]) &
    (fdf["Cost_of_Living_Index"] >= c_range[0]) &
    (fdf["Cost_of_Living_Index"] <= c_range[1]) &
    (fdf["Pollution_Index"] >= pol_range[0]) &
    (fdf["Pollution_Index"] <= pol_range[1]) &
    (fdf["Safety_Index"] >= safe_min_filter) &
    (fdf["Health_Care_Index"] >= health_min_filter)
]

if city_search.strip():
    q = city_search.strip().lower()
    fdf = fdf[fdf["City"].str.lower().str.contains(q) | fdf["Country"].str.lower().str.contains(q)]

st.markdown(
    f"<div style='margin-bottom:1rem; font-size:0.86rem; color:{TEXT_SECONDARY};'>"
    f"Displaying <strong style='color:{TEXT_PRIMARY};'>{len(fdf)}</strong> of {len(df)} verified global cities</div>",
    unsafe_allow_html=True,
)

if fdf.empty:
    st.warning("No cities match your filter parameters. Please widen the filter ranges in the sidebar.")
    st.stop()

# ── Primary Exploration Views ─────────────────────────────────────────────────
tab_scatter, tab_map = st.tabs(["📊 City Relationship Explorer", "🗺️ Global 238-City World Map"])

METRICS_DICT = {
    "Purchasing_Power_Index": "Local Purchasing Power (NY=100)",
    "Cost_of_Living_Index": "Cost of Living (NY=100)",
    "Quality_of_Life_Index": "Quality of Life Index",
    "Safety_Index": "Safety Index (0-100)",
    "Health_Care_Index": "Healthcare Quality Score",
    "Property_Price_to_Income_Ratio": "Property Price to Income Ratio",
    "Traffic_Commute_Time_Index": "Traffic Commute Time Index",
    "Pollution_Index": "Pollution Index (Lower is Cleaner)",
    "Climate_Index": "Climate Comfort Score",
}

with tab_scatter:
    c_x, c_y, c_group, c_trend = st.columns([1, 1, 1, 1])
    with c_x:
        x_var = st.selectbox("X-Axis Variable", list(METRICS_DICT.keys()), index=0, format_func=lambda k: METRICS_DICT[k], key="rel_x")
    with c_y:
        y_var = st.selectbox("Y-Axis Variable", list(METRICS_DICT.keys()), index=7, format_func=lambda k: METRICS_DICT[k], key="rel_y")
    with c_group:
        color_by = st.selectbox("Color Group", ["Region", "Liveability_Zone"], index=0, key="rel_color")
    with c_trend:
        add_trend = st.checkbox("Show OLS Trendline", value=True, key="rel_trend")

    log_x = st.checkbox("Logarithmic scale for X-axis", value=False, key="rel_log_x")

    fig_rel = px.scatter(
        fdf,
        x=x_var,
        y=y_var,
        color=color_by,
        color_discrete_map=REGION_COLORS if color_by == "Region" else None,
        size="Cost_of_Living_Index",
        size_max=18,
        log_x=log_x,
        hover_name="City",
        hover_data={
            "Country": True,
            "Region": True,
            x_var: ":.1f",
            y_var: ":.1f",
            "Cost_of_Living_Index": ":.1f",
        },
        labels={
            x_var: METRICS_DICT[x_var] + (" [Log Scale]" if log_x else ""),
            y_var: METRICS_DICT[y_var],
            "Cost_of_Living_Index": "Cost of Living",
        },
    )
    if add_trend and len(fdf) >= 3:
        clean_pts = fdf[[x_var, y_var]].dropna()
        if len(clean_pts) >= 3:
            x_pts = clean_pts[x_var].values
            y_pts = clean_pts[y_var].values
            p_slope, p_intercept = np.polyfit(x_pts, y_pts, 1)
            x_line = np.linspace(x_pts.min(), x_pts.max(), 50)
            y_line = p_slope * x_line + p_intercept
            fig_rel.add_trace(
                go.Scatter(
                    x=x_line, y=y_line,
                    mode="lines",
                    line=dict(color=CHAMPAGNE, dash="dot", width=2),
                    name=f"OLS Trend (slope: {p_slope:.3f})",
                )
            )
    fig_rel.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color=BG)))
    fig_rel.update_layout(
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, title_text=""),
        margin=dict(l=55, r=20, t=75, b=55),
    )
    st.plotly_chart(fig_rel, use_container_width=True)
    st.caption("Bubble size = Cost of Living. Use box-select or lasso in the chart toolbar to inspect subsets.")

with tab_map:
    map_metric = st.selectbox(
        "Colour markers by",
        options=list(METRICS_DICT.keys()),
        index=0,
        format_func=lambda k: METRICS_DICT[k],
        key="map_metric_sel",
    )
    reverse_c = map_metric in ["Pollution_Index", "Property_Price_to_Income_Ratio", "Traffic_Commute_Time_Index"]
    cscale = "RdYlGn_r" if reverse_c else "RdYlGn"

    fig_map = px.scatter_geo(
        fdf,
        lat="Latitude",
        lon="Longitude",
        color=map_metric,
        size="Cost_of_Living_Index",
        size_max=16,
        color_continuous_scale=cscale,
        hover_name="City",
        hover_data={
            "Country": True,
            "Region": True,
            map_metric: ":.1f",
            "Purchasing_Power_Index": ":.1f",
            "Cost_of_Living_Index": ":.1f",
        },
        projection="natural earth",
        labels={map_metric: METRICS_DICT[map_metric]},
    )
    fig_map.update_geos(
        showcoastlines=True, coastlinecolor=BORDER,
        showland=True, landcolor=SURFACE,
        showocean=True, oceancolor="#07090C",
        showcountries=True, countrycolor=BORDER,
    )
    fig_map.update_layout(
        height=540,
        margin=dict(l=0, r=0, t=15, b=0),
        coloraxis_colorbar=dict(
            title=dict(font=dict(color=TEXT_SECONDARY, size=11)),
            tickfont=dict(color=TEXT_SECONDARY),
        ),
        geo=dict(bgcolor=BG),
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ── City Passport ─────────────────────────────────────────────────────────────
st.markdown("---")
section_header("🪪 City Passport & Diagnostic Profile", "Detailed performance scorecard for individual global cities.")

city_opts = sorted(fdf["City"].unique())
sel_city = st.selectbox("Select a city to inspect", city_opts, key="pass_city")
row = fdf[fdf["City"] == sel_city].iloc[0]

# Compute valid percentile comparisons across all 238 cities
p_pct = int(stats.percentileofscore(df["Purchasing_Power_Index"], row["Purchasing_Power_Index"]))
qol_pct = int(stats.percentileofscore(df["Quality_of_Life_Index"], row["Quality_of_Life_Index"]))
safe_pct = int(stats.percentileofscore(df["Safety_Index"], row["Safety_Index"]))

col_p1, col_p2, col_p3 = st.columns([1, 1, 1])

with col_p1:
    st.markdown(
        f"""
        <div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:14px; padding:22px; height:100%;">
            <div style="font-size:2rem; font-weight:800; color:{TEXT_PRIMARY};">{row['City']}</div>
            <div style="color:{TEXT_SECONDARY}; font-size:0.95rem; margin-top:2px;">{row['Country']} · {row['Region']}</div>
            <div style="font-size:0.75rem; color:{SILVER}; margin-top:4px;">Lat: {row['Latitude']:.2f} · Lon: {row['Longitude']:.2f}</div>
            <hr style="border-color:{BORDER}; margin:14px 0;">
            <div style="font-size:0.72rem; color:{CHAMPAGNE}; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">LIVEABILITY TIER</div>
            <div style="font-size:1.1rem; font-weight:700; color:{EMERALD};">{row['Liveability_Zone']}</div>
            <div style="margin-top:12px; display:flex; gap:6px; flex-wrap:wrap;">
                {semantic_badge(f"Quality of Life: {row['Quality_of_Life_Index']:.1f} ({qol_pct}th %ile)", CHAMPAGNE)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _passport_row(lbl, val, unit="", col=TEXT_PRIMARY):
    return (
        f'<div style="display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid {BORDER};">'
        f'<span style="color:{TEXT_SECONDARY}; font-size:0.85rem;">{lbl}</span>'
        f'<span style="color:{col}; font-weight:600; font-family:\'JetBrains Mono\', monospace;">{val}{unit}</span>'
        f'</div>'
    )

with col_p2:
    afford_content = (
        _passport_row("Purchasing Power", f"{row['Purchasing_Power_Index']:.1f}", f" ({p_pct}th %ile)", CHAMPAGNE)
        + _passport_row("Cost of Living", f"{row['Cost_of_Living_Index']:.1f}", " (NY=100)")
        + _passport_row("House Price / Income", f"{row['Property_Price_to_Income_Ratio']:.1f}×", " income",
                      EMERALD if row['Property_Price_to_Income_Ratio'] < 10 else CORAL)
        + _passport_row("National GDP/Capita", f"${row['GDP_Per_Capita_USD']:,.0f}", "", SILVER)
    )
    st.markdown(
        f'<div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:14px; padding:18px 20px;">'
        f'<div style="font-size:0.72rem; color:{CHAMPAGNE}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">💰 Economic & Housing</div>'
        f'{afford_content}</div>',
        unsafe_allow_html=True,
    )

with col_p3:
    pol_c = EMERALD if row['Pollution_Index'] < 35 else (CHAMPAGNE if row['Pollution_Index'] < 60 else CORAL)
    live_content = (
        _passport_row("Pollution Index", f"{row['Pollution_Index']:.1f}", " / 100", pol_c)
        + _passport_row("Safety Index", f"{row['Safety_Index']:.1f}", f" ({safe_pct}th %ile)", EMERALD if row['Safety_Index'] >= 60 else CHAMPAGNE)
        + _passport_row("Healthcare Score", f"{row['Health_Care_Index']:.1f}", " / 100", EMERALD)
        + _passport_row("Traffic Commute Time", f"{row['Traffic_Commute_Time_Index']:.1f}", " mins", CORAL if row['Traffic_Commute_Time_Index'] > 45 else CHAMPAGNE)
    )
    st.markdown(
        f'<div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:14px; padding:18px 20px;">'
        f'<div style="font-size:0.72rem; color:{pol_c}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">🌿 Environment & Society</div>'
        f'{live_content}</div>',
        unsafe_allow_html=True,
    )
