# BISL504 - Permanent Agent Instructions

## Mission
Build the complete Urban Affordability & Liveability
Intelligence Platform.

## Fixed technology
- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Matplotlib
- Seaborn
- Pytest

## Scope
Only build the functional data visualization project.

Do not create PowerPoint presentations, academic reports,
viva documents or unrelated deliverables.

## Approved source datasets
- data/raw/numbeo_raw.csv
- data/raw/iqair_raw.csv
- data/raw/tomtom_raw.csv
- data/raw/cities_reference.csv

Never use the older synthetic datasets.

Never fabricate observations or historical trends.
Never overwrite original raw datasets.
Never replace missing traffic values with zero.

## Engineering rules
- Inspect existing code before changing it.
- Preserve working components.
- Use modular, reusable functions.
- Avoid unnecessary dependencies.
- Avoid duplicate calculations.
- Cache expensive data operations.
- Handle loading, empty and error states.
- Never silently suppress errors.
- Do not modify files outside this project.
- Do not expose credentials.
- Ask before destructive operations.

## Execution rules
- Work sequentially through implementation milestones.
- Prioritize functional completeness and speed.
- Avoid unnecessary planning loops.
- Do not repeatedly rewrite working components.
- Batch independent operations where safe.
- Never run conflicting agents against the same files.
- Test after meaningful implementation changes.
- Update PROGRESS.md after each milestone.
- Preserve exact unfinished tasks for recovery.

## Dashboard requirements
- Executive overview.
- Dataset profiling.
- City exploration.
- Global map.
- City comparison.
- Dynamic rankings.
- Correlation and distribution.
- Data explorer.
- Automated insights.
- Methodology and limitations.

## Verification
Run the pipeline, automated tests and live Streamlit app.
Verify charts, filters, comparisons, rankings and downloads.

## Launch
streamlit run app.py

Do not declare completion without actual verification.
