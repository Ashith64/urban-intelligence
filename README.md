# Urban Affordability & Liveability Intelligence Platform (BISL504)

An interactive, production-ready analytics platform exploring the intersection between financial purchasing power, cost of living, fine particulate matter ($\text{PM}_{2.5}$) air quality, and urban traffic congestion across 72 benchmark global cities.

Built with **Python**, **Streamlit**, **Plotly**, **Pandas**, **NumPy**, **Matplotlib**, **Seaborn**, and **Pytest**.

---

## 🎯 Project Overview & Core Question
> *"Which world cities are both affordable and breathable, and how do cost, purchasing power, air quality, and traffic relate?"*

This intelligence platform synthesizes four real-world datasets into an interactive multi-page dashboard. All calculations, rankings, correlations, and insights are computed dynamically from real snapshot data—no synthetic or fabricated values are ever used.

---

## 🧭 Dashboard Architecture (10 Pages)

1. **🏠 Executive Overview (`1_Home.py`)**: High-level KPI summary cards, validated data source badges, and user navigation guide.
2. **📊 Dataset Profiling (`2_Data_Profiling.py`)**: Data schema inspection, missingness analysis, Tukey's 1.5×IQR outlier detection audit, and label parsing verification.
3. **🔍 City Exploration (`3_Explore.py`)**: Multi-filter scatter plot (Purchasing Power vs. $\text{PM}_{2.5}$ log scale) with WHO annual guideline threshold and an interactive linked city detail drill-down panel.
4. **🗺️ Global Map (`4_Map.py`)**: Interactive Plotly `scatter_geo` projection with dynamic metric color encoding and Cost of Living bubble dimensioning (no external API keys required).
5. **⚖️ City Comparison (`5_Compare_Cities.py`)**: Multi-city selector (2–5 cities), radar chart of normalized dimensions, grouped bar charts, and a side-by-side indicator matrix.
6. **🏆 Dynamic Rankings (`6_Rankings.py`)**: What-if simulation sliders for economic purchasing power ($w_1$) vs. clean air ($w_2$) with auto-normalization, live Top-N bar charts, and CSV data export.
7. **📈 Correlation & Distribution (`7_Correlation_and_Distribution.py`)**: Parametric Pearson and non-parametric Spearman correlation heatmaps, regional box plots, frequency histograms, and a static dual-panel Seaborn density plot.
8. **📁 Data Explorer (`8_Data_Explorer.py`)**: Interactive searchable tabular data viewer for raw and processed datasets, dynamic column picker, and CSV downloads.
9. **💡 Automated Insights (`9_Insights.py`)**: Dynamically generated analytical takeaways, including top balanced performers, extreme cities, regional medians, and WHO air quality guideline compliance.
10. **📋 Methodology & Limits (`10_Methodology_and_Limits.py`)**: Transparent documentation of data provenance, normalization equations, composite score formulation, and explicit analytical limitations (cross-sectional snapshot, capital bias, and sparse traffic coverage).

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12 and Python 3.14)
- Git

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone <repo-url>
cd bisl504-dashboard

# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Run Preprocessing Pipeline
```bash
python -m src.pipeline
```
This processes `data/raw/` into `data/processed/{cost_of_living,air_quality,traffic}_processed.csv` and generates the harmonized `data/processed/final_merged.csv`.

### 4. Launch Streamlit Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Automated Testing

Execute the test suite verifying data validation counts, derived index equations, and full page rendering:

```bash
pytest tests/ -v
```

The test suite covers:
- **`tests/test_pipeline.py`**: Asserts exact raw-to-scope counts (Numbeo 536 $\rightarrow$ 161, IQAir 124 $\rightarrow$ 72, TomTom 22 $\rightarrow$ 22, Final = 72 cities, 10 traffic rows), IQR outlier flags (19/9/0), normalization bounds $[0, 1]$, and zero nulls.
- **`tests/test_analysis.py`**: Validates dynamic what-if scoring, Pearson/Spearman correlation matrices, filtering logic, and Seaborn static rendering.
- **`tests/test_app.py`**: Uses `streamlit.testing.v1.AppTest` to verify that `app.py` and all 10 pages render without exceptions.

---

## 📁 Repository Structure

```
bisl504-dashboard/
├── .streamlit/
│   └── config.toml                  # Streamlit visual theme (Okabe-Ito friendly, dark/light safe)
├── data/
│   ├── raw/                         # 4 immutable raw datasets
│   │   ├── cities_reference.csv     # 161 benchmark global cities scope
│   │   ├── iqair_raw.csv            # 124 air quality observations
│   │   ├── numbeo_raw.csv           # 536 cost of living records
│   │   └── tomtom_raw.csv           # 22 traffic congestion records
│   └── processed/                   # Harmonized and normalized datasets
│       ├── cost_of_living_processed.csv
│       ├── air_quality_processed.csv
│       ├── traffic_processed.csv
│       └── final_merged.csv         # 72 cities unified dataset
├── docs/
│   └── SPEC.md                      # Technical specifications & validation benchmarks
├── pages/
│   ├── 1_Home.py                    # Page 1: Executive Overview
│   ├── 2_Data_Profiling.py          # Page 2: Profiling, Missingness & Outliers
│   ├── 3_Explore.py                 # Page 3: Interactive City Exploration
│   ├── 4_Map.py                     # Page 4: Global Geospatial Map
│   ├── 5_Compare_Cities.py          # Page 5: Multi-City Radar & Bar Comparisons
│   ├── 6_Rankings.py                # Page 6: Dynamic What-If Rankings
│   ├── 7_Correlation_and_Distribution.py # Page 7: Heatmaps, Distributions & Static KDE
│   ├── 8_Data_Explorer.py           # Page 8: Tabular Explorer & CSV Downloads
│   ├── 9_Insights.py                # Page 9: Automated Statistical Insights
│   └── 10_Methodology_and_Limits.py # Page 10: Methodology & Documented Limits
├── src/
│   ├── __init__.py
│   ├── config.py                    # Paths, aliases, color palettes, constants
│   ├── pipeline.py                  # Cleaning, outlier flagging, normalization, merge
│   ├── data_loader.py               # Cached data loading (@st.cache_data)
│   ├── analysis.py                  # Metrics calculation, correlation, filtering
│   ├── charts.py                    # Reusable Plotly & Matplotlib/Seaborn charting
│   └── insights.py                  # Dynamic insight computations
├── tests/
│   ├── test_pipeline.py             # SPEC Section 4 validation test suite
│   ├── test_analysis.py             # Analytical computation tests
│   └── test_app.py                  # AppTest smoke tests across all 10 pages
├── app.py                           # App entry point with st.navigation
├── requirements.txt                 # Runtime dependencies
├── requirements-dev.txt             # Development & test dependencies
├── PROGRESS.md                      # Milestone tracking log
└── README.md                        # Documentation & setup guide
```

---

## ☁️ Streamlit Community Cloud Deployment

1. Fork or push this repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app**, select the repository and branch (`master` or `main`).
4. Set **Main file path** to `app.py`.
5. Deploy. Streamlit automatically installs from `requirements.txt` and starts the application.
