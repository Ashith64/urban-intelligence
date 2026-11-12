"""URBAN INTELLIGENCE — THE GLOBAL LIVEABILITY OBSERVATORY.

Main Application Shell, Navigation Router, and Global Branding.
"""
import streamlit as st
from src.theme import inject_obsidian_luxe_css, BORDER, CHAMPAGNE, EMERALD, TEXT_SECONDARY, TEXT_PRIMARY

st.set_page_config(
    page_title="Urban Intelligence — The Global Liveability Observatory",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_obsidian_luxe_css()

# ── Persistent Sidebar Branding & Data Snapshot ───────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding: 0.8rem 0 1.2rem;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.6rem;">🏛️</span>
                <span style="font-size:1.25rem; font-weight:800; color:{TEXT_PRIMARY}; letter-spacing:0.04em;">
                    URBAN INTELLIGENCE
                </span>
            </div>
            <div style="font-size:0.7rem; font-weight:700; color:{CHAMPAGNE}; letter-spacing:0.12em; text-transform:uppercase; margin-top:2px;">
                THE GLOBAL LIVEABILITY OBSERVATORY
            </div>
            <p style="font-size:0.78rem; color:{TEXT_SECONDARY}; margin:8px 0 0; line-height:1.4;">
                Where can people enjoy a better balance of affordability, purchasing power, quality of life and environmental conditions?
            </p>
        </div>
        <div style="background:#141A21; border:1px solid {BORDER}; border-radius:10px; padding:12px; margin-bottom:1.2rem;">
            <div style="font-size:0.68rem; font-weight:700; color:{EMERALD}; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">
                DATASET SNAPSHOT
            </div>
            <div style="font-size:0.78rem; color:{TEXT_PRIMARY}; font-weight:600;">
                238 Cities · 82 Countries & Areas
            </div>
            <div style="font-size:0.72rem; color:{TEXT_SECONDARY}; margin-top:2px;">
                Observation: 2024–2025 Benchmark
            </div>
            <div style="font-size:0.72rem; color:{TEXT_SECONDARY};">
                Sources: Numbeo · GeoNames · World Bank
            </div>
        </div>
        <hr style="border-color:{BORDER}; margin:0 0 1rem;">
        """,
        unsafe_allow_html=True,
    )

# ── Five Clear Navigation Destinations ────────────────────────────────────────
exec_page     = st.Page("pages/1_Executive_Dashboard.py", title="Executive Dashboard", icon="🏛️", default=True)
explorer_page = st.Page("pages/2_City_Explorer.py",       title="City Explorer",       icon="🔍")
h2h_page      = st.Page("pages/3_Head_to_Head.py",        title="Head-to-Head",        icon="⚔️")
analysis_page = st.Page("pages/4_Analysis_Findings.py",    title="Analysis & Findings", icon="🔬")
dataroom_page = st.Page("pages/5_Data_Room.py",           title="Data Room",           icon="🗄️")

nav = st.navigation([exec_page, explorer_page, h2h_page, analysis_page, dataroom_page])
nav.run()
