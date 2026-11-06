# BISL504 - Project Progress

Status: COMPLETED & VERIFIED

## Completed Milestones
- [x] **M0: Repository & Environment Setup**
  - Inspected approved raw datasets, established baseline git repo.
  - Configured `requirements.txt`, `requirements-dev.txt`, and `.streamlit/config.toml`.
  - Configured Python 3.14 / virtual environment `.venv`.
- [x] **M1: Preprocessing Pipeline & Data Harmonization**
  - Built `src/config.py` and `src/pipeline.py` implementing unicode normalization, label parsing, alias mapping, 1.5×IQR outlier detection, Min-Max normalization, and joins.
  - Generated all processed CSV files in `data/processed/`.
  - Asserted all Section 4 validation figures (Numbeo: 536 $\rightarrow$ 161; IQAir: 124 $\rightarrow$ 72; TomTom: 22 $\rightarrow$ 22; Final: 72 cities, 10 traffic rows, 0 nulls, 19/9/0 outliers).
- [x] **M2: Analytical Modules & Visualization Helpers**
  - Implemented `src/data_loader.py` with `@st.cache_data`.
  - Implemented `src/analysis.py` with dynamic what-if scoring, Pearson/Spearman correlation matrices, and filtering.
  - Implemented `src/charts.py` with Okabe-Ito accessible color palettes, Plotly geo scatter map, radar comparisons, grouped bars, heatmaps, box plots, histograms, and static Seaborn/Matplotlib bivariate KDE plots.
  - Implemented `src/insights.py` computing all empirical insights dynamically from real data.
- [x] **M3: Full Multi-Page Streamlit Dashboard**
  - Implemented `app.py` with `st.navigation`.
  - Built all 10 pages in `pages/`:
    1. `1_Home.py`: Executive Overview & 5 KPI cards.
    2. `2_Data_Profiling.py`: Profiling, Missingness, Outliers & Validation Audit.
    3. `3_Explore.py`: Dynamic Exploration Scatter with Linked City Drill-Down.
    4. `4_Map.py`: Global Geospatial Intelligence Map.
    5. `5_Compare_Cities.py`: Head-to-Head Radar & Grouped Bar Comparison.
    6. `6_Rankings.py`: Dynamic What-If Simulation & CSV Export.
    7. `7_Correlation_and_Distribution.py`: Heatmaps, Boxplots & Static Seaborn KDE.
    8. `8_Data_Explorer.py`: Interactive Tabular Explorer & Multi-Dataset Exports.
    9. `9_Insights.py`: Dynamic Automated Findings & Disparities.
    10. `10_Methodology_and_Limits.py`: Transparent Methodology, Formulas & Documented Limits.
- [x] **M4: Automated Testing & Headless Verification**
  - Built and verified test suite: 22/22 tests passing across `test_pipeline.py`, `test_analysis.py`, and `test_app.py`.
  - Validated all 11 Streamlit entrypoints with `streamlit.testing.v1.AppTest`.
  - Executed live headless verification (`streamlit run app.py --server.headless true`), confirming HTTP 200 OK.
- [x] **M5: Documentation & Project Completion**
  - Generated comprehensive `README.md` with installation, execution, testing, and deployment instructions.
  - Finalized `PROGRESS.md`.

## Quality Gates Status
- Pytest Suite: 22 passed, 0 failed.
- AppTest Page Rendering: 11 passed (app.py + 10 pages), 0 exceptions.
- Live HTTP Service: HTTP 200 OK on `http://localhost:8501`.
- Data Provenance: 100% verified real data, 0 synthetic observations.

## Launch Command
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
