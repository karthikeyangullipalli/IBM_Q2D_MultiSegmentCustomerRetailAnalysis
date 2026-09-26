"""
classifier.py
--------------
Supervised High-Value prediction: trains a Random Forest to predict the
cluster-derived High-Value label directly from Age, Gender, Annual Income,
and Spending Score, so new customers can be scored without re-running
K-Means. Random Forest remains the core classifier, but its raw votes are
wrapped in CalibratedClassifierCV (sigmoid/Platt scaling) so the reported
probability is a genuine calibrated likelihood rather than an extreme
"fraction of trees that agreed" score. Also owns the single-customer and
batch prediction entry points used by the Streamlit pages, which lazily
load the saved model bundle from models/ on first use.

Why calibration is needed here: the High-Value label is a deterministic
function of Income + Spending Score (see persona_rules.is_high_value).
Random Forest's default predict_proba is just the fraction of trees that
voted for the positive class — with a deterministic, cleanly-separable
label, nearly every tree agrees on nearly every point, so raw RF
probabilities collapse to ~0% or ~100% almost everywhere. That's not
wrong, but it isn't informative either: it can't distinguish "this
customer is unambiguously mid-tier" from "this customer is a genuine
borderline case." CalibratedClassifierCV fixes this by holding out folds
of the training data, fitting a secondary 1-D logistic regression (Platt
scaling) that maps the Random Forest's raw scores to probabilities that
actually match observed outcome frequencies, then averaging that mapping
across folds. The result still comes from the same Random Forest votes —
calibration only rescales how those votes are translated into a
probability, it never touches predictions or the High-Value business
rule itself.

Service-layer contract (unchanged):
    train_classifier(df, labels) -> (model, metrics_dict)
    predict_customer(age, gender, income, score) -> {persona, high_value, probability}
    predict_batch(df) -> DataFrame with prediction columns appended
"""

from pathlib import Path
from typing import Dict, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = ["Age", "Gender", "Annual Income (k$)", "Spending Score (1-100)"]
GENDER_MAP = {"Male": 0, "Female": 1}

# Calibration settings. 'sigmoid' (Platt scaling) is used rather than
# 'isotonic' because our per-fold calibration sample is small (~30 rows
# per fold at this dataset size), and isotonic regression needs more data
# than that to avoid overfitting the calibration curve itself.
CALIBRATION_METHOD = "sigmoid"
CALIBRATION_FOLDS = 5

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
CLASSIFIER_PATH = MODELS_DIR / "classifier_model.pkl"
KMEANS_PATH = MODELS_DIR / "kmeans_model.pkl"

_model_cache: Dict[str, object] = {}


def _encode_gender(series: pd.Series) -> pd.Series:
    return series.map(GENDER_MAP).fillna(0).astype(int)


def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    encoded = df.copy()
    encoded["Gender"] = _encode_gender(encoded["Gender"])
    return encoded[FEATURE_COLUMNS]


def _aggregate_feature_importances(calibrated_model: CalibratedClassifierCV) -> np.ndarray:
    """
    CalibratedClassifierCV doesn't expose .feature_importances_ directly
    since it's an ensemble of per-fold calibrated estimators. Average the
    underlying Random Forest's importances across those folds so the
    Insights/report tooling that reads .feature_importances_ keeps working.
    """
    importances = [
        cc.estimator.feature_importances_
        for cc in calibrated_model.calibrated_classifiers_
    ]
    return np.mean(importances, axis=0)


def train_classifier(
    df: pd.DataFrame,
    labels: Union[np.ndarray, pd.Series],
    random_state: int = 42,
) -> Tuple[CalibratedClassifierCV, Dict[str, float]]:
    """
    Train a Random Forest on Age/Gender/Income/Spending to predict the
    binary High-Value label, wrap it in CalibratedClassifierCV so its
    predict_proba output is a genuine calibrated probability rather than
    a raw tree-vote fraction, and return evaluation metrics.

    Random Forest is still the classifier making every decision; the
    calibration wrapper only rescales how confidence is reported. The
    High-Value label itself (labels arg) is untouched — it still comes
    from clustering.derive_high_value_labels(), which applies
    persona_rules.is_high_value() and is not affected by this function.

    Args:
        df: cleaned customer DataFrame (from load_and_clean_data).
        labels: binary High-Value target aligned row-for-row with `df`
            (0/1 or True/False) — typically clustering.derive_high_value_labels().
    """
    X = _prepare_features(df)
    y = np.asarray(labels).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    base_rf = RandomForestClassifier(n_estimators=200, random_state=random_state)
    model = CalibratedClassifierCV(
        estimator=base_rf,
        method=CALIBRATION_METHOD,
        cv=CALIBRATION_FOLDS,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "brier_score": float(brier_score_loss(y_test, y_proba)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positive_rate": float(y.mean()),
        "calibration_method": CALIBRATION_METHOD,
        "calibration_folds": CALIBRATION_FOLDS,
    }

    # Keep inference metadata attached to the model so it's one self
    # contained artifact once saved with joblib.
    model.feature_columns_ = FEATURE_COLUMNS
    model.gender_map_ = GENDER_MAP
    model.feature_importances_ = _aggregate_feature_importances(model)

    return model, metrics


def _load_models():
    """Lazily load and cache the saved model bundles from models/."""
    if "classifier" not in _model_cache:
        if not CLASSIFIER_PATH.exists():
            raise FileNotFoundError(
                f"No trained classifier found at {CLASSIFIER_PATH}. "
                "Run the training pipeline first (see src/utils.py "
                "train_and_persist_models())."
            )
        _model_cache["classifier"] = joblib.load(CLASSIFIER_PATH)
    if "kmeans" not in _model_cache:
        if not KMEANS_PATH.exists():
            raise FileNotFoundError(
                f"No trained K-Means bundle found at {KMEANS_PATH}. "
                "Run the training pipeline first (see src/utils.py "
                "train_and_persist_models())."
            )
        _model_cache["kmeans"] = joblib.load(KMEANS_PATH)
    return _model_cache["classifier"], _model_cache["kmeans"]


def predict_customer(age: int, gender: str, income: float, score: float) -> Dict[str, object]:
    """
    Score a single new customer: predicted persona (via the saved K-Means
    bundle), High-Value flag + calibrated probability (via the saved,
    calibrated Random Forest), and a data-grounded explanation of the
    persona assignment (see clustering.explain_cluster_assignment).
    `probability` is a calibrated likelihood — see the module docstring
    for why that differs from a raw RF vote fraction — not a guarantee of
    real-world revenue behavior.
    """
    from src.clustering import explain_cluster_assignment  # local import avoids a circular import at module load

    classifier_model, kmeans = _load_models()

    row = pd.DataFrame(
        [
            {
                "Age": age,
                "Gender": gender,
                "Annual Income (k$)": income,
                "Spending Score (1-100)": score,
            }
        ]
    )

    X = _prepare_features(row)
    high_value = bool(classifier_model.predict(X)[0])
    probability = float(classifier_model.predict_proba(X)[0][1])

    scaled_point = kmeans.scaler_.transform(row[kmeans.cluster_features_])
    cluster_id = int(kmeans.predict(scaled_point)[0])
    persona = kmeans.persona_names_[cluster_id]

    explanation = explain_cluster_assignment(income, score, kmeans)
    explanation["age_vs_dataset_avg"] = float(age - kmeans.dataset_stats_["avg_age"])

    return {
        "persona": persona,
        "high_value": high_value,
        "probability": probability,
        "cluster_id": cluster_id,
        "explanation": explanation,
    }


def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score every row of `df` and append prediction columns. High_Value is
    the predicted class (thresholded at 0.5 on the calibrated
    probability); High_Value_Probability is that calibrated probability
    itself, not a raw Random Forest vote fraction.
    """
    classifier_model, kmeans = _load_models()

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Batch input is missing required columns: {missing}")

    X = _prepare_features(df)
    high_value_preds = classifier_model.predict(X).astype(bool)
    probabilities = classifier_model.predict_proba(X)[:, 1]

    scaled_points = kmeans.scaler_.transform(df[kmeans.cluster_features_])
    cluster_ids = kmeans.predict(scaled_points)
    personas = [kmeans.persona_names_[int(c)] for c in cluster_ids]

    result = df.copy()
    result["Predicted_Persona"] = personas
    result["High_Value"] = high_value_preds
    result["High_Value_Probability"] = probabilities
    return result
