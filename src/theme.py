"""Design System: OBSIDIAN LUXE for URBAN INTELLIGENCE — The Global Liveability Observatory.

Contains:
- Exact color tokens (Main background, Sidebar, Surfaces, Borders, Accents)
- Typography & CSS injection (Inter, JetBrains Mono, restrained elegance)
- Reusable UI builders (Executive KPI cards, Discovery Feed cards, Section headers, Badges)
- Plotly dark template 'obsidian_luxe' with semantic colors:
  Emerald: favourable / clean
  Champagne gold: benchmarks / highlights
  Muted coral: adverse / high cost / pollution
  Silver: neutral structural context
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ── Obsidian Luxe Colour Tokens ───────────────────────────────────────────────
BG = "#0B0E12"
SIDEBAR = "#10151B"
SURFACE = "#141A21"
SURFACE_ELEVATED = "#1B232C"
BORDER = "#28323D"
TEXT_PRIMARY = "#F0F1ED"
TEXT_SECONDARY = "#929DA8"

# Semantic Accents
EMERALD = "#55B89A"       # Favourable environmental / clean / positive
CHAMPAGNE = "#C6A46A"     # Benchmarks / highlights / economic power
CORAL = "#D97870"         # Adverse conditions / pollution / extreme cost
SILVER = "#929DA8"        # Neutral information

# Regional Palette (Harmonized with Obsidian Luxe)
REGION_COLORS = {
    "Europe":        "#55B89A",  # Emerald
    "North America": "#C6A46A",  # Champagne
    "Asia":          "#68A4C4",  # Cool Blue
    "South Asia":    "#D97870",  # Coral
    "Middle East":   "#E5C158",  # Gold
    "South America": "#48BB78",  # Soft Green
    "Oceania":       "#81E6D9",  # Cyan Teal
    "Africa":        "#B794F4",  # Purple
}

# ── Plotly Shared Dark Template: obsidian_luxe ───────────────────────────────
OBSIDIAN_TEMPLATE = dict(
    layout=dict(
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12, color=TEXT_PRIMARY),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=[EMERALD, CHAMPAGNE, CORAL, "#68A4C4", "#B794F4", "#E5C158", "#81E6D9", SILVER],
        xaxis=dict(
            gridcolor=BORDER,
            gridwidth=0.5,
            zeroline=False,
            linecolor=BORDER,
            tickcolor=TEXT_SECONDARY,
            tickfont=dict(color=TEXT_SECONDARY, size=11),
            title=dict(font=dict(color=TEXT_PRIMARY, size=12)),
        ),
        yaxis=dict(
            gridcolor=BORDER,
            gridwidth=0.5,
            zeroline=False,
            linecolor=BORDER,
            tickcolor=TEXT_SECONDARY,
            tickfont=dict(color=TEXT_SECONDARY, size=11),
            title=dict(font=dict(color=TEXT_PRIMARY, size=12)),
        ),
        hoverlabel=dict(
            bgcolor=SURFACE_ELEVATED,
            font_size=12,
            font_color=TEXT_PRIMARY,
            bordercolor=CHAMPAGNE,
            font_family="Inter, sans-serif",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER,
            font=dict(color=TEXT_SECONDARY, size=11),
        ),
        margin=dict(l=50, r=25, t=65, b=55),
        autosize=True,
        title=dict(font=dict(size=14, color=TEXT_PRIMARY, family="Inter, sans-serif")),
    )
)
pio.templates["obsidian_luxe"] = go.layout.Template(**OBSIDIAN_TEMPLATE)
pio.templates.default = "obsidian_luxe"


def inject_obsidian_luxe_css() -> None:
    """Inject full-page refined Obsidian Luxe styling."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* Root background and typography */
        html, body, [data-testid="stApp"] {{
            background-color: {BG} !important;
            color: {TEXT_PRIMARY};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.01em;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR} !important;
            border-right: 1px solid {BORDER};
        }}
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {{
            color: {TEXT_SECONDARY} !important;
        }}
        [data-testid="stSidebarNavLink"] {{
            border-radius: 8px;
            font-weight: 500;
            color: {TEXT_SECONDARY} !important;
            padding: 8px 12px;
            margin: 2px 0;
            transition: all 0.15s ease;
        }}
        [data-testid="stSidebarNavLink"]:hover {{
            background: {SURFACE_ELEVATED} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"] {{
            background: linear-gradient(90deg, {EMERALD}20, transparent) !important;
            color: {EMERALD} !important;
            border-left: 3px solid {EMERALD};
            font-weight: 600;
        }}

        /* Content block container */
        .main .block-container {{
            padding: 2rem 2.5rem 3rem;
            max-width: 1440px;
        }}

        /* Headings */
        h1, h2, h3, h4 {{
            color: {TEXT_PRIMARY} !important;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        /* Tabs */
        [data-baseweb="tab-list"] {{
            background: {SURFACE} !important;
            border: 1px solid {BORDER};
            border-radius: 10px;
            gap: 4px;
            padding: 4px;
        }}
        [data-baseweb="tab"] {{
            border-radius: 8px !important;
            color: {TEXT_SECONDARY} !important;
            font-weight: 500;
            font-size: 0.88rem;
            padding: 6px 16px;
        }}
        [aria-selected="true"][data-baseweb="tab"] {{
            background: {SURFACE_ELEVATED} !important;
            color: {CHAMPAGNE} !important;
            border: 1px solid {BORDER} !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}

        /* Inputs & Selectboxes */
        [data-baseweb="select"] > div {{
            background: {SURFACE_ELEVATED} !important;
            border-color: {BORDER} !important;
            border-radius: 8px !important;
            color: {TEXT_PRIMARY} !important;
        }}
        input, textarea {{
            background: {SURFACE_ELEVATED} !important;
            color: {TEXT_PRIMARY} !important;
            border-color: {BORDER} !important;
            border-radius: 8px !important;
        }}

        /* Dataframes */
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 10px;
            background: {SURFACE};
        }}

        /* Buttons */
        [data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, {EMERALD}, #3E9A7E) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            color: #0B0E12 !important;
            box-shadow: 0 3px 12px {EMERALD}35;
        }}
        [data-testid="baseButton-secondary"] {{
            background: {SURFACE_ELEVATED} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
            color: {TEXT_PRIMARY} !important;
        }}

        /* Expanders */
        [data-testid="stExpander"] {{
            background: {SURFACE} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 10px !important;
        }}

        /* Dividers */
        hr {{
            border-color: {BORDER} !important;
            margin: 1.8rem 0;
        }}

        /* Monospace technical figures */
        .mono-num {{
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Mobile layout adjustments */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 1rem 1rem 2rem;
            }}
            [data-testid="stHorizontalBlock"] {{
                flex-wrap: wrap !important;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="column"],
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def executive_kpi_card(title: str, value: str, subtext: str = "", accent: str = CHAMPAGNE, icon: str = "") -> str:
    """Render a restrained, elegant executive KPI card."""
    return f"""
    <div style="
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-top: 3px solid {accent};
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:0.72rem; font-weight:700; color:{accent}; text-transform:uppercase; letter-spacing:0.1em;">
                {title}
            </span>
            <span style="font-size:1.2rem;">{icon}</span>
        </div>
        <div style="font-size:2.1rem; font-weight:800; color:{TEXT_PRIMARY}; font-family:'JetBrains Mono', monospace; line-height:1.1;">
            {value}
        </div>
        <div style="font-size:0.78rem; color:{TEXT_SECONDARY}; margin-top:6px;">
            {subtext}
        </div>
    </div>
    """


def discovery_card(title: str, metric_value: str, badge_label: str, explanation: str, sample_size: int, source: str) -> str:
    """Render an automated statistical discovery card for the Discovery Feed."""
    return f"""
    <div style="
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-left: 4px solid {CHAMPAGNE};
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.25);
    ">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
            <div>
                <span style="font-size:0.72rem; font-weight:700; color:{CHAMPAGNE}; text-transform:uppercase; letter-spacing:0.08em;">
                    DISCOVERY
                </span>
                <div style="font-size:1.15rem; font-weight:700; color:{TEXT_PRIMARY}; margin-top:2px;">
                    {title}
                </div>
            </div>
            <span style="background:{EMERALD}22; color:{EMERALD}; border:1px solid {EMERALD}44; border-radius:6px; padding:3px 10px; font-size:0.75rem; font-weight:600;">
                {badge_label}
            </span>
        </div>
        <div style="font-size:1.6rem; font-weight:800; color:{TEXT_PRIMARY}; font-family:'JetBrains Mono', monospace; margin:6px 0;">
            {metric_value}
        </div>
        <div style="font-size:0.86rem; color:{TEXT_SECONDARY}; line-height:1.5; margin-bottom:10px;">
            {explanation}
        </div>
        <div style="display:flex; gap:16px; font-size:0.75rem; color:{SILVER}; border-top:1px solid {BORDER}; padding-top:8px;">
            <span><strong>Sample:</strong> {sample_size} global cities</span>
            <span><strong>Period:</strong> 2024–2025</span>
            <span><strong>Source:</strong> {source}</span>
        </div>
    </div>
    """


def section_header(title: str, subtitle: str = "") -> None:
    """Render a clean, premium section header."""
    st.markdown(
        f"""
        <div style="margin-bottom: 1.4rem; padding-bottom: 0.6rem; border-bottom: 1px solid {BORDER};">
            <h2 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: {TEXT_PRIMARY};">{title}</h2>
            {"" if not subtitle else f'<p style="margin: 4px 0 0; font-size: 0.86rem; color: {TEXT_SECONDARY}; line-height:1.4;">{subtitle}</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


def semantic_badge(text: str, color: str = EMERALD) -> str:
    """Render an inline semantic badge."""
    return (
        f'<span style="background:{color}20; color:{color}; border:1px solid {color}40; '
        f'border-radius:6px; padding:2px 8px; font-size:0.75rem; font-weight:600; font-family:\'JetBrains Mono\', monospace;">{text}</span>'
    )
