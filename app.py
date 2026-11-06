"""Main Entry Point for the BISL504 Urban Affordability & Liveability Platform."""
import streamlit as st

# Configure multi-page navigation
home_page = st.Page("pages/1_Home.py", title="Executive Overview", icon="🏠", default=True)
profiling_page = st.Page("pages/2_Data_Profiling.py", title="Data Profiling", icon="📊")
explore_page = st.Page("pages/3_Explore.py", title="Explore Cities", icon="🔍")
map_page = st.Page("pages/4_Map.py", title="Global Map", icon="🗺️")
compare_page = st.Page("pages/5_Compare_Cities.py", title="Compare Cities", icon="⚖️")
rankings_page = st.Page("pages/6_Rankings.py", title="Dynamic Rankings", icon="🏆")
correlation_page = st.Page("pages/7_Correlation_and_Distribution.py", title="Correlation & Distribution", icon="📈")
explorer_page = st.Page("pages/8_Data_Explorer.py", title="Data Explorer", icon="📁")
insights_page = st.Page("pages/9_Insights.py", title="Automated Insights", icon="💡")
methodology_page = st.Page("pages/10_Methodology_and_Limits.py", title="Methodology & Limits", icon="📋")

nav = st.navigation(
    {
        "Overview": [home_page, profiling_page],
        "City Analytics": [explore_page, map_page, compare_page, rankings_page],
        "Statistical Intelligence": [correlation_page, explorer_page, insights_page, methodology_page],
    }
)

nav.run()
