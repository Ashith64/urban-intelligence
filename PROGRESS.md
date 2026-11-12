# URBAN INTELLIGENCE: The Global Liveability Observatory

## Status: COMPLETE & VERIFIED ✅

### Product Identity
- **Product Name**: URBAN INTELLIGENCE
- **Subtitle**: THE GLOBAL LIVEABILITY OBSERVATORY
- **Central Question**: *"Where can people enjoy a better balance of affordability, purchasing power, quality of life and environmental conditions?"*

---

## 1. Design System: Obsidian Luxe (`src/theme.py`, `.streamlit/config.toml`)
- **Colour Tokens**:
  - Main Background: `#0B0E12`
  - Sidebar: `#10151B`
  - Primary Surface: `#141A21`
  - Elevated Surface: `#1B232C`
  - Structural Borders: `#28323D`
  - Primary Text: `#F0F1ED`
  - Secondary Text: `#929DA8`
  - Emerald: `#55B89A` (Favourable environmental outcomes & clean air)
  - Champagne Gold: `#C6A46A` (Economic benchmarks & highlights)
  - Muted Coral: `#D97870` (Adverse conditions & severe pollution)
  - Silver: `#929DA8` (Neutral structural framing)
- **Shared Plotly Template**: `obsidian_luxe` registered and default across all views.
- **Typography**: Inter (UI Structure) + JetBrains Mono (Technical Numeric Values).

---

## 2. Five Unified Destinations

### 🏛️ Page 1: Executive Dashboard (`pages/1_Executive_Dashboard.py`)
- **Hero Banner**: "Where does your money go further? Explore how affordability, purchasing power and quality of life vary across global cities."
- **Observation Metadata**: 238 metropolises across 82 countries & areas, 2024–2025 benchmark, offline verified cache.
- **4 Prominent KPI Cards**: Cities Analysed (238), Countries & Areas (82), Median Purchasing Power (72.5), Median House Price Multiple (11.2×).
- **The Liveability Quadrant**: 4-zone scatter plot mapping Purchasing Power vs. Inverted Pollution with custom tooltip cards and quadrant highlights.
- **3 Automatically Calculated Findings**: Peak purchasing power, lowest consumer basket, cleanest environment.
- **Regional Disparity Visual**: Bubble chart comparing continental medians.

### 🔍 Page 2: City Explorer (`pages/2_City_Explorer.py`)
- **Contextual Filters**: Region, Country, City search, Purchasing power, Cost of living, Pollution, Safety, and Healthcare.
- **City Relationship Explorer**: Interactive scatter with selectable X and Y variables, linear/log scale toggle, and native OLS regression line.
- **Global 238-City World Map**: `scatter_geo` projection with semantic color scales.
- **City Passport**: Complete 10-dimensional diagnostic profile with percentile rankings and World Bank macroeconomic context.

### ⚔️ Page 3: Head-to-Head Arena (`pages/3_Head_to_Head.py`)
- **Contender Selector**: Compare 2 to 4 cities simultaneously.
- **Contender Summary Battle Cards**: High-contrast cards highlighting key indicators side-by-side.
- **Grouped Bar Charts & Direct Comparison Table**: Detailed indicator levels.
- **6-Axis Spider / Radar Profile**: Translucent overlaid polygons for normalized dimensions.
- **Benchmark Variance Matrix**: Percentage delta ($\pm\%$) relative to chosen base city.
- **Interactive Lifestyle Simulator**:
  - 3 Instant Presets (*Affordability First*, *Environment First*, *Balanced Priorities*)
  - Manual weight sliders with normalized score re-ranking.

### 🔬 Page 4: Analysis & Findings (`pages/4_Analysis_Findings.py`)
*The Central Interactive Analytical Workspace:*
- **Section A — Discovery Feed**: Real-time algorithmic discoveries (sample size $N=238$, 2024–2025 period, source lineage, expandable drawer).
- **Section B — Statistical Overview**: 12 summary statistics (Mean, Median, Min, Max, Range, Std, Variance, Q1, Q3, IQR, Missing %) + Distribution chart with mean/median reference lines.
- **Section C — Relationship Explorer**: Bivariate scatter with OLS regression, Pearson $r$, Spearman $\rho$, and causality disclaimers.
- **Section D — Correlation Studio**: Pearson and Spearman heatmaps with constituent exclusion safeguards.
- **Section E — Distribution Lab**: Histogram, Box Plot, and Violin Plot across world regions.
- **Section F — Regional Intelligence**: Ranked continental bar charts and comparative tables.
- **Section G — Custom Visualization Studio**: Full user chart builder (7 chart types, filters, aggregations, reset, CSV export, interactive HTML chart export).

### 🗄️ Page 5: Intelligence Data Room (`pages/5_Data_Room.py`)
- **Data Provenance**: Collection specifications for Numbeo, GeoNames, and World Bank APIs.
- **Searchable Master Explorer**: Filter, sort, and download the full 238-city database.
- **Mathematical Audit**: Automated validation table proving 11/11 normalized metrics strictly satisfy $[0.0, 1.0]$.
- **Outlier Preservation Policy**: Plain-English Tukey IQR policy.
- **Scientific Methodology**: KaTeX mathematical formulations for all indices.

---

## 3. Verification & Testing
- **Automated Test Suite**: `18 passed in 7.56s` (`pytest tests/`)
  - `tests/test_pipeline.py`: 6 tests passing (data integrity, coordinate coverage, World Bank joins, min-max bounds, edge cases).
  - `tests/test_analysis.py`: 6 tests passing (KPIs, univariate stats, discovery feed, presets, bivariate regression, correlation matrix).
  - `tests/test_app.py`: 6 tests passing (`AppTest` headless rendering for `app.py` and all 5 individual pages).

### Launch Command
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```
