"""Start met: streamlit run dashboard/app.py"""

from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.shared import apply_global_style  # noqa: E402


st.set_page_config(page_title="Sales analytics", page_icon="📊", layout="wide")
apply_global_style()

navigation = st.navigation(
    {
        "Sales intelligence": [
            st.Page("pages/overview.py", title="Executive overview", icon="📊", default=True),
            st.Page("pages/profitability.py", title="Sales & profitability", icon="💶"),
            st.Page("pages/customers.py", title="Customer intelligence", icon="👥"),
            st.Page("pages/forecast.py", title="Forecast & alerts", icon="🔭"),
        ],
        "Operations": [
            st.Page("pages/data_quality.py", title="Data quality", icon="✅"),
        ],
    },
    position="sidebar",
)
navigation.run()
