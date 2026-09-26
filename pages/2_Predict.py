"""
pages/2_Predict.py
--------------------
The primary demo page. A customer profile goes in; a decision-support
panel comes out: predicted persona, High-Value status, a calibrated
confidence score, a deterministic marketing recommendation, and a
"Why This Prediction?" explanation grounded in actual centroid
distances and comparisons to real dataset/persona averages — nothing
here is invented.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.classifier import predict_customer
from src.persona_rules import generate_marketing_recommendation
from src.theme import COLORS, inject_theme_css, persona_color
from src.utils import models_exist, train_and_persist_models

st.set_page_config(page_title="Predict | Retail Customer Intelligence", layout="wide")
inject_theme_css()


@st.cache_resource(show_spinner=False)
def ensure_models():
    if not models_exist():
        train_and_persist_models()
    return True


def _delta_phrase(delta: float, unit: str = "") -> str:
    if abs(delta) < 1e-9:
        return f"in line with{(' ' + unit) if unit else ''}"
    direction = "above" if delta > 0 else "below"
    return f"{abs(delta):.1f}{unit} {direction}"


def render_result(result: dict, age: int, gender: str, income: float, score: float) -> None:
    persona = result["persona"]
    high_value = result["high_value"]
    probability = result["probability"]
    exp = result["explanation"]
    color = persona_color(persona)

    # --- Customer profile -------------------------------------------------
    st.markdown('<div class="section-label">Customer profile</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ui-card">
            <span style="color:{COLORS['text_secondary']};">
                Age <strong style="color:{COLORS['primary']};">{age}</strong> &nbsp;&middot;&nbsp;
                Gender <strong style="color:{COLORS['primary']};">{gender}</strong> &nbsp;&middot;&nbsp;
                Annual Income <strong style="color:{COLORS['primary']};">${income:.0f}k</strong> &nbsp;&middot;&nbsp;
                Spending Score <strong style="color:{COLORS['primary']};">{score:.0f}</strong>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Persona + High-Value status ---------------------------------------
    status_text = "HIGH-VALUE" if high_value else "NOT HIGH-VALUE"
    status_bg = COLORS["success"] if high_value else COLORS["text_muted"]

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="section-label">Predicted persona</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ui-card" style="border-left: 5px solid {color};">
                <div style="font-size:1.5rem; font-weight:700; color:{color};">{persona}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown('<div class="section-label">High-value status</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ui-card" style="text-align:center;">
                <span class="ui-badge" style="background-color:{status_bg}; color:#FFFFFF;">{status_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Confidence + recommendation ---------------------------------------
    col3, col4 = st.columns([1, 2])
    with col3:
        st.markdown('<div class="section-label">Confidence</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ui-card">
                <div style="font-size:1.4rem; font-weight:700; color:{COLORS['primary']};">
                    {probability * 100:.1f}%
                </div>
                <div style="font-size:0.78rem; color:{COLORS['text_muted']}; margin-top:0.2rem;">
                    Calibrated High-Value likelihood — reflects model confidence,
                    not a guaranteed real-world outcome.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown('<div class="section-label">Recommended marketing action</div>', unsafe_allow_html=True)
        recommendation = generate_marketing_recommendation(persona, age, income, score, high_value)
        st.markdown(f'<div class="ui-card">{recommendation}</div>', unsafe_allow_html=True)

    # --- Why this prediction -------------------------------------------------
    st.markdown('<div class="section-label">Why this prediction</div>', unsafe_allow_html=True)
    income_phrase = _delta_phrase(exp["income_vs_dataset_avg"], "k")
    spending_phrase = _delta_phrase(exp["spending_vs_persona_avg"])
    ratio = (
        exp["distance_to_next_closest_centroid"] / exp["distance_to_assigned_centroid"]
        if exp["distance_to_assigned_centroid"] > 0
        else float("inf")
    )
    st.markdown(
        f"""
        <div class="ui-card">
            <ul style="margin:0; padding-left:1.1rem; color:{COLORS['primary']}; font-size:0.9rem; line-height:1.7;">
                <li>Annual income (${income:.0f}k) is <strong>${abs(exp['income_vs_dataset_avg']):.1f}k
                    {'above' if exp['income_vs_dataset_avg'] >= 0 else 'below'}</strong> the dataset average
                    (${income - exp['income_vs_dataset_avg']:.1f}k).</li>
                <li>Spending score ({score:.0f}) is <strong>{abs(exp['spending_vs_persona_avg']):.1f} points
                    {'above' if exp['spending_vs_persona_avg'] >= 0 else 'below'}</strong> the average for
                    the {persona} segment ({exp['persona_avg_spending']:.1f}).</li>
                <li>Age ({age}) is <strong>{abs(exp['age_vs_dataset_avg']):.1f} years
                    {'above' if exp['age_vs_dataset_avg'] >= 0 else 'below'}</strong> the dataset average.</li>
                <li>This customer is <strong>{ratio:.1f}x closer</strong> (in standardized distance) to the
                    {persona} centroid than to the next-closest segment,
                    {exp['next_closest_persona']} — a {'clear' if ratio > 2 else 'moderate'} match.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    ensure_models()

    st.title("Predict")
    st.markdown(
        '<div class="app-subtitle">Enter a hypothetical customer to see their predicted '
        "persona, High-Value status, and the reasoning behind it.</div>",
        unsafe_allow_html=True,
    )

    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.slider("Age", min_value=18, max_value=80, value=35, step=1)
            gender = st.selectbox("Gender", ["Male", "Female"])
        with col2:
            income = st.slider("Annual Income (k$)", min_value=0, max_value=150, value=60, step=1)
            score = st.slider("Spending Score (1-100)", min_value=1, max_value=100, value=50, step=1)
        submitted = st.form_submit_button("Analyze Customer", width="stretch")

    if submitted:
        result = predict_customer(age=age, gender=gender, income=income, score=score)
        st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)
        render_result(result, age, gender, income, score)
    else:
        st.caption("Fill in the details above and click Analyze Customer to see a result.")


main()
