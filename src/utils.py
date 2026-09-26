"""
utils.py
--------
Glue/orchestration helpers that aren't part of the core service-layer
contract but are needed to wire data_loader -> clustering -> classifier
-> persisted model artifacts. Used by the training notebook and by
app.py's first-run bootstrap (auto-train if models/ is empty).
"""

from pathlib import Path
from typing import Dict

import joblib
import pandas as pd

from src.classifier import train_classifier
from src.clustering import derive_high_value_labels, fit_clusters
from src.data_loader import load_and_clean_data

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mall_customers.csv"
DEFAULT_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def train_and_persist_models(
    data_path: Path = DEFAULT_DATA_PATH,
    models_dir: Path = DEFAULT_MODELS_DIR,
) -> Dict[str, object]:
    """
    Run the full pipeline end-to-end: load data -> fit K-Means -> derive
    High-Value labels -> train the Random Forest -> save both model
    bundles with joblib. Returns a summary dict of real metrics (no
    placeholders) for the Dashboard/Insights pages and the case study
    report.
    """
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    df = load_and_clean_data(str(data_path))

    # n_clusters is intentionally omitted: fit_clusters() evaluates K=2..10
    # by silhouette score and selects the best one — the cluster count is
    # not assumed.
    kmeans, cluster_labels, persona_names = fit_clusters(df)
    high_value_labels = derive_high_value_labels(cluster_labels, kmeans)

    classifier_model, metrics = train_classifier(df, high_value_labels)

    joblib.dump(kmeans, models_dir / "kmeans_model.pkl")
    joblib.dump(classifier_model, models_dir / "classifier_model.pkl")

    # Persona breakdown for the Dashboard's summary cards / report numbers
    working = df.copy()
    working["Cluster"] = cluster_labels
    working["Persona"] = working["Cluster"].map(persona_names)
    working["High_Value"] = high_value_labels

    persona_summary = (
        working.groupby("Persona")
        .agg(
            count=("Persona", "size"),
            avg_age=("Age", "mean"),
            avg_income=("Annual Income (k$)", "mean"),
            avg_spending=("Spending Score (1-100)", "mean"),
            pct_high_value=("High_Value", "mean"),
            high_value_count=("High_Value", "sum"),
        )
        .round(2)
        .reset_index()
    )

    high_value_df = working[working["High_Value"] == 1]
    high_value_stats = {
        "count": int(len(high_value_df)),
        "pct_of_base": float(len(high_value_df) / len(working)) if len(working) else 0.0,
        "avg_income": float(high_value_df["Annual Income (k$)"].mean()) if len(high_value_df) else 0.0,
        "avg_spending": float(high_value_df["Spending Score (1-100)"].mean()) if len(high_value_df) else 0.0,
        "avg_age": float(high_value_df["Age"].mean()) if len(high_value_df) else 0.0,
        "share_of_total_income": float(
            high_value_df["Annual Income (k$)"].sum() / working["Annual Income (k$)"].sum()
        ) if working["Annual Income (k$)"].sum() else 0.0,
        "share_of_total_spending": float(
            high_value_df["Spending Score (1-100)"].sum() / working["Spending Score (1-100)"].sum()
        ) if working["Spending Score (1-100)"].sum() else 0.0,
    }

    summary = {
        "n_customers": int(len(df)),
        "n_clusters": int(kmeans.n_clusters),
        "silhouette_score": kmeans.silhouette_score_,
        "k_evaluation": kmeans.k_evaluation_,
        "cluster_features": kmeans.cluster_features_,
        "classifier_metrics": metrics,
        "high_value_count": int(high_value_labels.sum()),
        "high_value_pct": float(high_value_labels.mean()),
        "high_value_stats": high_value_stats,
        "persona_summary": persona_summary,
    }

    joblib.dump(summary, models_dir / "training_summary.pkl")

    scored_cols = [
        "CustomerID",
        "Gender",
        "Age",
        "Annual Income (k$)",
        "Spending Score (1-100)",
        "Cluster",
        "Persona",
        "High_Value",
    ]
    working[scored_cols].to_csv(models_dir / "scored_customers.csv", index=False)

    return summary


def load_scored_customers(models_dir: Path = DEFAULT_MODELS_DIR) -> pd.DataFrame:
    """Load the per-customer cluster/persona/high-value assignments from training time."""
    scored_path = Path(models_dir) / "scored_customers.csv"
    if not scored_path.exists():
        raise FileNotFoundError(
            f"No scored customer data at {scored_path}. Run "
            "train_and_persist_models() first."
        )
    return pd.read_csv(scored_path)


def load_training_summary(models_dir: Path = DEFAULT_MODELS_DIR) -> Dict[str, object]:
    """Load the cached metrics/summary produced by train_and_persist_models()."""
    summary_path = Path(models_dir) / "training_summary.pkl"
    if not summary_path.exists():
        raise FileNotFoundError(
            f"No training summary at {summary_path}. Run "
            "train_and_persist_models() first."
        )
    return joblib.load(summary_path)


def models_exist(models_dir: Path = DEFAULT_MODELS_DIR) -> bool:
    models_dir = Path(models_dir)
    return (models_dir / "kmeans_model.pkl").exists() and (
        models_dir / "classifier_model.pkl"
    ).exists()
