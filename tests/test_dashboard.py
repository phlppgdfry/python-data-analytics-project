from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "relative_path",
    [
        "dashboard/app.py",
        "dashboard/pages/overview.py",
        "dashboard/pages/profitability.py",
        "dashboard/pages/customers.py",
        "dashboard/pages/forecast.py",
        "dashboard/pages/data_quality.py",
    ],
)
def test_dashboard_pages_render_without_exceptions(relative_path):
    app = AppTest.from_file(str(PROJECT_ROOT / relative_path)).run(timeout=30)
    assert not app.exception
