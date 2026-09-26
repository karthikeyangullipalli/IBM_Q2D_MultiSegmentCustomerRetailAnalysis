"""
evaluation.py
-------------
Computes and exports comprehensive, reproducible machine-readable evaluation
metrics for the Retail Customer Intelligence pipeline. Produces both
results/final_metrics.json and results/final_metrics.csv directly from the
trained models and ground-truth data.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from src.classifier import FEATURE_COLUMNS, _prepare_features
from src.clustering import CLUSTER_FEATURES, derive_high_value_labels
from src.data_loader import load_and_clean_data
from src.utils import (
    DEFAULT_DATA_PATH,
    DEFAULT_MODELS_DIR,
    load_training_summary,
    models_exist,
    train_and_persist_models,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


class NpEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy datatypes."""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def run_comprehensive_evaluation(
    data_path: Path = DEFAULT_DATA_PATH,
    models_dir: Path = DEFAULT_MODELS_DIR,
    results_dir: Path = RESULTS_DIR,
) -> Dict[str, Any]:
    """
    Run full model evaluation, gathering clustering quality metrics,
    supervised classification performance, confusion matrix, calibration
    loss, and persona cohort statistics, and write machine-readable artifacts.
    """
    results_dir.mkdir(parents=True, exist_ok=True)

    if not models_exist(models_dir):
        summary = train_and_persist_models(data_path, models_dir)
    else:
        summary = load_training_summary(models_dir)

    import joblib

    classifier_model = joblib.load(models_dir / "classifier_model.pkl")
    kmeans_model = joblib.load(models_dir / "kmeans_model.pkl")

    df = load_and_clean_data(str(data_path))
    X = _prepare_features(df)
    high_value_labels = derive_high_value_labels(kmeans_model.labels_, kmeans_model)
    y = np.asarray(high_value_labels).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    y_pred = classifier_model.predict(X_test)
    y_proba = classifier_model.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred).tolist()
    clf_report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    roc_auc = float(roc_auc_score(y_test, y_proba))

    feature_importances = dict(
        zip(FEATURE_COLUMNS, [float(fi) for fi in classifier_model.feature_importances_])
    )

    k_eval_df = summary["k_evaluation"]
    if isinstance(k_eval_df, pd.DataFrame):
        k_eval_records = k_eval_df.to_dict(orient="records")
    else:
        k_eval_records = k_eval_df

    persona_df = summary["persona_summary"]
    if isinstance(persona_df, pd.DataFrame):
        persona_records = persona_df.to_dict(orient="records")
    else:
        persona_records = persona_df

    metrics_payload = {
        "dataset_metadata": {
            "dataset_name": "Mall Customer Segmentation Dataset",
            "total_records": len(df),
            "total_features": len(df.columns),
            "missing_values": int(df.isnull().sum().sum()),
            "clustering_features": CLUSTER_FEATURES,
            "classifier_features": FEATURE_COLUMNS,
            "spending_metric_note": "The dataset contains Spending Score (1-100), an assigned behavioral index, not monetary currency amounts.",
        },
        "clustering_metrics": {
            "optimal_k": int(kmeans_model.n_clusters),
            "selection_method": "Silhouette Score Maximization (K=2..10)",
            "peak_silhouette_score": float(kmeans_model.silhouette_score_),
            "inertia_at_k5": float(kmeans_model.inertia_),
            "k_evaluation_table": k_eval_records,
        },
        "classifier_metrics": {
            "algorithm": "RandomForestClassifier with CalibratedClassifierCV (Platt scaling)",
            "n_estimators": 200,
            "calibration_method": "sigmoid",
            "calibration_folds": 5,
            "train_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": roc_auc,
            "brier_score_loss": float(brier_score_loss(y_test, y_proba)),
            "confusion_matrix": {
                "true_negative": cm[0][0],
                "false_positive": cm[0][1],
                "false_negative": cm[1][0],
                "true_positive": cm[1][1],
            },
            "classification_report": clf_report,
            "feature_importances": feature_importances,
            "academic_honesty_note": (
                "The classifier learns the deterministic decision boundary induced by the income "
                "and spending thresholds used to define the High-Value cohort. Sigmoid calibration "
                "transforms raw classifier scores into probability estimates intended to be better calibrated."
            ),
        },
        "business_cohort_metrics": {
            "high_value_customer_count": int(summary["high_value_count"]),
            "high_value_percentage_of_base": float(summary["high_value_pct"]),
            "high_value_share_of_aggregate_spending_score": float(
                summary["high_value_stats"]["share_of_total_spending"]
            ),
            "high_value_share_of_total_income": float(
                summary["high_value_stats"]["share_of_total_income"]
            ),
            "high_value_average_income_k": float(summary["high_value_stats"]["avg_income"]),
            "high_value_average_spending_score": float(summary["high_value_stats"]["avg_spending"]),
            "high_value_average_age": float(summary["high_value_stats"]["avg_age"]),
            "persona_summary": persona_records,
        },
    }

    # Save JSON
    json_path = results_dir / "final_metrics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4, cls=NpEncoder)

    # Save Summary CSV
    summary_rows = [
        {"Category": "Dataset", "Metric": "Total Customers", "Value": len(df)},
        {"Category": "Clustering", "Metric": "Optimal Clusters (K)", "Value": kmeans_model.n_clusters},
        {"Category": "Clustering", "Metric": "Silhouette Score", "Value": round(kmeans_model.silhouette_score_, 4)},
        {"Category": "Clustering", "Metric": "Inertia (K=5)", "Value": round(kmeans_model.inertia_, 2)},
        {"Category": "Classification", "Metric": "Test Accuracy", "Value": round(accuracy_score(y_test, y_pred), 4)},
        {"Category": "Classification", "Metric": "Test Precision", "Value": round(precision_score(y_test, y_pred), 4)},
        {"Category": "Classification", "Metric": "Test Recall", "Value": round(recall_score(y_test, y_pred), 4)},
        {"Category": "Classification", "Metric": "Test F1-Score", "Value": round(f1_score(y_test, y_pred), 4)},
        {"Category": "Classification", "Metric": "ROC-AUC Score", "Value": round(roc_auc, 4)},
        {"Category": "Classification", "Metric": "Brier Score Loss", "Value": round(brier_score_loss(y_test, y_proba), 6)},
        {"Category": "Business Cohort", "Metric": "High-Value Customers", "Value": int(summary["high_value_count"])},
        {"Category": "Business Cohort", "Metric": "High-Value Base %", "Value": f"{summary['high_value_pct']*100:.1f}%"},
        {"Category": "Business Cohort", "Metric": "Aggregate Spending Score Share %", "Value": f"{summary['high_value_stats']['share_of_total_spending']*100:.1f}%"},
    ]
    csv_path = results_dir / "final_metrics.csv"
    pd.DataFrame(summary_rows).to_csv(csv_path, index=False)

    return metrics_payload


if __name__ == "__main__":
    metrics = run_comprehensive_evaluation()
    print("Successfully generated final metrics:")
    print(f"- results/final_metrics.json")
    print(f"- results/final_metrics.csv")
    print(f"Accuracy: {metrics['classifier_metrics']['accuracy'] * 100:.1f}%")
    print(f"Brier Score: {metrics['classifier_metrics']['brier_score_loss']:.6f}")
    print(f"Silhouette Score: {metrics['clustering_metrics']['peak_silhouette_score']:.4f}")
