"""Reusable charting and visualization components using Plotly and Matplotlib/Seaborn.

All charts incorporate Okabe-Ito accessible colors, clear labels with units,
informative hover tooltips, and explanatory captions.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

from src.config import (
    OKABE_ITO_PALETTE,
    REGION_COLORS,
    PM25_BAND_COLORS,
    WHO_ANNUAL_GUIDELINE,
)

# Shared Plotly template styling
PLOTLY_LAYOUT_DEFAULTS = dict(
    font=dict(family="sans-serif", size=13, color="#1E293B"),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="#1E293B", font_size=12, font_color="#FFFFFF"),
)


def render_kpi_card(title: str, value: str | int | float, subtext: str = "", help_text: str | None = None):
    """Render a clean, high-contrast KPI metric card."""
    with st.container():
        st.markdown(
            f"""
            <div style="
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 16px 20px;
                margin-bottom: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            ">
                <div style="font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">
                    {title}
                </div>
                <div style="font-size: 1.85rem; font-weight: 700; color: #0072B2; margin: 4px 0;">
                    {value}
                </div>
                <div style="font-size: 0.8rem; color: #475569;">
                    {subtext}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def plot_global_map(
    df: pd.DataFrame,
    color_metric: str = "Affordability_Air_Score_0_100",
    color_label: str = "Affordability-Air Score (0-100)",
) -> go.Figure:
    """Render an interactive scatter_geo world map without external API tokens."""
    hover_template = (
        "<b>%{customdata[0]}, %{customdata[1]}</b><br>"
        "Region: %{customdata[2]}<br>"
        "Score: %{customdata[3]:.1f}<br>"
        "Local Purchasing Power: %{customdata[4]:.1f}<br>"
        "Cost of Living Index: %{customdata[5]:.1f}<br>"
        "PM2.5 (2024): %{customdata[6]:.1f} µg/m³<br>"
        "WHO Band: %{customdata[7]}<extra></extra>"
    )

    customdata = df[
        [
            "City",
            "Country",
            "Region",
            "Affordability_Air_Score_0_100",
            "Local_Purchasing_Power_Index",
            "Cost_of_Living_Index",
            "PM2_5_2024_ugm3",
            "PM2_5_WHO_Band",
        ]
    ].values

    # Determine colorscale: reverse if higher is worse (like PM2.5)
    reverse_color = "PM2_5" in color_metric or "Cost" in color_metric
    colorscale = "Viridis_r" if reverse_color else "Viridis"

    fig = px.scatter_geo(
        df,
        lat="Latitude",
        lon="Longitude",
        color=color_metric,
        size="Cost_of_Living_Index",
        size_max=16,
        color_continuous_scale=colorscale,
        labels={color_metric: color_label, "Cost_of_Living_Index": "Cost of Living"},
        projection="natural earth",
        title=f"Global City Distribution: {color_label} (Bubble Size = Cost of Living)",
    )

    fig.update_traces(
        customdata=customdata,
        hovertemplate=hover_template,
        marker=dict(line=dict(width=1, color="#1E293B"), opacity=0.85),
    )

    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="#CBD5E1",
        showland=True,
        landcolor="#F1F5F9",
        showocean=True,
        oceancolor="#E0F2FE",
        showlakes=True,
        lakecolor="#E0F2FE",
        showcountries=True,
        countrycolor="#CBD5E1",
    )

    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    return fig


def plot_explore_scatter(
    df: pd.DataFrame,
    log_y: bool = True,
    color_by: str = "Region",
) -> go.Figure:
    """Render scatter plot of Purchasing Power vs PM2.5 with WHO reference line."""
    color_discrete_map = REGION_COLORS if color_by == "Region" else PM25_BAND_COLORS

    fig = px.scatter(
        df,
        x="Local_Purchasing_Power_Index",
        y="PM2_5_2024_ugm3",
        color=color_by,
        color_discrete_map=color_discrete_map,
        log_y=log_y,
        size="Cost_of_Living_Index",
        size_max=14,
        hover_name="City",
        hover_data={
            "Country": True,
            "Region": True,
            "Local_Purchasing_Power_Index": ":.1f",
            "PM2_5_2024_ugm3": ":.1f",
            "Cost_of_Living_Index": ":.1f",
            "Affordability_Air_Score_0_100": ":.1f",
        },
        labels={
            "Local_Purchasing_Power_Index": "Local Purchasing Power Index (New York = 100)",
            "PM2_5_2024_ugm3": "PM2.5 Concentration (µg/m³)" + (" [Log Scale]" if log_y else ""),
            "Cost_of_Living_Index": "Cost of Living",
        },
        title="Purchasing Power vs PM2.5 Air Pollution (Bubble Size = Cost of Living)",
    )

    # Add WHO Annual Air Quality Guideline reference line (5 µg/m³)
    fig.add_hline(
        y=WHO_ANNUAL_GUIDELINE,
        line_dash="dash",
        line_color="#D55E00",
        line_width=2,
        annotation_text="WHO Annual Guideline (5.0 µg/m³)",
        annotation_position="bottom right",
    )

    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    return fig


def plot_radar_comparison(df: pd.DataFrame, cities: list[str]) -> go.Figure:
    """Render a multi-city radar chart of normalized attributes."""
    metrics = [
        ("Local_Purchasing_Power_Index_norm", "Purchasing Power"),
        ("Cost_of_Living_Index_norm", "Cost of Living"),
        ("Rent_Index_norm", "Rent Index"),
        ("Groceries_Index_norm", "Groceries"),
        ("Restaurant_Price_Index_norm", "Restaurant Price"),
    ]

    metric_cols = [m[0] for m in metrics]
    categories = [m[1] for m in metrics]
    # Add Clean Air dimension: 1 - norm(PM2.5)
    categories.append("Clean Air (1 - PM2.5)")

    fig = go.Figure()

    palette = list(OKABE_ITO_PALETTE.values())

    for idx, city in enumerate(cities):
        city_row = df[df["City"] == city]
        if city_row.empty:
            continue
        vals = [city_row[col].values[0] for col in metric_cols]
        # Clean air dimension
        clean_air = 1.0 - city_row["PM2_5_2024_ugm3_norm"].values[0]
        vals.append(clean_air)
        # Close radar loop
        vals_loop = vals + [vals[0]]
        cats_loop = categories + [categories[0]]

        color = palette[idx % len(palette)]
        fig.add_trace(
            go.Scatterpolar(
                r=vals_loop,
                theta=cats_loop,
                fill="toself",
                fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)",
                line=dict(color=color, width=2),
                name=city,
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=10)),
        ),
        title="Multidimensional City Comparison (Normalized 0 - 1)",
        **PLOTLY_LAYOUT_DEFAULTS,
    )
    return fig


def plot_grouped_bar_comparison(df: pd.DataFrame, cities: list[str]) -> go.Figure:
    """Render grouped bar chart comparing raw key indicators for selected cities."""
    subset = df[df["City"].isin(cities)]
    metrics = [
        ("Local_Purchasing_Power_Index", "Purchasing Power (NY=100)"),
        ("Cost_of_Living_Index", "Cost of Living (NY=100)"),
        ("Rent_Index", "Rent Index (NY=100)"),
        ("PM2_5_2024_ugm3", "PM2.5 (µg/m³)"),
    ]

    plot_data = []
    for _, row in subset.iterrows():
        for col, label in metrics:
            plot_data.append({"City": row["City"], "Indicator": label, "Value": row[col]})

    plot_df = pd.DataFrame(plot_data)

    fig = px.bar(
        plot_df,
        x="Indicator",
        y="Value",
        color="City",
        barmode="group",
        color_discrete_sequence=list(OKABE_ITO_PALETTE.values()),
        title="Direct Indicator Comparison by City",
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis_title="Key Indicator",
        yaxis_title="Indicator Value",
    )
    return fig


def plot_rankings_bar(df: pd.DataFrame, score_col: str = "Affordability_Air_Score_0_100", top_n: int = 15) -> go.Figure:
    """Render horizontal bar chart for Top-N ranked cities."""
    top_df = df.head(top_n).sort_values(by=score_col, ascending=True)

    fig = px.bar(
        top_df,
        x=score_col,
        y="City",
        orientation="h",
        color="Region",
        color_discrete_map=REGION_COLORS,
        hover_data={"Country": True, score_col: ":.2f", "PM2_5_2024_ugm3": ":.1f"},
        labels={score_col: "Score (0-100)", "City": "City"},
        title=f"Top {top_n} Cities: Live Dynamic Ranking",
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis_title="Affordability-Air Score (0-100)",
        yaxis_title="City",
    )
    return fig


def plot_correlation_heatmap(corr_df: pd.DataFrame, title: str = "Correlation Heatmap") -> go.Figure:
    """Render interactive correlation matrix heatmap."""
    labels = [c.replace("_", " ") for c in corr_df.columns]

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_df.values,
            x=labels,
            y=labels,
            colorscale="RdBu_r",
            zmin=-1.0,
            zmax=1.0,
            text=np.round(corr_df.values, 2),
            texttemplate="%{text}",
            textfont={"size": 11},
            hoverongaps=False,
        )
    )
    fig.update_layout(
        title=title,
        **PLOTLY_LAYOUT_DEFAULTS,
    )
    return fig


def plot_regional_boxplots(df: pd.DataFrame, metric: str, metric_label: str) -> go.Figure:
    """Render regional box plots showing distributions."""
    fig = px.box(
        df,
        x="Region",
        y=metric,
        color="Region",
        color_discrete_map=REGION_COLORS,
        points="all",
        hover_name="City",
        labels={metric: metric_label, "Region": "Region"},
        title=f"Regional Distribution: {metric_label}",
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        showlegend=False,
    )
    return fig


def plot_metric_histogram(df: pd.DataFrame, metric: str, metric_label: str, nbins: int = 20) -> go.Figure:
    """Render interactive distribution histogram with mean line."""
    fig = px.histogram(
        df,
        x=metric,
        nbins=nbins,
        color_discrete_sequence=["#0072B2"],
        labels={metric: metric_label},
        title=f"Distribution of {metric_label}",
    )
    mean_val = df[metric].mean()
    median_val = df[metric].median()

    fig.add_vline(x=mean_val, line_dash="dash", line_color="#D55E00", annotation_text=f"Mean: {mean_val:.1f}")
    fig.add_vline(x=median_val, line_dash="dot", line_color="#009E73", annotation_text=f"Median: {median_val:.1f}")

    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        yaxis_title="City Count",
    )
    return fig


def render_static_seaborn_pairplot(df: pd.DataFrame) -> plt.Figure:
    """Create a static Seaborn / Matplotlib figure for st.pyplot (SPEC requirement)."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=100)

    # Subplot 1: KDE Distribution of LPP vs PM2.5
    sns.kdeplot(
        data=df,
        x="Local_Purchasing_Power_Index",
        y="PM2_5_2024_ugm3",
        hue="Region",
        palette=REGION_COLORS,
        fill=True,
        alpha=0.3,
        ax=axes[0],
        legend=False,
        warn_singular=False,
    )
    axes[0].set_title("Density: Purchasing Power vs PM2.5", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Local Purchasing Power Index", fontsize=10)
    axes[0].set_ylabel("PM2.5 (µg/m³)", fontsize=10)
    axes[0].axhline(WHO_ANNUAL_GUIDELINE, color="#D55E00", linestyle="--", linewidth=1.2, label="WHO Guideline")
    axes[0].grid(True, linestyle=":", alpha=0.5)

    # Subplot 2: Regression scatter plot
    sns.regplot(
        data=df,
        x="Cost_of_Living_Index",
        y="Local_Purchasing_Power_Index",
        scatter_kws={"alpha": 0.6, "color": "#0072B2"},
        line_kws={"color": "#D55E00", "linewidth": 1.5},
        ax=axes[1],
    )
    axes[1].set_title("Linear Fit: Cost vs Purchasing Power", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Cost of Living Index", fontsize=10)
    axes[1].set_ylabel("Local Purchasing Power Index", fontsize=10)
    axes[1].grid(True, linestyle=":", alpha=0.5)

    fig.tight_layout()
    return fig
