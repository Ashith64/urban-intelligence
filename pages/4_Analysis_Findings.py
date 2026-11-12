"""Page 4 — Analysis & Findings: Comprehensive Interactive Analytical Workspace.

Modules:
- Section A: Discovery Feed (automated real-time findings with metadata)
- Section B: Statistical Overview (12 summary statistics + distribution chart)
- Section C: Relationship Explorer (bivariate regression, Pearson r, Spearman rho, causality disclaimer)
- Section D: Correlation Studio (Pearson & Spearman heatmaps with constituent safeguards)
- Section E: Distribution Lab (Histogram, Box plot, Violin plot, KDE across regions)
- Section F: Regional Intelligence (Ranked continental scorecards)
- Section G: Custom Visualization Studio (user-built charts with 7 chart types, filters, and HTML export)
"""
import io
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.data_loader import get_master_data
from src.analysis import (
    calculate_univariate_stats,
    generate_discovery_feed,
    compute_bivariate_analysis,
    compute_correlation_matrix_filtered,
)
from src.theme import (
    section_header, discovery_card, semantic_badge,
    EMERALD, CHAMPAGNE, CORAL, SILVER,
    TEXT_PRIMARY, TEXT_SECONDARY, SURFACE, SURFACE_ELEVATED, BORDER, REGION_COLORS, BG,
)

df = get_master_data()

st.markdown(
    f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:2rem; font-weight:800; margin:0; color:{TEXT_PRIMARY};">🔬 Analysis & Analytical Findings</h1>
        <p style="color:{TEXT_SECONDARY}; margin:6px 0 0; font-size:0.95rem;">
            A unified analytical intelligence workspace combining automated statistical discoveries, distribution labs, and user-driven chart synthesis.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

ANALYSIS_METRICS = {
    "Purchasing_Power_Index": "Local Purchasing Power Index",
    "Cost_of_Living_Index": "Cost of Living Index",
    "Property_Price_to_Income_Ratio": "Property Price to Income Ratio",
    "Pollution_Index": "Pollution Index",
    "Safety_Index": "Safety Score",
    "Health_Care_Index": "Health Care Quality Index",
    "Traffic_Commute_Time_Index": "Traffic Commute Time Index",
    "Climate_Index": "Climate Comfort Score",
    "Quality_of_Life_Index": "Quality of Life Index (Composite)",
    "GDP_Per_Capita_USD": "National GDP per Capita (USD)",
    "Life_Expectancy_Years": "National Life Expectancy (Years)",
}

# ── Primary Analytical Tabs ───────────────────────────────────────────────────
t_feed, t_stats, t_rel, t_corr, t_dist, t_reg, t_studio = st.tabs([
    "💡 Discovery Feed",
    "📐 Statistical Overview",
    "📈 Relationship Explorer",
    "🔥 Correlation Studio",
    "📦 Distribution Lab",
    "🌐 Regional Intelligence",
    "🎨 Custom Studio",
])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION A — DISCOVERY FEED
# ══════════════════════════════════════════════════════════════════════════════
with t_feed:
    section_header(
        "Automated Statistical Discovery Feed",
        "Algorithmic findings computed directly from the 238-city master dataset. Displays calculated results, sample sizes, and source observation periods."
    )
    discoveries = generate_discovery_feed(df)

    # Display primary 4 findings
    feed_cols1, feed_cols2 = st.columns(2)
    for i in range(min(4, len(discoveries))):
        col = feed_cols1 if i % 2 == 0 else feed_cols2
        d = discoveries[i]
        with col:
            st.markdown(
                discovery_card(d["title"], d["metric_value"], d["badge"], d["explanation"], d["sample_size"], d["source"]),
                unsafe_allow_html=True,
            )

    # Expandable drawer for further discoveries
    if len(discoveries) > 4:
        with st.expander("Show Additional Statistical Discoveries"):
            extra_cols1, extra_cols2 = st.columns(2)
            for j in range(4, len(discoveries)):
                col_extra = extra_cols1 if j % 2 == 0 else extra_cols2
                d_extra = discoveries[j]
                with col_extra:
                    st.markdown(
                        discovery_card(d_extra["title"], d_extra["metric_value"], d_extra["badge"], d_extra["explanation"], d_extra["sample_size"], d_extra["source"]),
                        unsafe_allow_html=True,
                    )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION B — STATISTICAL OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with t_stats:
    section_header("Univariate Statistical Overview", "Examine 12 descriptive metrics across any numerical urban indicator.")

    stat_var = st.selectbox(
        "Select Numerical Indicator",
        options=list(ANALYSIS_METRICS.keys()),
        index=0,
        format_func=lambda k: ANALYSIS_METRICS[k],
        key="stat_var_sel",
    )

    stats_dict = calculate_univariate_stats(df[stat_var])

    # Display 12 metrics in clean grid
    grid_cols = st.columns(4)
    stat_keys = list(stats_dict.keys())
    for idx, k in enumerate(stat_keys):
        c = grid_cols[idx % 4]
        with c:
            st.markdown(
                f"""
                <div style="background:{SURFACE}; border:1px solid {BORDER}; border-radius:10px; padding:12px; margin-bottom:8px;">
                    <div style="font-size:0.72rem; color:{SILVER}; font-weight:700; text-transform:uppercase;">{k}</div>
                    <div style="font-size:1.4rem; font-weight:800; color:{TEXT_PRIMARY}; font-family:'JetBrains Mono', monospace; margin-top:2px;">
                        {stats_dict[k]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:1rem;'>", unsafe_allow_html=True)
    # Distribution chart with mean and median
    fig_hist = px.histogram(
        df,
        x=stat_var,
        nbins=25,
        color_discrete_sequence=[CHAMPAGNE],
        labels={stat_var: ANALYSIS_METRICS[stat_var]},
        title=f"Sample Distribution: {ANALYSIS_METRICS[stat_var]} (N = {len(df)})",
    )
    mean_val = float(df[stat_var].mean())
    median_val = float(df[stat_var].median())
    fig_hist.add_vline(x=mean_val, line_dash="dash", line_color=EMERALD, annotation_text=f"Mean: {mean_val:.1f}")
    fig_hist.add_vline(x=median_val, line_dash="dot", line_color=CORAL, annotation_text=f"Median: {median_val:.1f}")
    fig_hist.update_layout(height=380, margin=dict(l=45, r=20, t=65, b=50))
    st.plotly_chart(fig_hist, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION C — RELATIONSHIP EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with t_rel:
    section_header(
        "Bivariate Relationship Explorer",
        "Investigate mathematical correlations between indicator pairs with linear regression and analytical takeaways."
    )

    r_c1, r_c2, r_c3, r_c4 = st.columns(4)
    with r_c1:
        biv_x = st.selectbox("Independent Variable (X)", list(ANALYSIS_METRICS.keys()), index=0, format_func=lambda k: ANALYSIS_METRICS[k], key="biv_x")
    with r_c2:
        biv_y = st.selectbox("Dependent Variable (Y)", list(ANALYSIS_METRICS.keys()), index=1, format_func=lambda k: ANALYSIS_METRICS[k], key="biv_y")
    with r_c3:
        biv_reg = st.selectbox("Filter Region", ["All Continents"] + sorted(df["Region"].unique().tolist()), key="biv_reg")
    with r_c4:
        biv_trend = st.checkbox("Fit OLS Line", value=True, key="biv_trend")

    biv_df = df.copy()
    if biv_reg != "All Continents":
        biv_df = biv_df[biv_df["Region"] == biv_reg]

    biv_results = compute_bivariate_analysis(biv_df, biv_x, biv_y)

    fig_biv = px.scatter(
        biv_df,
        x=biv_x,
        y=biv_y,
        color="Region",
        color_discrete_map=REGION_COLORS,
        size="Cost_of_Living_Index",
        size_max=18,
        hover_name="City",
        hover_data={"Country": True, biv_x: ":.1f", biv_y: ":.1f"},
        labels={biv_x: ANALYSIS_METRICS[biv_x], biv_y: ANALYSIS_METRICS[biv_y]},
    )
    if biv_trend and biv_results["n"] >= 3:
        clean_biv = biv_df[[biv_x, biv_y]].dropna()
        x_min, x_max = clean_biv[biv_x].min(), clean_biv[biv_x].max()
        x_trend = np.linspace(x_min, x_max, 50)
        y_trend = biv_results["slope"] * x_trend + biv_results["intercept"]
        fig_biv.add_trace(
            go.Scatter(
                x=x_trend, y=y_trend,
                mode="lines",
                line=dict(color=CHAMPAGNE, dash="dot", width=2),
                name=f"OLS Fit (slope: {biv_results['slope']:.3f})",
            )
        )
    fig_biv.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color=BG)))
    fig_biv.update_layout(height=480, margin=dict(l=55, r=20, t=65, b=55))
    st.plotly_chart(fig_biv, use_container_width=True)

    # Textual interpretation callout with strict causality disclaimer
    st.info(f"📊 **Statistical Finding:** {biv_results['interpretation']}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION D — CORRELATION STUDIO
# ══════════════════════════════════════════════════════════════════════════════
with t_corr:
    section_header(
        "Correlation Studio",
        "Pairwise linear (Pearson) and monotonic rank (Spearman) relationship matrices across all numerical indicators."
    )

    corr_method = st.radio("Correlation Method", ["pearson", "spearman"], format_func=lambda m: "Pearson (Linear Co-movement)" if m == "pearson" else "Spearman (Rank Order Monotonicity)", horizontal=True, key="corr_method_rad")

    corr_candidates = [
        "Purchasing_Power_Index", "Cost_of_Living_Index", "Property_Price_to_Income_Ratio",
        "Pollution_Index", "Safety_Index", "Health_Care_Index", "Traffic_Commute_Time_Index",
        "Climate_Index", "GDP_Per_Capita_USD", "Life_Expectancy_Years"
    ]
    # Safeguard: Do not include Quality_of_Life_Index in correlation with its own constituents
    corr_matrix = compute_correlation_matrix_filtered(df, columns=corr_candidates, method=corr_method)
    short_labels = [ANALYSIS_METRICS.get(c, c) for c in corr_candidates]

    fig_corr = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=short_labels,
            y=short_labels,
            colorscale="RdBu_r",
            zmin=-1.0,
            zmax=1.0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 11, "color": TEXT_PRIMARY},
            hoverongaps=False,
        )
    )
    fig_corr.update_layout(
        height=520,
        margin=dict(l=150, r=30, t=50, b=100),
        xaxis=dict(automargin=True, tickangle=-25),
        yaxis=dict(automargin=True),
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    st.caption("Values range from -1.0 (inverse correlation) to +1.0 (direct correlation). Composite indicators are excluded from self-correlations.")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION E — DISTRIBUTION LAB
# ══════════════════════════════════════════════════════════════════════════════
with t_dist:
    section_header("Distribution Lab", "Inspect dispersion, skewness, multimodal characteristics, and outliers across world regions.")

    d_var = st.selectbox("Indicator to Examine", list(ANALYSIS_METRICS.keys()), index=0, format_func=lambda k: ANALYSIS_METRICS[k], key="dist_var_sel")
    d_type = st.radio("Distribution Visualization", ["Box Plot by Region", "Violin Plot (Density Profile)", "Multi-Region KDE Histogram"], horizontal=True, key="dist_plot_type")

    if d_type == "Box Plot by Region":
        fig_dist = px.box(
            df,
            x="Region",
            y=d_var,
            color="Region",
            color_discrete_map=REGION_COLORS,
            points="all",
            hover_name="City",
            labels={d_var: ANALYSIS_METRICS[d_var]},
            title=f"Dispersion and Outliers: {ANALYSIS_METRICS[d_var]} by Region",
        )
    elif d_type == "Violin Plot (Density Profile)":
        fig_dist = px.violin(
            df,
            x="Region",
            y=d_var,
            color="Region",
            color_discrete_map=REGION_COLORS,
            box=True,
            points="all",
            hover_name="City",
            labels={d_var: ANALYSIS_METRICS[d_var]},
            title=f"Probability Density Violin Profile: {ANALYSIS_METRICS[d_var]}",
        )
    else:
        fig_dist = px.histogram(
            df,
            x=d_var,
            color="Region",
            color_discrete_map=REGION_COLORS,
            barmode="overlay",
            opacity=0.65,
            labels={d_var: ANALYSIS_METRICS[d_var]},
            title=f"Histogram Overlay by Region: {ANALYSIS_METRICS[d_var]}",
        )

    fig_dist.update_layout(height=480, margin=dict(l=55, r=20, t=65, b=60))
    st.plotly_chart(fig_dist, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION F — REGIONAL INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with t_reg:
    section_header("Regional Intelligence Scorecards", "Empirical medians, city counts, and housing affordability comparisons by continent.")

    reg_metric = st.selectbox("Compare Regions by Indicator", list(ANALYSIS_METRICS.keys()), index=0, format_func=lambda k: ANALYSIS_METRICS[k], key="reg_intel_metric")

    reg_summary = (
        df.groupby("Region")
        .agg(
            Cities=("City", "count"),
            Median_Value=(reg_metric, "median"),
            Mean_Value=(reg_metric, "mean"),
            Min_Value=(reg_metric, "min"),
            Max_Value=(reg_metric, "max"),
        )
        .reset_index()
        .sort_values(by="Median_Value", ascending=False)
    )

    fig_reg_bar = px.bar(
        reg_summary,
        x="Median_Value",
        y="Region",
        orientation="h",
        color="Region",
        color_discrete_map=REGION_COLORS,
        text="Median_Value",
        labels={"Median_Value": f"Median {ANALYSIS_METRICS[reg_metric]}"},
        title=f"Continental Ranking: Median {ANALYSIS_METRICS[reg_metric]}",
    )
    fig_reg_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_reg_bar.update_layout(height=400, showlegend=False, margin=dict(l=70, r=40, t=50, b=50))
    st.plotly_chart(fig_reg_bar, use_container_width=True)

    st.markdown("#### Regional Aggregate Table")
    disp_summary = reg_summary.copy()
    disp_summary["Median_Value"] = disp_summary["Median_Value"].round(1)
    disp_summary["Mean_Value"] = disp_summary["Mean_Value"].round(1)
    disp_summary["Min_Value"] = disp_summary["Min_Value"].round(1)
    disp_summary["Max_Value"] = disp_summary["Max_Value"].round(1)
    st.dataframe(disp_summary, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION G — CUSTOM VISUALIZATION STUDIO
# ══════════════════════════════════════════════════════════════════════════════
with t_studio:
    section_header(
        "Custom Visualization Studio",
        "Design, customize, and export your own visualizations from the 238-city master intelligence database."
    )

    with st.expander("🛠️ Chart Builder Controls", expanded=True):
        st1, st2, st3, st4 = st.columns(4)
        with st1:
            cust_type = st.selectbox(
                "Chart Type",
                ["Scatter Plot", "Bar Chart", "Histogram", "Box Plot", "Violin Plot", "World Map"],
                key="cust_chart_type",
            )
        with st2:
            cust_x = st.selectbox(
                "X-Axis Indicator",
                list(ANALYSIS_METRICS.keys()),
                index=0,
                format_func=lambda k: ANALYSIS_METRICS[k],
                key="cust_x_var",
            )
        with st3:
            cust_y = st.selectbox(
                "Y-Axis Indicator (where applicable)",
                list(ANALYSIS_METRICS.keys()),
                index=1,
                format_func=lambda k: ANALYSIS_METRICS[k],
                key="cust_y_var",
            )
        with st4:
            cust_color = st.selectbox(
                "Color Dimension",
                ["Region", "Liveability_Zone", "None"],
                key="cust_color_var",
            )

        st5, st6, st7, st8 = st.columns(4)
        with st5:
            cust_reg_filter = st.selectbox("Region Filter", ["All"] + sorted(df["Region"].unique().tolist()), key="cust_reg_f")
        with st6:
            cust_top_n = st.slider("Top-N Slice", 10, len(df), len(df), key="cust_top_n_sl")
        with st7:
            cust_scale = st.radio("Axis Scale", ["Linear", "Logarithmic"], horizontal=True, key="cust_scale_rad")
        with st8:
            cust_title = st.text_input("Custom Chart Title", value="Custom Analysis Visual", key="cust_custom_title")

    # Filter studio dataset
    studio_df = df.copy()
    if cust_reg_filter != "All":
        studio_df = studio_df[studio_df["Region"] == cust_reg_filter]
    studio_df = studio_df.head(cust_top_n)

    # Render selected chart
    c_color_arg = None if cust_color == "None" else cust_color
    log_arg = cust_scale == "Logarithmic"

    if cust_type == "Scatter Plot":
        fig_cust = px.scatter(
            studio_df,
            x=cust_x,
            y=cust_y,
            color=c_color_arg,
            color_discrete_map=REGION_COLORS if cust_color == "Region" else None,
            size="Cost_of_Living_Index",
            size_max=18,
            log_x=log_arg,
            hover_name="City",
            hover_data={"Country": True, cust_x: ":.1f", cust_y: ":.1f"},
            title=cust_title,
            labels={cust_x: ANALYSIS_METRICS[cust_x], cust_y: ANALYSIS_METRICS[cust_y]},
        )
    elif cust_type == "Bar Chart":
        fig_cust = px.bar(
            studio_df.sort_values(by=cust_x, ascending=False).head(20),
            x="City",
            y=cust_x,
            color=c_color_arg,
            color_discrete_map=REGION_COLORS if cust_color == "Region" else None,
            title=f"Top Cities by {ANALYSIS_METRICS[cust_x]}",
            labels={cust_x: ANALYSIS_METRICS[cust_x]},
        )
    elif cust_type == "Histogram":
        fig_cust = px.histogram(
            studio_df,
            x=cust_x,
            color=c_color_arg,
            color_discrete_map=REGION_COLORS if cust_color == "Region" else None,
            title=cust_title,
            labels={cust_x: ANALYSIS_METRICS[cust_x]},
        )
    elif cust_type == "Box Plot":
        fig_cust = px.box(
            studio_df,
            x="Region",
            y=cust_x,
            color=c_color_arg,
            color_discrete_map=REGION_COLORS if cust_color == "Region" else None,
            points="all",
            hover_name="City",
            title=cust_title,
            labels={cust_x: ANALYSIS_METRICS[cust_x]},
        )
    elif cust_type == "Violin Plot":
        fig_cust = px.violin(
            studio_df,
            x="Region",
            y=cust_x,
            color=c_color_arg,
            color_discrete_map=REGION_COLORS if cust_color == "Region" else None,
            box=True,
            points="all",
            hover_name="City",
            title=cust_title,
            labels={cust_x: ANALYSIS_METRICS[cust_x]},
        )
    else:  # World Map
        fig_cust = px.scatter_geo(
            studio_df,
            lat="Latitude",
            lon="Longitude",
            color=cust_x,
            size="Cost_of_Living_Index",
            size_max=16,
            color_continuous_scale="Viridis",
            hover_name="City",
            hover_data={"Country": True, cust_x: ":.1f"},
            title=cust_title,
            projection="natural earth",
            labels={cust_x: ANALYSIS_METRICS[cust_x]},
        )
        fig_cust.update_geos(showland=True, landcolor=SURFACE, showocean=True, oceancolor=BG)

    fig_cust.update_layout(height=520, margin=dict(l=55, r=20, t=65, b=55))
    st.plotly_chart(fig_cust, use_container_width=True)

    # Export capabilities
    e_col1, e_col2, e_col3 = st.columns([1, 1, 2])
    with e_col1:
        csv_bytes = studio_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Data (CSV)",
            data=csv_bytes,
            file_name="custom_studio_data.csv",
            mime="text/csv",
            key="btn_studio_csv",
        )
    with e_col2:
        html_buffer = io.StringIO()
        fig_cust.write_html(html_buffer, include_plotlyjs="cdn")
        html_bytes = html_buffer.getvalue().encode("utf-8")
        st.download_button(
            label="⬇️ Export Chart (Interactive HTML)",
            data=html_bytes,
            file_name="custom_studio_chart.html",
            mime="text/html",
            key="btn_studio_html",
        )
