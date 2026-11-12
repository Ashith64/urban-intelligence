# BISL504 - Project Progress

Status: IN PROGRESS

## Current milestone
M1 - Data preprocessing pipeline & validation.

## Completed
- [x] M0: Repository & dataset inspection, `.streamlit/config.toml`, `requirements.txt`, `requirements-dev.txt`.

## In progress
- [ ] M1: Build `src/config.py`, `src/pipeline.py`, generate `data/processed/`, verify with `tests/test_pipeline.py`.

## Pending
- [ ] M2: Analytical core (`src/data_loader.py`, `src/analysis.py`, `src/insights.py`, `src/charts.py`).
- [ ] M3: Complete Streamlit dashboard (`app.py` + 9 multipage views).
- [ ] M4: AppTest smoke tests, headless verification, and final launch.

## Important decisions
- Streamlit is the dashboard framework.
- Plotly is the primary interactive visualization library, with Matplotlib/Seaborn for static distribution figures.
- Okabe-Ito colour-blind-safe palette used across all categorical charts.
- Only approved source datasets are permitted (`data/raw/`).
- No synthetic data, no imputation of missing traffic values.

## Last verified command
`python -c "import streamlit, plotly, pandas, numpy, seaborn, matplotlib, pytest; print('ALL PACKAGES LOADED SUCCESSFULLY!')"` -> exited 0.

## Next action
Implement `src/config.py`, `src/pipeline.py`, and `tests/test_pipeline.py`.
