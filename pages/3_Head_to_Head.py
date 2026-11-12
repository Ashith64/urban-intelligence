"""Page 3 — Head-to-Head Comparison: Multi-city arena, radar profiles, and lifestyle presets."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.data_loader import get_master_data
from src.analysis import calculate_preset_ranking
from src.theme import (
    section_header, semantic_badge,
    EMERALD, CHAMPAGNE, CORAL, SILVER,
    TEXT_PRIMARY, TEXT_SECONDARY, SURFACE, SURFACE_ELEVATED, BORDER, BG,
)

df = get_master_data()

st.markdown(
    f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:1.95rem; font-weight:800; margin:0; color:{TEXT_PRIMARY};">⚔️ Head-to-Head Comparison Arena</h1>
        <p style="color:{TEXT_SECONDARY}; margin:6px 0 0; font-size:0.95rem;">
            Direct side-by-side indicator benchmarking, multi-axis radar profiles, and customizable lifestyle scenario weighting.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── City Contender Selector ───────────────────────────────────────────────────
all_cities = sorted(df["City"].unique())
default_picks = [c for c in ["Zurich", "Tokyo", "London", "New York"] if c in all_cities][:3]
if not default_picks:
    default_picks = all_cities[:3]

selected_cities = st.multiselect(
    "Select 2 to 4 cities to compare",
    options=all_cities,
    default=default_picks,
    max_selections=4,
    help="Choose between 2 and 4 global cities to enter the comparison arena.",
)

if len(selected_cities) < 2:
    st.info("💡 Please choose at least 2 cities from the dropdown above to begin the head-to-head comparison.")
    st.stop()

comp_df = df[df["City"].isin(selected_cities)].copy()
comp_df["__order"] = comp_df["City"].map(lambda c: selected_cities.index(c))
comp_df = comp_df.sort_values("__order").reset_index(drop=True)

# ── 1. Summary Comparison Cards ───────────────────────────────────────────────
PALETTE = [CHAMPAGNE, EMERALD, "#68A4C4", CORAL]
card_cols = st.columns(len(selected_cities))

for i, (_, row) in enumerate(comp_df.iterrows()):
    col_color = PALETTE[i % len(PALETTE)]
    with card_cols[i]:
        pol_col = EMERALD if row["Pollution_Index"] < 35 else (CHAMPAGNE if row["Pollution_Index"] < 60 else CORAL)
        st.markdown(
            f"""
            <div style="
                background: {SURFACE};
                border: 1px solid {BORDER};
                border-top: 4px solid {col_color};
                border-radius: 12px;
                padding: 18px;
                margin-bottom: 1rem;
                box-shadow: 0 4px 18px rgba(0,0,0,0.25);
            ">
                <div style="font-size:0.72rem; font-weight:700; color:{col_color}; text-transform:uppercase; letter-spacing:0.08em;">
                    Contender #{i+1}
                </div>
                <div style="font-size:1.45rem; font-weight:800; color:{TEXT_PRIMARY}; margin: 4px 0 2px;">
                    {row['City']}
                </div>
                <div style="font-size:0.84rem; color:{TEXT_SECONDARY}; margin-bottom:12px;">
                    {row['Country']} · {row['Region']}
                </div>

                <div style="display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid {BORDER}; font-size:0.84rem;">
                    <span style="color:{TEXT_SECONDARY};">Purchasing Power</span>
                    <span style="color:{CHAMPAGNE}; font-weight:700; font-family:'JetBrains Mono', monospace;">{row['Purchasing_Power_Index']:.1f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid {BORDER}; font-size:0.84rem;">
                    <span style="color:{TEXT_SECONDARY};">Cost of Living</span>
                    <span style="color:{TEXT_PRIMARY}; font-weight:600; font-family:'JetBrains Mono', monospace;">{row['Cost_of_Living_Index']:.1f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid {BORDER}; font-size:0.84rem;">
                    <span style="color:{TEXT_SECONDARY};">Pollution Index</span>
                    <span style="color:{pol_col}; font-weight:700; font-family:'JetBrains Mono', monospace;">{row['Pollution_Index']:.1f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid {BORDER}; font-size:0.84rem;">
                    <span style="color:{TEXT_SECONDARY};">Safety Score</span>
                    <span style="color:{EMERALD}; font-weight:600; font-family:'JetBrains Mono', monospace;">{row['Safety_Index']:.1f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:5px 0; border-top:1px solid {BORDER}; font-size:0.84rem;">
                    <span style="color:{TEXT_SECONDARY};">House Price/Income</span>
                    <span style="color:{TEXT_PRIMARY}; font-weight:600; font-family:'JetBrains Mono', monospace;">{row['Property_Price_to_Income_Ratio']:.1f}×</span>
                </div>
                <div style="margin-top:10px;">
                    {semantic_badge(row['Liveability_Zone'], col_color)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Visual Comparison Tabs ────────────────────────────────────────────────────
tab_grouped, tab_table, tab_radar, tab_delta = st.tabs([
    "📊 Grouped Bar Comparison",
    "📋 Indicator Comparison Table",
    "🕸️ Multidimensional Radar Profile",
    "⚖️ Benchmark Variance Matrix",
])

with tab_grouped:
    section_header("Direct Metric Comparison", "Side-by-side indicator performance for chosen metropolises.")
    metrics_list = [
        ("Purchasing_Power_Index", "Purchasing Power (NY=100)"),
        ("Cost_of_Living_Index", "Cost of Living (NY=100)"),
        ("Safety_Index", "Safety Score (0-100)"),
        ("Health_Care_Index", "Healthcare Quality (0-100)"),
        ("Pollution_Index", "Pollution Index (Lower is Better)"),
        ("Property_Price_to_Income_Ratio", "House Price/Income Multiple"),
    ]
    plot_rows = []
    for _, r in comp_df.iterrows():
        for col_name, label in metrics_list:
            plot_rows.append({
                "City": r["City"],
                "Indicator": label,
                "Value": r[col_name],
            })

    fig_bar = px.bar(
        pd.DataFrame(plot_rows),
        x="Indicator",
        y="Value",
        color="City",
        barmode="group",
        color_discrete_sequence=PALETTE[:len(selected_cities)],
        hover_data={"Value": ":.1f"},
    )
    fig_bar.update_layout(
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        margin=dict(l=45, r=20, t=75, b=60),
        xaxis_title="",
        yaxis_title="Indicator Value",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_table:
    section_header("Side-by-Side Indicator Table", "Exact numeric levels for all verified city-level indicators.")
    disp_cols_table = [
        "Purchasing_Power_Index", "Cost_of_Living_Index", "Quality_of_Life_Index",
        "Property_Price_to_Income_Ratio", "Safety_Index", "Health_Care_Index",
        "Pollution_Index", "Traffic_Commute_Time_Index", "Climate_Index",
    ]
    labels_table = {
        "Purchasing_Power_Index": "Purchasing Power (NY=100)",
        "Cost_of_Living_Index": "Cost of Living (NY=100)",
        "Quality_of_Life_Index": "Quality of Life Index",
        "Property_Price_to_Income_Ratio": "House Price / Income Multiple",
        "Safety_Index": "Safety Score (0-100)",
        "Health_Care_Index": "Healthcare Quality (0-100)",
        "Pollution_Index": "Pollution Index (0-100)",
        "Traffic_Commute_Time_Index": "Traffic Commute (Mins)",
        "Climate_Index": "Climate Comfort Index",
    }
    table_df = comp_df[["City"] + disp_cols_table].set_index("City").T
    table_df.index = [labels_table.get(idx, idx) for idx in table_df.index]
    st.dataframe(table_df, use_container_width=True)

with tab_radar:
    section_header(
        "Multidimensional Radar Profile (Advanced)",
        "Overlaid spider polygons across 6 normalized indicators (0.0 = global minimum, 1.0 = global maximum). All metrics oriented positively."
    )
    radar_axes = [
        ("Purchasing_Power_Index_norm", "Purchasing Power"),
        ("Cost_of_Living_Index_norm", "Cost of Living"),
        ("Safety_Index_norm", "Safety"),
        ("Health_Care_Index_norm", "Healthcare Quality"),
        ("Clean_Environment_norm", "Clean Environment"),
        ("Housing_Affordability_norm", "Housing Affordability"),
    ]
    radar_labels = [a[1] for a in radar_axes]

    fig_radar = go.Figure()
    for idx, (_, row) in enumerate(comp_df.iterrows()):
        vals = [row[a[0]] for a in radar_axes]
        vals_loop = vals + [vals[0]]
        cats_loop = radar_labels + [radar_labels[0]]

        color = PALETTE[idx % len(PALETTE)]
        h = color.lstrip("#")
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        fig_radar.add_trace(
            go.Scatterpolar(
                r=vals_loop,
                theta=cats_loop,
                fill="toself",
                fillcolor=f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.20)",
                line=dict(color=color, width=2.5),
                name=row["City"],
            )
        )

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=10, color=TEXT_SECONDARY), gridcolor=BORDER),
            angularaxis=dict(gridcolor=BORDER, tickfont=dict(size=11, color=TEXT_PRIMARY)),
            bgcolor=SURFACE_ELEVATED,
        ),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text=""),
        margin=dict(l=60, r=60, t=75, b=60),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab_delta:
    base_city = selected_cities[0]
    section_header(f"Variance Matrix vs Benchmark: {base_city}", "Percentage variance (±%) in key metrics relative to the benchmark city.")
    benchmark = comp_df.iloc[0]

    indicators_delta = [
        ("Purchasing_Power_Index", "Purchasing Power"),
        ("Cost_of_Living_Index", "Cost of Living"),
        ("Pollution_Index", "Pollution"),
        ("Safety_Index", "Safety"),
        ("Health_Care_Index", "Healthcare"),
        ("Property_Price_to_Income_Ratio", "House Price/Income"),
    ]

    comp_matrix = []
    for _, r in comp_df.iterrows():
        row_dict = {"City": r["City"]}
        for col_name, lbl in indicators_delta:
            base_v = benchmark[col_name]
            curr_v = r[col_name]
            diff_pct = ((curr_v - base_v) / base_v) * 100.0 if base_v != 0 else 0
            if r["City"] == benchmark["City"]:
                row_dict[lbl] = "Benchmark (Base)"
            else:
                sign = "+" if diff_pct > 0 else ""
                row_dict[lbl] = f"{curr_v:.1f} ({sign}{diff_pct:.1f}%)"
        comp_matrix.append(row_dict)

    st.dataframe(pd.DataFrame(comp_matrix), use_container_width=True, hide_index=True)

# ── 7. Interactive Lifestyle What-If Simulator ─────────────────────────────────
st.markdown("---")
section_header(
    "🎛️ Interactive Lifestyle Scenario Simulator",
    "Choose a ready-made lifestyle priority preset or adjust custom sliders to simulate personalized global rankings."
)

col_preset, col_sliders = st.columns([1, 2])

with col_preset:
    preset_choice = st.radio(
        "Ready-Made Weighting Presets",
        ["Affordability First", "Environment First", "Balanced Priorities", "Custom Weights"],
        index=2,
        key="preset_choice",
        help="Presets automatically assign normalized weights across economic, environmental, and social dimensions.",
    )
    st.markdown(
        f"""
        <div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px; padding:12px; margin-top:10px; font-size:0.8rem; color:{TEXT_SECONDARY}; line-height:1.4;">
            <strong>Important Notice:</strong> Custom scenario scores are illustrative user-defined models. They do not constitute official city liveability rankings.
        </div>
        """,
        unsafe_allow_html=True,
    )

custom_weights = {}
with col_sliders:
    if preset_choice == "Custom Weights":
        st.markdown("**Adjust Custom Normalized Weights:**")
        w_p = st.slider("💰 Purchasing Power Weight", 0.0, 1.0, 0.35, 0.05, key="w_p_sl")
        w_air = st.slider("🌿 Clean Environment Weight", 0.0, 1.0, 0.25, 0.05, key="w_air_sl")
        w_safe = st.slider("🛡️ Safety & Security Weight", 0.0, 1.0, 0.15, 0.05, key="w_safe_sl")
        w_health = st.slider("🩺 Healthcare Quality Weight", 0.0, 1.0, 0.15, 0.05, key="w_health_sl")
        w_house = st.slider("🏠 Housing Affordability Weight", 0.0, 1.0, 0.10, 0.05, key="w_house_sl")
        custom_weights = {"purchasing": w_p, "environment": w_air, "safety": w_safe, "health": w_health, "housing": w_house}
    else:
        st.markdown(f"**Preset Selected: {preset_choice}**")
        st.markdown(
            """
            - **Affordability First**: High emphasis on high wages and accessible housing (50% Purchasing Power, 30% Housing).
            - **Environment First**: High emphasis on clean air, mild climate, and healthcare (50% Clean Environment, 25% Climate).
            - **Balanced Priorities**: Equal distribution across economic power, environmental cleanliness, safety, and healthcare (25% each).
            """
        )

# Recalculate ranking immediately
df_ranked = calculate_preset_ranking(df, preset=preset_choice, custom_weights=custom_weights)
sim_sub = df_ranked[df_ranked["City"].isin(selected_cities)].sort_values("Custom_Rank")

st.markdown(f"<div style='margin:1.2rem 0 0.6rem; font-weight:700; color:{TEXT_PRIMARY}; font-size:0.95rem;'>Rankings for Selected Cities under Current Lifestyle Scenario:</div>", unsafe_allow_html=True)

res_cols = st.columns(len(selected_cities))
for i, (_, srow) in enumerate(sim_sub.iterrows()):
    with res_cols[i]:
        st.markdown(
            f"""
            <div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:12px; padding:16px; text-align:center;">
                <div style="font-size:0.75rem; color:{CHAMPAGNE}; font-weight:700;">SCENARIO RANK #{srow['Custom_Rank']}</div>
                <div style="font-size:1.35rem; font-weight:800; color:{TEXT_PRIMARY}; margin:4px 0;">{srow['City']}</div>
                <div style="font-size:1.85rem; font-weight:800; color:{EMERALD}; font-family:'JetBrains Mono', monospace;">
                    {srow['Custom_Score']:.1f}<span style="font-size:0.85rem; color:{TEXT_SECONDARY};"> / 100</span>
                </div>
                <div style="font-size:0.75rem; color:{TEXT_SECONDARY}; margin-top:4px;">Ranked #{srow['Custom_Rank']} of {len(df_ranked)} global cities</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
