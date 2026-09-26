"""
pages/4_Data_Explorer.py
--------------------------
Filter and browse the actual scored customer records (persona, gender,
age range, income range, spending range), and export the filtered
result as CSV. No synthetic rows — this reads the real dataset/model
output produced during training.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.theme import inject_theme_css
from src.utils import load_scored_customers, models_exist, train_and_persist_models

st.set_page_config(page_title="Data Explorer | Retail Customer Intelligence", layout="wide")
inject_theme_css()


@st.cache_resource(show_spinner=False)
def ensure_models():
    if not models_exist():
        train_and_persist_models()
    return True


@st.cache_data(show_spinner=False)
def get_scored_customers():
    return load_scored_customers()


def main():
    ensure_models()

    st.title("Data Explorer")
    st.markdown(
        '<div class="app-subtitle">Filter and export the underlying customer records.</div>',
        unsafe_allow_html=True,
    )

    df = get_scored_customers()

    st.markdown('<div class="section-label">Filters</div>', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        personas = st.multiselect("Persona", sorted(df["Persona"].unique()), default=None)
        genders = st.multiselect("Gender", sorted(df["Gender"].unique()), default=None)
    with f2:
        age_range = st.slider(
            "Age range", int(df["Age"].min()), int(df["Age"].max()),
            (int(df["Age"].min()), int(df["Age"].max())),
        )
        income_range = st.slider(
            "Annual Income (k$) range",
            int(df["Annual Income (k$)"].min()), int(df["Annual Income (k$)"].max()),
            (int(df["Annual Income (k$)"].min()), int(df["Annual Income (k$)"].max())),
        )
    spending_range = st.slider(
        "Spending Score range",
        int(df["Spending Score (1-100)"].min()), int(df["Spending Score (1-100)"].max()),
        (int(df["Spending Score (1-100)"].min()), int(df["Spending Score (1-100)"].max())),
    )

    filtered = df.copy()
    if personas:
        filtered = filtered[filtered["Persona"].isin(personas)]
    if genders:
        filtered = filtered[filtered["Gender"].isin(genders)]
    filtered = filtered[filtered["Age"].between(*age_range)]
    filtered = filtered[filtered["Annual Income (k$)"].between(*income_range)]
    filtered = filtered[filtered["Spending Score (1-100)"].between(*spending_range)]

    st.markdown('<hr class="ui-divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-label">Results ({len(filtered)} of {len(df)} customers)</div>',
        unsafe_allow_html=True,
    )

    export_df = filtered.rename(columns={"High_Value": "High-Value Status"}).copy()
    export_df["High-Value Status"] = export_df["High-Value Status"].map(
        {1: "High-Value", 0: "Not High-Value"}
    )

    st.dataframe(export_df, width="stretch", hide_index=True)

    st.download_button(
        "Download filtered results as CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="customer_segmentation_export.csv",
        mime="text/csv",
    )


main()
