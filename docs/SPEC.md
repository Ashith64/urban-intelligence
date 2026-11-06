# SPEC: Urban Affordability x Air Quality Dashboard (BISL504)

## 1. Goal
Answer: "Which world cities are both affordable and breathable, and how do cost, purchasing power, air quality and traffic relate?" Deliver a professional Streamlit analytics platform + the 10 academic deliverables. Single real snapshot (Numbeo ~2025, IQAir 2024, TomTom 2025): there is NO time series, so do not build date selectors or trend charts; state this limitation in the report. Substitute with region/country comparison, rankings, what-if weights, correlation and distribution analysis.

## 2. Input files (data/raw/)
- numbeo_raw.csv (536 rows): Rank, City ("City, [State,] Country"), Cost of Living Index, Rent Index, Cost of Living Plus Rent Index, Groceries Index, Restaurant Price Index, Local Purchasing Power Index (New York = 100)
- iqair_raw.csv (124 rows): Rank, City_As_Published ("City, Country"), PM2_5_2024_ugm3, Source_Table (121 capitals + 3 US cities)
- tomtom_raw.csv (22 rows): City_As_Published ("City, CC"), Congestion_Level_2025_pct, Change_vs_2024_pp, Avg_Speed_kmh, Rush_Hours_Lost_per_Year, Source (many blanks are genuine: the source did not publish them)
- cities_reference.csv (161 rows): City, Country, Region, Latitude, Longitude: the project city scope

## 3. Pipeline (src/pipeline.py, run: python -m src.pipeline) -> data/processed/
For each source: parse label into City / State / Country; strip accents; apply aliases; drop exact duplicates; rename columns to snake-style (Cost_of_Living_Index, Rent_Index, Cost_of_Living_Plus_Rent_Index, Groceries_Index, Restaurant_Price_Index, Local_Purchasing_Power_Index, PM2_5_2024_ugm3, Congestion_Level_2025_pct, ...); flag outliers with the 1.5xIQR rule in an Outlier_Flags_IQR column (KEEP values); add Min-Max *_norm columns; add In_Project_Scope = (City, Country) present in cities_reference.
- City aliases: Tel Aviv-Yafo->Tel Aviv, Krakow (Cracow)->Krakow, Lucknow (Lakhnau)->Lucknow, Jeddah (Jiddah)->Jeddah, Kiev->Kyiv, New Delhi->Delhi, Dakha->Dhaka, Bengaluru->Bangalore, Washington D.C.->Washington; accents removed (Chisinau, Sao Paulo)
- Country aliases: USA/US->United States, Hong Kong SAR->Hong Kong, UK->United Kingdom, Bosnia Herzegovina->Bosnia and Herzegovina; TomTom ISO codes: MX Mexico, IN India, IE Ireland, TR Turkey, ID Indonesia, BR Brazil, NL Netherlands, JP Japan, FR France
- Numbeo scope special case: Portland is in scope only when State == OR
- Outputs: data/processed/{cost_of_living,air_quality,traffic}_processed.csv and data/processed/final_merged.csv
- Merge: Numbeo(in scope) INNER JOIN IQAir(in scope) on City+Country, LEFT JOIN TomTom(in scope), then join Region/Latitude/Longitude.
- Derived: Relative_Net_Income_Index = LPP x Cost_of_Living_Plus_Rent / 100; PM2_5_x_WHO_Guideline = PM2.5 / 5; PM2_5_WHO_Band (<=5 Meets guideline, 5-10 Interim 4, 10-15 Interim 3, 15-25 Interim 2, 25-35 Interim 1, >35 Above interim targets); Affordability_Air_Score_0_100 = 100 x (w1 x norm(LPP) + w2 x (1 - norm(PM2.5))), default w1=0.6, w2=0.4 (norms computed on the final merged set).

## 4. Validation numbers (pytest MUST assert these; if the pipeline disagrees, debug before continuing)
Numbeo 536 raw -> 161 in scope; IQAir 124 raw -> 72 in scope; TomTom 22 raw -> 22 in scope; FINAL = 72 cities, no duplicate (City, Country), 10 cities with real congestion; no nulls in cost or PM2.5 columns; Min-Max columns within [0,1]. Flagged outliers (IQR): Numbeo 19 cities, IQAir 9, TomTom 0.

## 5. Dashboard (app.py + pages/), sidebar navigation
1. Home: title, one-paragraph purpose, 5 KPI cards (cities, countries, median purchasing power, median PM2.5, share of cities above WHO guideline), data-source badges, how-to-use.
2. Data Profiling (Phase 2): per source row/column counts, dtypes, missing-value heatmap/bars, outlier table with IQR flags, before/after (raw labels vs standardised), validation checks.
3. Explore: sidebar filters (Region, Country, PM2.5 band, purchasing-power range). Scatter purchasing power vs PM2.5 (log y, WHO guideline line at 5), selectable points drive a linked detail panel (KPIs + table). Tooltips on all charts.
4. Map: Plotly scatter_geo (no API token): colour = metric chosen by dropdown, size = cost of living; hover shows all metrics.
5. Compare Cities: choose 2-5 cities; grouped bars of normalised metrics + a radar chart; side-by-side table.
6. Rankings (what-if): sliders for the two score weights (auto-normalised to sum 1), live Top-N bar chart and ranking table, download button for CSV.
7. Correlation & Distribution: Pearson/Spearman heatmap (choose method), histograms and box plots by Region (Plotly), seaborn/matplotlib static figure with st.pyplot for at least one chart; caption each chart with its takeaway.
8. Data Explorer: interactive table (st.dataframe), column picker, download buttons (raw/processed/final).
9. Insights: auto-generated findings computed from the data (strongest correlation, cleanest and most polluted cities, best affordability-air score, region medians, share above WHO guideline). No hardcoded text numbers.
10. Methodology & Limits: sources, pipeline steps, formulas, limitations (single snapshot; IQAir values are mostly capital cities; only 10 cities have traffic data; Numbeo is crowd-sourced; hand-transcribed values).

## 6. Design and accessibility
Clean, calm, professional. One accent colour; Okabe-Ito colour-blind-safe palette for categories; never rely on colour alone (add labels/symbols); every chart has a title, axis labels with units and a one-line caption; contrast >= 4.5:1; light and dark friendly (use Streamlit theme config in .streamlit/config.toml); consistent card/KPI styling via one helper; responsive layout (st.columns that stack). Empty/error states for every filter combination (e.g. "No cities match these filters").

## 7. Repository structure
app.py, pages/, src/{config.py,data_loader.py,pipeline.py,analysis.py,charts.py,insights.py}, data/{raw,processed}, docs/, tests/, .streamlit/config.toml, requirements.txt, requirements-dev.txt, README.md, PROGRESS.md

## 8. Academic deliverables (write into docs/; every number computed by code and read from docs/generated/*.json or *.csv)
- Phase 1: docs/01_tool_selection.md: compare Power BI, Tableau Public, Looker Studio, Excel, Streamlit+Plotly against this project (cost, interactivity, reproducibility, deployment, learning value); justify Streamlit+Plotly.
- Phase 2: docs/02_dataset_profiling.md generated by script (sources/credibility, profiling, missing-value analysis, outlier detection, 8+ analytical questions).
- Phase 3: docs/03_project_proposal.md: problem statement, objectives, chart-mapping table (question -> chart -> columns), ASCII wireframes for each page, Version 1 vs Version 2 of the proposal and why it changed.
- Phase 4: docs/04_implementation.md: cleaning decisions with reasons (why real values are not imputed or capped), aggregation, analysis, core visualisations (save PNGs to docs/figures/ using matplotlib).
- Phase 5: docs/05_usability_testing.md: heuristic checklist, 5 task scenarios with a results template for real users, accessibility checks, plus automated results (pytest, AppTest).
- Phase 6: docs/06_final_report.md (abstract, intro, data, method, results, discussion, limitations, conclusion, references), docs/slides.pptx (python-pptx, 12-15 slides with figures), docs/07_viva_qa.md (30 questions and answers grounded in this project, including tricky ones about limitations).
- README.md: install (python -m venv .venv; activate; pip install -r requirements.txt), run (python -m src.pipeline; streamlit run app.py), tests, structure, Streamlit Community Cloud deployment steps.

## 9. Quality gates
pytest passes (pipeline counts, no duplicates, norm ranges, derived-metric formulas, insights function outputs); every page passes streamlit.testing.v1.AppTest without exceptions; `streamlit run app.py --server.headless true` starts and serves HTTP 200 on localhost:8501; fresh-venv install works from requirements.txt; no hardcoded results.

## 10. Non-goals
No time series, no synthetic/simulated data, no external API calls at runtime, no login system, no paid services.
