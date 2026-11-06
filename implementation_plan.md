# BISL504 - Implementation Plan

## Objective
Build the complete, interactive Urban Affordability & Liveability Intelligence Platform using Streamlit, Plotly, Pandas, and Python.

## Scope & Constraints
- Only build the functional data visualization dashboard application and automated tests.
- Strictly adhere to approved raw datasets in `data/raw/` (`numbeo_raw.csv`, `iqair_raw.csv`, `tomtom_raw.csv`, `cities_reference.csv`).
- No synthetic datasets, fabricated observations, or imputation of missing traffic values.
- No PPT presentations, viva documents, or academic reports.

---

## Baseline Inspection Findings (M0)
1. **Existing Assets**:
   - Specifications: `AGENTS.md`, `docs/SPEC.md`, `PROGRESS.md`, `PROMPT.md`, `PROMPT_RESUME.md`.
   - Raw data files verified in `data/raw/`:
     - `numbeo_raw.csv`: 536 rows, 8 columns
     - `iqair_raw.csv`: 124 rows, 4 columns
     - `tomtom_raw.csv`: 22 rows, 6 columns
     - `cities_reference.csv`: 161 rows, 5 columns
   - Git repository initialized.
2. **Current State & Gaps**:
   - Zero Python source files exist (no `src/`, `app.py`, `pages/`, or `tests/`).
   - `data/processed/` directory and processed data do not yet exist.
   - Streamlit configuration (`.streamlit/config.toml`) not yet created.
   - Git repository has no commits yet.
3. **Dataset Verification**:
   - All 4 raw datasets are accessible, undamaged, and valid.
   - Data cleaning and normalization rules verified:
     - Numbeo: 536 raw -> 161 in scope; 19 IQR outliers.
     - IQAir: 124 raw -> 72 in scope; 9 IQR outliers.
     - TomTom: 22 raw -> 22 in scope; 0 congestion IQR outliers.
     - Final merged dataset: 72 cities, 0 duplicates, 10 cities with real congestion, 0 nulls in cost/PM2.5.
4. **Environment & Dependencies**:
   - Python 3.14.2 verified.
   - All required libraries are installed: `streamlit` (1.64.0), `plotly` (6.8.0), `pandas` (3.0.3), `numpy` (2.5.0), `matplotlib` (3.11.0), `seaborn` (0.13.2), `pytest` (9.1.1), `scipy` (1.18.1).
   - `requirements.txt` and `requirements-dev.txt` will be written for reproducible deployment.

---

## Shortest Implementation Sequence

### Phase 1: Environment & Repository Baseline (M0)
- Create `requirements.txt` and `requirements-dev.txt`.
- Create `.streamlit/config.toml` with professional, high-contrast, theme-aware styling.
- Create initial commit.

### Phase 2: Data Preprocessing Pipeline & Validation (M1)
- Create `src/config.py` with column definitions, aliases, palettes, and default constants.
- Create `src/pipeline.py` to:
  - Parse, strip accents, and apply aliases.
  - Compute 1.5x IQR outlier flags for raw tables.
  - Filter to project scope using `cities_reference.csv`.
  - Calculate Min-Max normalized metrics.
  - Inner join Numbeo & IQAir; Left join TomTom; Join Region/Lat/Long from `cities_reference.csv`.
  - Calculate derived metrics:
    - `Relative_Net_Income_Index = LPP * Cost_of_Living_Plus_Rent / 100`
    - `PM2_5_x_WHO_Guideline = PM2.5 / 5`
    - `PM2_5_WHO_Band` (<=5 Meets guideline, 5-10 Interim 4, 10-15 Interim 3, 15-25 Interim 2, 25-35 Interim 1, >35 Above interim targets)
    - `Affordability_Air_Score_0_100 = 100 * (0.6 * norm(LPP) + 0.4 * (1 - norm(PM2.5)))`
  - Export processed files to `data/processed/`.
- Create `tests/test_pipeline.py` asserting exact validation targets from SPEC Section 4.
- Run `pytest` and commit.

### Phase 3: Analytical Engine, Loader & Chart Components (M2)
- Create `src/data_loader.py` with `@st.cache_data` for fast loading of raw and processed datasets.
- Create `src/analysis.py` for correlation (Pearson, Spearman), distribution stats, dynamic ranking calculations.
- Create `src/insights.py` to dynamically generate headline findings directly from data (no hardcoding).
- Create `src/charts.py` for reusable Plotly & Matplotlib/Seaborn charts with Okabe-Ito colorblind-friendly palettes, tooltips, consistent titles and captions.
- Run unit tests and commit.

### Phase 4: Complete Dashboard Implementation (M3)
- Create `app.py`:
  - Home / Executive Overview with 5 KPI cards, project summary, data source badges, quick start guide.
- Create 9 multipage components in `pages/`:
  - `pages/01_Dataset_Profiling.py`: Source shapes, missing value matrices, IQR outlier tables, raw vs standardized labels.
  - `pages/02_City_Exploration.py`: Filterable scatter (LPP vs PM2.5, log scale, WHO guideline), interactive selection linked to KPI detail cards.
  - `pages/03_Global_Map.py`: Plotly `scatter_geo` colored by selected metric, sized by Cost of Living, hover inspection.
  - `pages/04_City_Comparison.py`: Multi-city selector (2-5 cities), normalized grouped bar chart, radar chart, side-by-side metric table.
  - `pages/05_Dynamic_Rankings.py`: Interactive weight sliders for what-if composite scoring, live Top-N bar chart, ranking table, CSV download.
  - `pages/06_Correlation_and_Distribution.py`: Pearson/Spearman heatmap, regional box plots, static Seaborn/Matplotlib distribution chart via `st.pyplot`.
  - `pages/07_Data_Explorer.py`: Interactive `st.dataframe`, column filters, raw/processed/final CSV downloads.
  - `pages/08_Automated_Insights.py`: Dynamic data-driven findings (cleanest vs most polluted, affordability champions, regional patterns).
  - `pages/09_Methodology_and_Limitations.py`: Methodology, formulas, data lineage, limitations (single snapshot, 10 traffic cities, crowdsourcing caveats).
- Commit.

### Phase 5: Testing, Headless Verification & Launch (M4)
- Create `tests/test_app.py` utilizing `streamlit.testing.v1.AppTest` to verify all 10 pages load without errors.
- Run full pytest test suite.
- Test headless execution with `streamlit run app.py --server.headless true`.
- Update `PROGRESS.md` to COMPLETED.
- Provide the launch command: `streamlit run app.py`.
