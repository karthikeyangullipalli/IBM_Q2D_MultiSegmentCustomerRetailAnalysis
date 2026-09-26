"""
app.py
------
Streamlit entry point for the Retail Customer Intelligence application.
Bootstraps (trains) models on first run if they don't exist yet, and
renders the landing page. Dashboard, Predict, Insights, and Data
Explorer live in pages/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from src.theme import COLORS, inject_theme_css
from src.utils import load_training_summary, models_exist, train_and_persist_models

st.set_page_config(
    page_title="Retail Customer Intelligence",
    page_icon=None,
    layout="wide",
)
inject_theme_css()


@st.cache_resource(show_spinner=False)
def bootstrap_models():
    """Train models on first run if they don't exist yet; otherwise reuse them."""
    if not models_exist():
        return train_and_persist_models()
    return load_training_summary()


def main():
    with st.spinner("Loading models..."):
        summary = bootstrap_models()

    st.title("Retail Customer Intelligence")
    st.markdown(
        '<div class="app-subtitle">Data-driven customer segmentation and '
        "High-Value classification for retail decision support.</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", summary["n_customers"])
    col2.metric("Personas", summary["n_clusters"])
    col3.metric(
        "High-Value Customers",
        summary["high_value_count"],
        f"{summary['high_value_pct'] * 100:.1f}% of base",
    )
    col4.metric("Silhouette Score", f"{summary['silhouette_score']:.3f}")

    st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)

    st.markdown('<div class="section-label">System overview</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="ui-card">
        This system segments customers into behavioral personas using K-Means
        clustering on Annual Income and Spending Score, applies a transparent,
        documented rule to identify High-Value customers, and trains a
        calibrated Random Forest classifier so new customers can be scored
        instantly without re-running clustering.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Pages</div>', unsafe_allow_html=True)
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        st.markdown(
            """
            <div class="ui-card">
            <strong>Dashboard</strong><br>
            <span style="color:#5B6472;font-size:0.9rem;">
            Segment visualization, persona breakdown, and headline KPIs.
            </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="ui-card">
            <strong>Insights</strong><br>
            <span style="color:#5B6472;font-size:0.9rem;">
            Cluster selection analysis, persona comparison, and business insights.
            </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nav_col2:
        st.markdown(
            """
            <div class="ui-card">
            <strong>Predict</strong><br>
            <span style="color:#5B6472;font-size:0.9rem;">
            Score a hypothetical customer and see a full explanation of the result.
            </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="ui-card">
            <strong>Data Explorer</strong><br>
            <span style="color:#5B6472;font-size:0.9rem;">
            Filter and export the underlying customer records.
            </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<p style="color:{COLORS["text_muted"]};font-size:0.85rem;">'
        "Use the sidebar to navigate between pages.</p>",
        unsafe_allow_html=True,
    )


main()
