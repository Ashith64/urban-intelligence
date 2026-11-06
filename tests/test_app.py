"""Automated AppTest test suite validating that all Streamlit pages render cleanly."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

ROOT_DIR = Path(__file__).resolve().parent.parent

PAGES = [
    "app.py",
    "pages/1_Home.py",
    "pages/2_Data_Profiling.py",
    "pages/3_Explore.py",
    "pages/4_Map.py",
    "pages/5_Compare_Cities.py",
    "pages/6_Rankings.py",
    "pages/7_Correlation_and_Distribution.py",
    "pages/8_Data_Explorer.py",
    "pages/9_Insights.py",
    "pages/10_Methodology_and_Limits.py",
]


@pytest.mark.parametrize("page_path", PAGES)
def test_streamlit_page_renders_without_exception(page_path: str):
    """Run Streamlit AppTest for each page file and assert no exceptions occurred."""
    abs_path = (ROOT_DIR / page_path).resolve()
    assert abs_path.exists(), f"Page file does not exist: {abs_path}"

    at = AppTest.from_file(str(abs_path), default_timeout=15)
    at.run()

    assert not at.exception, f"Exception occurred while rendering {page_path}: {at.exception}"
