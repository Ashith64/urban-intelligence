"""Page 10: Methodology, Mathematical Formulations, and Analytical Limitations."""
import streamlit as st

st.set_page_config(page_title="Methodology & Limits - BISL504", page_icon="📋", layout="wide")

st.title("📋 Methodology, Analytical Formulas & Data Limitations")
st.markdown(
    """
    Transparent documentation of data provenance, standardization algorithms, 
    derived index equations, and real-world analytical constraints governing this project.
    """
)

# 1. Provenance and Scope
st.subheader("1. Data Provenance & Harmonization")
st.markdown(
    r"""
    The platform integrates four distinct real-world data sources:
    - **Cities Reference (`cities_reference.csv`)**: 161 curated benchmark global cities with standardized names, ISO nations, continental regions, and coordinates.
    - **Numbeo Cost of Living (`numbeo_raw.csv`)**: 536 worldwide urban centers indexed against New York City ($= 100$).
    - **IQAir World Air Quality (`iqair_raw.csv`)**: 124 annual ground-level particulate matter measurements ($\mu\text{g/m}^3$).
    - **TomTom Traffic Index (`tomtom_raw.csv`)**: 22 metropolitan traffic congestion indices.

    **Harmonization Process**:
    1. **Normalization**: Unicode diacritics are stripped (e.g., *Chișinău* $\rightarrow$ *Chisinau*, *São Paulo* $\rightarrow$ *Sao Paulo*).
    2. **Alias Resolution**: City aliases (*Bengaluru* $\rightarrow$ *Bangalore*, *New Delhi* $\rightarrow$ *Delhi*, *Kiev* $\rightarrow$ *Kyiv*, *Dakha* $\rightarrow$ *Dhaka*) and country abbreviations (*USA/US* $\rightarrow$ *United States*, *UK* $\rightarrow$ *United Kingdom*) are mapped.
    3. **Scope Filtering**: Portland is constrained to Oregon (`State == 'OR'`). Inner join between Numbeo and IQAir on `(City, Country)` yields 72 valid cities, left joined with TomTom transport data.
    """
)

st.markdown("---")

# 2. Mathematical Formulations
st.subheader("2. Mathematical Index Formulations")

st.markdown(
    r"""
    #### A. Min-Max Normalization
    To compare metrics measured on different scales without distortion:
    $$x_{\text{norm}} = \frac{x - x_{\min}}{x_{\max} - x_{\min}} \in [0, 1]$$
    
    #### B. Relative Net Income Index
    Reflects effective purchasing power scaled by local living and rent expense:
    $$\text{Relative\_Net\_Income\_Index} = \frac{\text{Local\_Purchasing\_Power\_Index} \times \text{Cost\_of\_Living\_Plus\_Rent\_Index}}{100}$$
    
    #### C. WHO $\text{PM}_{2.5}$ Guideline Multiple & Bands
    $$\text{PM2\_5\_x\_WHO\_Guideline} = \frac{\text{PM2\_5\_2024\_ugm3}}{5.0}$$
    
    Categorized into World Health Organization (2021) annual thresholds:
    - **Meets guideline**: $\le 5.0\ \mu\text{g/m}^3$
    - **Interim target 4**: $(5.0, 10.0]\ \mu\text{g/m}^3$
    - **Interim target 3**: $(10.0, 15.0]\ \mu\text{g/m}^3$
    - **Interim target 2**: $(15.0, 25.0]\ \mu\text{g/m}^3$
    - **Interim target 1**: $(25.0, 35.0]\ \mu\text{g/m}^3$
    - **Above interim targets**: $> 35.0\ \mu\text{g/m}^3$
    
    #### D. Affordability-Air Composite Score ($0 - 100$)
    $$\text{Score} = 100 \times \left[ w_1 \times \text{norm}(\text{LPP}) + w_2 \times (1 - \text{norm}(\text{PM}_{2.5})) \right]$$
    where default weights are $w_1 = 0.60$ and $w_2 = 0.40$ (auto-normalized such that $\sum w_i = 1$).
    """
)

st.markdown("---")

# 3. Limitations
st.subheader("3. Explicit Data & Analytical Limitations")

st.markdown(
    """
    1. **Cross-Sectional Snapshot (No Time Series)**:
       The datasets represent single real snapshots (Numbeo ~2025, IQAir 2024, TomTom 2025). 
       No historical time-series data exists; consequently, time sliders, date filters, and 
       multi-year trend lines are intentionally excluded to prevent misleading extrapolation.
    
    2. **Capital City Bias in Air Quality Data**:
       IQAir raw observations focus predominantly on national capitals (121 capitals + 3 US metropolises). 
       As a result, secondary industrial cities or regional centers within large nations are underrepresented in the merged scope.
    
    3. **Sparse Traffic Index Coverage**:
       Only 10 cities within the 72-city final merged dataset have published TomTom congestion statistics. 
       In strict accordance with engineering rules, missing traffic values are **never filled with zero** or imputed, 
       as doing so would falsely imply zero traffic congestion.
    
    4. **Crowdsourced Cost of Living Indices**:
       Numbeo data reflects crowd-sourced contributor pricing, which may introduce sampling bias toward expat, 
       digital nomad, or urban middle-class consumption baskets compared to official national statistical offices.
    
    5. **Outlier Treatment Protocol**:
       Tukey's 1.5×IQR fences flag 19 cities in Numbeo and 9 cities in IQAir as statistical outliers. 
       These observations reflect real economic and environmental extremes (e.g. Zurich's high purchasing power, 
       Delhi's particulate levels) and are retained in the analysis without alteration.
    """
)
