# BISL504 - Project Progress

Status: IN PROGRESS

## Current milestone
M2 - Analytical engine, cached data loader, and chart components.

## Completed
- [x] M0: Repository & dataset inspection, `.streamlit/config.toml`, `requirements.txt`, `requirements-dev.txt`.
- [x] M1: `src/config.py`, `src/pipeline.py`, `data/processed/*.csv`, `tests/test_pipeline.py` (6/6 tests passing).

## In progress
- [ ] M2: Build `src/data_loader.py`, `src/analysis.py`, `src/insights.py`, `src/charts.py`.

## Pending
- [ ] M3: Complete Streamlit dashboard (`app.py` + 9 multipage views).
- [ ] M4: AppTest smoke tests, headless verification, and final launch.

## Important decisions
- Streamlit is the dashboard framework.
- Plotly is the primary interactive visualization library, with Matplotlib/Seaborn for static distribution figures.
- Okabe-Ito colour-blind-safe palette used across all categorical charts.
- Only approved source datasets are permitted (`data/raw/`).
- No synthetic data, no imputation of missing traffic values.

## Last verified command
`python -m pytest tests/test_pipeline.py -v` -> 6 passed in 0.87s.

## Next action
Implement `src/data_loader.py`, `src/analysis.py`, `src/insights.py`, and `src/charts.py`.
