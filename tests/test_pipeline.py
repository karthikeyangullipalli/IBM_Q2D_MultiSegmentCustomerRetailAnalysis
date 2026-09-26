"""
test_pipeline.py
------------------
Simple pytest suite covering the pipeline's core contracts:
- data loads without error
- clustering produces exactly 5 clusters
- predict_customer returns a valid persona name and a probability in [0, 1]

Run with:  pytest tests/test_pipeline.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.classifier import predict_batch, predict_customer, train_classifier
from src.clustering import derive_high_value_labels, explain_cluster_assignment, fit_clusters
from src.data_loader import REQUIRED_COLUMNS, load_and_clean_data
from src.persona_rules import (
    PERSONA_ACTIONS,
    generate_business_insights,
    generate_marketing_recommendation,
    is_high_value,
    name_persona,
)
from src.utils import DEFAULT_DATA_PATH, train_and_persist_models

DATA_PATH = str(DEFAULT_DATA_PATH)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def clean_df():
    return load_and_clean_data(DATA_PATH)


@pytest.fixture(scope="module")
def fitted_clusters(clean_df):
    kmeans, cluster_labels, persona_names = fit_clusters(clean_df, n_clusters=5)
    return kmeans, cluster_labels, persona_names


@pytest.fixture(scope="module")
def trained_models(tmp_path_factory, clean_df, fitted_clusters):
    # Train once for the module and reuse across tests that need real models.
    models_dir = tmp_path_factory.mktemp("models")
    summary = train_and_persist_models(data_path=DATA_PATH, models_dir=models_dir)
    return summary, models_dir


# ---------------------------------------------------------------------------
# 1. Data loads without error
# ---------------------------------------------------------------------------

class TestDataLoader:
    def test_loads_without_error(self, clean_df):
        assert clean_df is not None
        assert not clean_df.empty

    def test_expected_shape(self, clean_df):
        # The Mall Customer dataset is 200 rows x 5 columns.
        assert clean_df.shape[0] == 200
        assert clean_df.shape[1] == len(REQUIRED_COLUMNS)

    def test_required_columns_present(self, clean_df):
        for col in REQUIRED_COLUMNS:
            assert col in clean_df.columns

    def test_no_missing_values(self, clean_df):
        assert clean_df.isnull().sum().sum() == 0

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_and_clean_data("data/does_not_exist.csv")

    def test_missing_columns_raises(self, tmp_path):
        bad_csv = tmp_path / "bad.csv"
        pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_csv(bad_csv, index=False)
        with pytest.raises(ValueError):
            load_and_clean_data(str(bad_csv))

    def test_genre_column_alias_is_normalized(self, tmp_path):
        # The real Kaggle distribution of this dataset uses "Genre" (a
        # known mislabeling of "Gender") — must be handled, not assumed away.
        csv_path = tmp_path / "genre.csv"
        pd.DataFrame({
            "CustomerID": [1, 2],
            "Genre": ["Male", "Female"],
            "Age": [25, 30],
            "Annual Income (k$)": [40, 50],
            "Spending Score (1-100)": [60, 70],
        }).to_csv(csv_path, index=False)
        df = load_and_clean_data(str(csv_path))
        assert "Gender" in df.columns
        assert set(df["Gender"]) == {"Male", "Female"}

    def test_duplicate_customer_id_raises(self, tmp_path):
        csv_path = tmp_path / "dup.csv"
        pd.DataFrame({
            "CustomerID": [1, 1],
            "Gender": ["Male", "Female"],
            "Age": [25, 30],
            "Annual Income (k$)": [40, 50],
            "Spending Score (1-100)": [60, 70],
        }).to_csv(csv_path, index=False)
        with pytest.raises(ValueError, match="duplicate CustomerID"):
            load_and_clean_data(str(csv_path))

    def test_unexpected_gender_value_raises(self, tmp_path):
        csv_path = tmp_path / "badgender.csv"
        pd.DataFrame({
            "CustomerID": [1, 2],
            "Gender": ["Male", "Unknown"],
            "Age": [25, 30],
            "Annual Income (k$)": [40, 50],
            "Spending Score (1-100)": [60, 70],
        }).to_csv(csv_path, index=False)
        with pytest.raises(ValueError, match="unexpected Gender"):
            load_and_clean_data(str(csv_path))

    def test_non_numeric_income_raises(self, tmp_path):
        csv_path = tmp_path / "badincome.csv"
        pd.DataFrame({
            "CustomerID": [1, 2],
            "Gender": ["Male", "Female"],
            "Age": [25, 30],
            "Annual Income (k$)": [40, "not-a-number"],
            "Spending Score (1-100)": [60, 70],
        }).to_csv(csv_path, index=False)
        with pytest.raises(ValueError, match="non-numeric"):
            load_and_clean_data(str(csv_path))


# ---------------------------------------------------------------------------
# 2. Clustering produces exactly 5 clusters
# ---------------------------------------------------------------------------

class TestClustering:
    def test_produces_five_clusters(self, fitted_clusters):
        kmeans, cluster_labels, persona_names = fitted_clusters
        assert kmeans.n_clusters == 5
        assert len(set(cluster_labels)) == 5

    def test_every_row_assigned_a_cluster(self, clean_df, fitted_clusters):
        _, cluster_labels, _ = fitted_clusters
        assert len(cluster_labels) == len(clean_df)

    def test_persona_names_cover_every_cluster(self, fitted_clusters):
        kmeans, cluster_labels, persona_names = fitted_clusters
        assert set(persona_names.keys()) == set(cluster_labels)

    def test_persona_names_are_known_personas(self, fitted_clusters):
        _, _, persona_names = fitted_clusters
        for name in persona_names.values():
            assert name in PERSONA_ACTIONS

    def test_silhouette_score_is_reasonable(self, fitted_clusters):
        kmeans, _, _ = fitted_clusters
        # Not a strict correctness bound, just guards against a broken fit
        # (e.g. accidentally clustering on unscaled or constant data).
        assert -1.0 <= kmeans.silhouette_score_ <= 1.0

    def test_derive_high_value_labels_is_binary(self, fitted_clusters):
        kmeans, cluster_labels, _ = fitted_clusters
        labels = derive_high_value_labels(cluster_labels, kmeans)
        assert set(np.unique(labels)).issubset({0, 1})
        assert len(labels) == len(cluster_labels)

    def test_too_few_rows_raises(self):
        tiny_df = pd.DataFrame(
            {"Annual Income (k$)": [10, 20], "Spending Score (1-100)": [30, 40]}
        )
        with pytest.raises(ValueError):
            fit_clusters(tiny_df, n_clusters=5)

    def test_auto_k_selection_not_hardcoded(self, clean_df):
        # No n_clusters passed — must evaluate K=2..10 and select by
        # silhouette score rather than assuming any particular value.
        kmeans, cluster_labels, persona_names = fit_clusters(clean_df)
        k_eval = kmeans.k_evaluation_
        assert set(k_eval["k"]) == set(range(2, 11))
        best_row = k_eval.loc[k_eval["silhouette_score"].idxmax()]
        assert kmeans.n_clusters == int(best_row["k"])
        assert len(set(cluster_labels)) == kmeans.n_clusters

    def test_explicit_k_overrides_auto_selection(self, clean_df):
        kmeans, cluster_labels, _ = fit_clusters(clean_df, n_clusters=3)
        assert kmeans.n_clusters == 3
        assert len(set(cluster_labels)) == 3


# ---------------------------------------------------------------------------
# Persona rules (business logic, tested in isolation from clustering)
# ---------------------------------------------------------------------------

class TestPersonaRules:
    def test_high_income_high_spending_is_high_value(self):
        assert is_high_value(90, 90, median_income=60, median_spending=50) is True

    def test_low_income_low_spending_is_not_high_value(self):
        assert is_high_value(20, 20, median_income=60, median_spending=50) is False

    def test_name_persona_returns_known_name(self):
        name = name_persona(90, 90, income_terciles=[40, 70], spending_terciles=[30, 60])
        assert name in PERSONA_ACTIONS

    def test_marketing_recommendation_is_deterministic(self):
        r1 = generate_marketing_recommendation("Premium Customers", 32, 90, 85, True)
        r2 = generate_marketing_recommendation("Premium Customers", 32, 90, 85, True)
        assert r1 == r2
        assert "Premium Customers" not in r1  # base action text, not a template echo of the name
        assert len(r1) > 0

    def test_business_insights_are_grounded_in_persona_summary(self, fitted_clusters, clean_df):
        kmeans, cluster_labels, persona_names = fitted_clusters
        working = clean_df.copy()
        working["Persona"] = pd.Series(cluster_labels).map(persona_names)
        working["High_Value"] = derive_high_value_labels(cluster_labels, kmeans)
        summary = (
            working.groupby("Persona")
            .agg(count=("Persona", "size"), avg_age=("Age", "mean"),
                 avg_income=("Annual Income (k$)", "mean"),
                 avg_spending=("Spending Score (1-100)", "mean"),
                 pct_high_value=("High_Value", "mean"))
            .reset_index()
        )
        insights = generate_business_insights(summary)
        assert len(insights) > 0
        for insight in insights:
            assert "title" in insight and "detail" in insight
            assert len(insight["detail"]) > 0

    def test_explain_cluster_assignment_grounded_in_model(self, fitted_clusters):
        kmeans, _, _ = fitted_clusters
        explanation = explain_cluster_assignment(income=90, spending=85, kmeans=kmeans)
        assert explanation["assigned_persona"] in PERSONA_ACTIONS
        # The assigned centroid must be at least as close as any other by construction
        assert explanation["distance_to_assigned_centroid"] <= explanation["distance_to_next_closest_centroid"]


# ---------------------------------------------------------------------------
# 3. predict_customer returns a valid persona and a probability in [0, 1]
# ---------------------------------------------------------------------------

class TestClassifier:
    def test_train_classifier_returns_model_and_metrics(self, clean_df, fitted_clusters):
        kmeans, cluster_labels, _ = fitted_clusters
        labels = derive_high_value_labels(cluster_labels, kmeans)
        model, metrics = train_classifier(clean_df, labels)
        assert model is not None
        for key in ("accuracy", "precision", "recall", "f1"):
            assert key in metrics
            assert 0.0 <= metrics[key] <= 1.0

    def test_predict_customer_returns_valid_persona_and_probability(self, trained_models, monkeypatch):
        _, models_dir = trained_models
        monkeypatch.setattr("src.classifier.CLASSIFIER_PATH", models_dir / "classifier_model.pkl")
        monkeypatch.setattr("src.classifier.KMEANS_PATH", models_dir / "kmeans_model.pkl")
        monkeypatch.setattr("src.classifier._model_cache", {})

        result = predict_customer(age=32, gender="Female", income=90, score=85)

        assert result["persona"] in PERSONA_ACTIONS
        assert isinstance(result["high_value"], bool)
        assert 0.0 <= result["probability"] <= 1.0
        assert "explanation" in result
        assert result["explanation"]["assigned_persona"] == result["persona"]

    def test_predict_customer_high_income_high_spending_is_high_value(self, trained_models, monkeypatch):
        _, models_dir = trained_models
        monkeypatch.setattr("src.classifier.CLASSIFIER_PATH", models_dir / "classifier_model.pkl")
        monkeypatch.setattr("src.classifier.KMEANS_PATH", models_dir / "kmeans_model.pkl")
        monkeypatch.setattr("src.classifier._model_cache", {})

        result = predict_customer(age=30, gender="Male", income=137, score=97)
        assert result["high_value"] is True

    def test_predict_batch_appends_expected_columns(self, clean_df, trained_models, monkeypatch):
        _, models_dir = trained_models
        monkeypatch.setattr("src.classifier.CLASSIFIER_PATH", models_dir / "classifier_model.pkl")
        monkeypatch.setattr("src.classifier.KMEANS_PATH", models_dir / "kmeans_model.pkl")
        monkeypatch.setattr("src.classifier._model_cache", {})

        scored = predict_batch(clean_df.head(10))
        for col in ("Predicted_Persona", "High_Value", "High_Value_Probability"):
            assert col in scored.columns
        assert len(scored) == 10
        assert scored["High_Value_Probability"].between(0, 1).all()

    def test_predict_batch_missing_columns_raises(self, trained_models, monkeypatch):
        _, models_dir = trained_models
        monkeypatch.setattr("src.classifier.CLASSIFIER_PATH", models_dir / "classifier_model.pkl")
        monkeypatch.setattr("src.classifier.KMEANS_PATH", models_dir / "kmeans_model.pkl")
        monkeypatch.setattr("src.classifier._model_cache", {})

        with pytest.raises(ValueError):
            predict_batch(pd.DataFrame({"Age": [30]}))

    def test_metrics_include_calibration_info(self, clean_df, fitted_clusters):
        kmeans, cluster_labels, _ = fitted_clusters
        labels = derive_high_value_labels(cluster_labels, kmeans)
        _, metrics = train_classifier(clean_df, labels)
        assert "brier_score" in metrics
        assert 0.0 <= metrics["brier_score"] <= 1.0
        assert metrics["calibration_method"] == "sigmoid"
        assert metrics["calibration_folds"] >= 2

    def test_batch_probabilities_are_not_degenerate(self, clean_df, trained_models, monkeypatch):
        # Regression test for the original bug: raw Random Forest votes on
        # this deterministic label collapsed to ~0%/100% everywhere.
        # Calibration should produce a real spread, including values
        # strictly between the extremes.
        _, models_dir = trained_models
        monkeypatch.setattr("src.classifier.CLASSIFIER_PATH", models_dir / "classifier_model.pkl")
        monkeypatch.setattr("src.classifier.KMEANS_PATH", models_dir / "kmeans_model.pkl")
        monkeypatch.setattr("src.classifier._model_cache", {})

        scored = predict_batch(clean_df)
        probs = scored["High_Value_Probability"]
        assert probs.nunique() > 10, "probabilities collapsed to a handful of degenerate values"
        assert ((probs > 0.05) & (probs < 0.95)).any(), "no non-extreme probabilities found"
