/plan
You are a senior data-visualization engineer. Build the COMPLETE BISL504 project in this folder, fully autonomously, from start to finish, without asking me questions.

Before anything else: read AGENTS.md, docs/SPEC.md and PROGRESS.md in full, and inspect the 4 files in data/raw/. SPEC.md is the single source of truth.

Step 1 (plan): write a short implementation_plan.md listing the milestones M0-M7 from PROGRESS.md and the files each will create. Then proceed immediately.

Execute milestones in order. After each one: run the checks from AGENTS.md (pytest, AppTest smoke, live run), tick it in PROGRESS.md, git commit, and continue automatically:
M0  Windows venv, requirements.txt (+ requirements-dev.txt), skeleton, .streamlit/config.toml, git init.
M1  src/pipeline.py + data_loader + tests: reproduce the validation numbers in SPEC section 4 exactly.
M2  Profiling module + docs/02_dataset_profiling.md generated from the data.
M3  All 10 dashboard pages from SPEC section 5 with linked views, tooltips, filters, accessible colours and a consistent professional look.
M4  Tests: pytest + AppTest for every page + headless run check; open http://localhost:8501 in the browser, take screenshots of each page into docs/figures/, and fix any visual or functional defect you see (overlaps, empty charts, errors).
M5  docs 01, 03, 04, 05 as specified.
M6  docs/06_final_report.md, docs/slides.pptx, docs/07_viva_qa.md, README.md.
M7  Final audit: verify all 10 deliverables exist, every number in the docs matches the data, run the full test suite from a fresh venv, then print a checklist summary and the exact commands to launch the dashboard.

Rules: real data only (never simulate, impute or alter real values); no hardcoded results; modular code; no silent failures; if a check fails twice, stop and show the error log. If the conversation becomes very long, finish the current milestone, commit, update PROGRESS.md and print "HANDOFF READY".
