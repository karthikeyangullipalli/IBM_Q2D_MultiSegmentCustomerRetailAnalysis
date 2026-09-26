"""
pages/1_Dashboard.py
---------------------
Segmentation visualization (Income vs Spending, colored by persona, with
centroid markers) and a full persona overview: count, share, averages,
High-Value rate, business interpretation, and recommended strategy for
every dynamically discovered persona. Every number comes from the
trained model / current dataset — nothing here is hardcoded.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import streamlit as st

from src.persona_rules import get_marketing_action, get_persona_interpretation
from src.theme import COLORS, inject_theme_css, persona_color
from src.utils import (
    load_scored_customers,
    load_training_summary,
    models_exist,
    train_and_persist_models,
)

st.set_page_config(page_title="Dashboard | Retail Customer Intelligence", layout="wide")
inject_theme_css()


@st.cache_resource(show_spinner=False)
def get_summary():
    if not models_exist():
        return train_and_persist_models()
    return load_training_summary()


@st.cache_data(show_spinner=False)
def get_scored_customers():
    return load_scored_customers()


def build_scatter(df):
    fig = go.Figure()
    for persona in sorted(df["Persona"].unique()):
        group = df[df["Persona"] == persona]
        color = persona_color(persona)
        fig.add_trace(
            go.Scatter(
                x=group["Annual Income (k$)"],
                y=group["Spending Score (1-100)"],
                mode="markers",
                name=f"{persona} (n={len(group)})",
                marker=dict(size=9, color=color, opacity=0.82, line=dict(width=0.5, color="white")),
                customdata=group[["CustomerID", "Age", "Gender"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Age: %{customdata[1]}<br>"
                    "Gender: %{customdata[2]}<br>"
                    "Income: $%{x}k<br>"
                    "Spending Score: %{y}<extra>" + persona + "</extra>"
                ),
            )
        )

        centroid_x = group["Annual Income (k$)"].mean()
        centroid_y = group["Spending Score (1-100)"].mean()
        fig.add_trace(
            go.Scatter(
                x=[centroid_x],
                y=[centroid_y],
                mode="markers",
                marker=dict(size=15, color=color, symbol="x", line=dict(width=2, color=COLORS["primary"])),
                showlegend=False,
                hovertemplate=f"{persona} centroid<extra></extra>",
            )
        )

    fig.update_layout(
        height=520,
        font=dict(family="Inter, sans-serif", color=COLORS["primary"], size=13),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="v", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="Annual Income (k$)", gridcolor=COLORS["border"], zeroline=False),
        yaxis=dict(title="Spending Score (1-100)", gridcolor=COLORS["border"], zeroline=False),
    )
    return fig


def main():
    with st.spinner("Loading segment data..."):
        summary = get_summary()
        df = get_scored_customers()

    st.title("Dashboard")
    st.markdown(
        '<div class="app-subtitle">Customer segments discovered from Annual Income and '
        "Spending Score.</div>",
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

    st.markdown('<div class="section-label">Segment visualization</div>', unsafe_allow_html=True)
    st.plotly_chart(build_scatter(df), width="stretch")
    st.caption("X markers indicate each persona's centroid. Hover a point for customer detail.")

    with st.expander("View underlying customer records"):
        st.dataframe(df, width="stretch", hide_index=True)

    st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Persona overview</div>', unsafe_allow_html=True)

    persona_summary = summary["persona_summary"].sort_values("count", ascending=False)
    total = persona_summary["count"].sum()

    for _, row in persona_summary.iterrows():
        persona = row["Persona"]
        color = persona_color(persona)
        pct_of_base = row["count"] / total * 100
        st.markdown(
            f"""
            <div class="ui-card" style="border-left: 4px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                    <span style="font-size:1.05rem; font-weight:700; color:{COLORS['primary']};">{persona}</span>
                    <span style="color:{COLORS['text_secondary']}; font-size:0.85rem;">
                        {int(row['count'])} customers &middot; {pct_of_base:.1f}% of base
                    </span>
                </div>
                <div style="margin-top:0.5rem; color:{COLORS['text_secondary']}; font-size:0.88rem;">
                    Avg age <strong style="color:{COLORS['primary']};">{row['avg_age']:.0f}</strong>
                    &nbsp;&middot;&nbsp; Avg income
                    <strong style="color:{COLORS['primary']};">${row['avg_income']:.0f}k</strong>
                    &nbsp;&middot;&nbsp; Avg spending
                    <strong style="color:{COLORS['primary']};">{row['avg_spending']:.0f}</strong>
                    &nbsp;&middot;&nbsp; High-Value
                    <strong style="color:{COLORS['success']};">{row['pct_high_value']*100:.0f}%</strong>
                </div>
                <div style="margin-top:0.7rem; font-size:0.88rem; color:{COLORS['primary']};">
                    {get_persona_interpretation(persona)}
                </div>
                <div style="margin-top:0.4rem; font-size:0.85rem; color:{COLORS['text_secondary']};">
                    <strong>Strategy:</strong> {get_marketing_action(persona)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


main()
