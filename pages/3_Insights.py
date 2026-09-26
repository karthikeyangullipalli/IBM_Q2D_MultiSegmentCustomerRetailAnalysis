"""
pages/3_Insights.py
---------------------
Analytical deep-dive: the evidence behind the cluster-count choice,
persona comparison, classifier feature importance, High-Value analytics,
and deterministic business insights. Every chart reads from the trained
model bundle / current dataset — nothing here is a fixed illustration.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import plotly.graph_objects as go
import streamlit as st

from src.classifier import CLASSIFIER_PATH
from src.persona_rules import generate_business_insights
from src.theme import COLORS, inject_theme_css, persona_color
from src.utils import (
    DEFAULT_MODELS_DIR,
    load_scored_customers,
    load_training_summary,
    models_exist,
    train_and_persist_models,
)

st.set_page_config(page_title="Insights | Retail Customer Intelligence", layout="wide")
inject_theme_css()


@st.cache_resource(show_spinner=False)
def get_summary():
    if not models_exist():
        return train_and_persist_models()
    return load_training_summary()


@st.cache_resource(show_spinner=False)
def get_classifier():
    return joblib.load(CLASSIFIER_PATH)


@st.cache_data(show_spinner=False)
def get_scored_customers():
    return load_scored_customers()


def line_chart(k_eval, y_col, title, selected_k):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=k_eval["k"], y=k_eval[y_col], mode="lines+markers",
            line=dict(color=COLORS["secondary"], width=2),
            marker=dict(size=7, color=COLORS["secondary"]),
        )
    )
    selected_row = k_eval[k_eval["k"] == selected_k]
    if not selected_row.empty:
        fig.add_trace(
            go.Scatter(
                x=selected_row["k"], y=selected_row[y_col], mode="markers",
                marker=dict(size=13, color=COLORS["accent"], symbol="circle",
                            line=dict(width=2, color=COLORS["primary"])),
                showlegend=False,
                hovertemplate=f"Selected K={selected_k}<extra></extra>",
            )
        )
    fig.update_layout(
        height=320,
        title=dict(text=title, font=dict(size=14, color=COLORS["primary"])),
        font=dict(family="Inter, sans-serif", color=COLORS["primary"], size=12),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
        xaxis=dict(title="K (number of clusters)", gridcolor=COLORS["border"], dtick=1),
        yaxis=dict(title=y_col.replace("_", " ").title(), gridcolor=COLORS["border"]),
    )
    return fig


def persona_bar_chart(persona_summary, y_col, title, y_label):
    colors = [persona_color(p) for p in persona_summary["Persona"]]
    fig = go.Figure(
        go.Bar(x=persona_summary["Persona"], y=persona_summary[y_col], marker_color=colors)
    )
    fig.update_layout(
        height=320,
        title=dict(text=title, font=dict(size=14, color=COLORS["primary"])),
        font=dict(family="Inter, sans-serif", color=COLORS["primary"], size=12),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(title=y_label, gridcolor=COLORS["border"]),
    )
    return fig


def main():
    with st.spinner("Loading analysis..."):
        summary = get_summary()
        classifier_model = get_classifier()
        df = get_scored_customers()

    st.title("Insights")
    st.markdown(
        '<div class="app-subtitle">The evidence behind the model\'s choices, '
        "and what the results mean for the business.</div>",
        unsafe_allow_html=True,
    )

    # --- Cluster selection ---------------------------------------------------
    st.markdown('<div class="section-label">Cluster selection analysis</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ui-card">K = {summary["n_clusters"]} was selected automatically by '
        f"maximizing silhouette score across K = 2 through K = 10 on the clustering features "
        f"({', '.join(summary['cluster_features'])}) — evaluated below, not assumed.</div>",
        unsafe_allow_html=True,
    )
    k_eval = summary["k_evaluation"]
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(line_chart(k_eval, "inertia", "K vs Inertia", summary["n_clusters"]), width="stretch")
    with c2:
        st.plotly_chart(
            line_chart(k_eval, "silhouette_score", "K vs Silhouette Score", summary["n_clusters"]),
            width="stretch",
        )

    st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)

    # --- Persona comparison ---------------------------------------------------
    st.markdown('<div class="section-label">Persona comparison</div>', unsafe_allow_html=True)
    persona_summary = summary["persona_summary"].sort_values("count", ascending=False)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.plotly_chart(
            persona_bar_chart(persona_summary, "avg_income", "Average Income by Persona", "Income (k$)"),
            width="stretch",
        )
        st.plotly_chart(
            persona_bar_chart(persona_summary, "count", "Customer Count by Persona", "Customers"),
            width="stretch",
        )
    with pc2:
        st.plotly_chart(
            persona_bar_chart(persona_summary, "avg_spending", "Average Spending Score by Persona", "Spending Score"),
            width="stretch",
        )
        st.plotly_chart(
            persona_bar_chart(persona_summary, "avg_age", "Average Age by Persona", "Age"),
            width="stretch",
        )

    st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)

    # --- Feature importance ---------------------------------------------------
    st.markdown('<div class="section-label">Classifier feature relevance</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ui-card">Random Forest feature importance is shown here because the '
        f"High-Value classifier is a genuine supervised task with a properly defined binary "
        f"target (the persona-rules High-Value label) — it is not attached to the unsupervised "
        f"clustering step, which uses only {' and '.join(summary['cluster_features'])}.</div>",
        unsafe_allow_html=True,
    )
    importances = sorted(
        zip(classifier_model.feature_columns_, classifier_model.feature_importances_),
        key=lambda x: x[1],
    )
    fig_fi = go.Figure(
        go.Bar(
            x=[v for _, v in importances], y=[f for f, _ in importances], orientation="h",
            marker_color=COLORS["accent"],
        )
    )
    fig_fi.update_layout(
        height=280,
        font=dict(family="Inter, sans-serif", color=COLORS["primary"], size=12),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="Relative importance", gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )
    st.plotly_chart(fig_fi, width="stretch")

    st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)

    # --- High-value analytics ---------------------------------------------------
    st.markdown('<div class="section-label">High-value analytics</div>', unsafe_allow_html=True)
    hv = summary["high_value_stats"]
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("High-Value Customers", hv["count"], f"{hv['pct_of_base']*100:.1f}% of base")
    h2.metric("Avg Income (High-Value)", f"${hv['avg_income']:.0f}k")
    h3.metric("Avg Spending (High-Value)", f"{hv['avg_spending']:.0f}")
    h4.metric("Share of Total Spending", f"{hv['share_of_total_spending']*100:.1f}%")

    st.plotly_chart(
        persona_bar_chart(persona_summary, "high_value_count", "High-Value Customers by Persona", "High-Value Customers"),
        width="stretch",
    )

    st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)

    # --- Business insights ---------------------------------------------------
    st.markdown('<div class="section-label">Business insights</div>', unsafe_allow_html=True)
    for insight in generate_business_insights(persona_summary):
        st.markdown(
            f"""
            <div class="ui-card">
                <div style="font-weight:600; color:{COLORS['primary']}; margin-bottom:0.2rem;">
                    {insight['title']}
                </div>
                <div style="color:{COLORS['text_secondary']}; font-size:0.9rem;">
                    {insight['detail']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


main()
