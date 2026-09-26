"""
clustering.py
--------------
Unsupervised segmentation: fits K-Means, names each resulting cluster as
a persona from its actual centroid characteristics, and flags which
clusters count as "High-Value". The number of clusters is not assumed —
see select_optimal_k() below — and the clustering feature set was chosen
by evidence, not convention (see CLUSTER_FEATURES note).

Service-layer contract:
    fit_clusters(df) -> (kmeans_model, cluster_labels, persona_names)

Note: to keep that 3-tuple contract exact while still giving the rest of
the app (persistence, the Predict page, the Insights page) everything it
needs, extra metadata (the fitted scaler, persona map, high-value cluster
set, centroid stats, K-selection table, silhouette score) is attached as
attributes directly on the returned `kmeans` object. joblib persists
these attributes along with the model, so a single saved file is a
self-contained bundle.
"""

from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.persona_rules import is_high_value, name_persona

# Clustering feature set: Annual Income + Spending Score.
#
# This was not assumed — it was chosen by empirically comparing silhouette
# scores across candidate feature sets on this exact dataset:
#   Income + Spending only:              best silhouette 0.555 (k=5)
#   Age + Income + Spending:              best silhouette 0.428 (k=6)
#   Age + Income + Spending + Gender:     best silhouette 0.421 (k=10, and
#                                          not a business-interpretable
#                                          cluster count)
# Adding Age or Gender measurably *dilutes* cluster separation on this
# dataset rather than improving it, so the 2D Income/Spending view is the
# defensible choice, not a leftover assumption. Age and Gender are still
# used downstream, just as classifier features (see classifier.py) and as
# descriptive stats per persona, rather than as clustering inputs.
CLUSTER_FEATURES = ["Annual Income (k$)", "Spending Score (1-100)"]

DEFAULT_K_RANGE = range(2, 11)


def evaluate_k_range(
    df: pd.DataFrame,
    k_range: Iterable[int] = DEFAULT_K_RANGE,
    features: Iterable[str] = CLUSTER_FEATURES,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Fit K-Means for every K in k_range on the given (scaled) features and
    record inertia + silhouette score for each — the evidence used to
    select the final cluster count, rather than assuming one.

    Returns a DataFrame with columns: k, inertia, silhouette_score.
    """
    features = list(features)
    X = df[features]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(X)

    rows = []
    for k in k_range:
        if k < 2 or k > len(df) - 1:
            continue
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(scaled)
        sil = silhouette_score(scaled, labels)
        rows.append({"k": int(k), "inertia": float(km.inertia_), "silhouette_score": float(sil)})

    return pd.DataFrame(rows)


def select_optimal_k(k_eval: pd.DataFrame) -> int:
    """
    Select the final cluster count by maximizing silhouette score across
    the evaluated range. Silhouette score is used as the sole criterion
    (rather than also eyeballing the inertia "elbow") because it has a
    single well-defined maximum, while an elbow point is a subjective
    visual judgment — a maximized silhouette score is a reproducible,
    defensible rule rather than a hardcoded cluster count.
    """
    if k_eval.empty:
        raise ValueError("k_eval is empty; nothing to select from.")
    return int(k_eval.loc[k_eval["silhouette_score"].idxmax(), "k"])


def fit_clusters(
    df: pd.DataFrame,
    n_clusters: Optional[int] = None,
    k_range: Iterable[int] = DEFAULT_K_RANGE,
    random_state: int = 42,
) -> Tuple[KMeans, np.ndarray, Dict[int, str]]:
    """
    Fit K-Means on Annual Income + Spending Score, name each cluster as a
    persona, and flag which clusters count as "High-Value".

    Args:
        df: cleaned customer DataFrame (from load_and_clean_data).
        n_clusters: number of K-Means clusters. If None (the default),
            the cluster count is selected automatically by
            select_optimal_k() over evaluate_k_range(df, k_range) —
            it is not assumed to be any particular value.
        k_range: K values to evaluate when n_clusters is None.
        random_state: seed for reproducibility.

    Returns:
        kmeans: fitted KMeans model, with extra attributes attached:
            .scaler_, .persona_names_, .high_value_clusters_,
            .centroid_stats_, .silhouette_score_, .k_evaluation_
        cluster_labels: np.ndarray of cluster IDs, one per row in `df`.
        persona_names: dict mapping cluster ID -> persona name.
    """
    k_eval = evaluate_k_range(df, k_range=k_range, random_state=random_state)

    if n_clusters is None:
        n_clusters = select_optimal_k(k_eval)

    if len(df) < n_clusters:
        raise ValueError(
            f"Need at least {n_clusters} rows to form {n_clusters} clusters; "
            f"got {len(df)}."
        )

    features = df[CLUSTER_FEATURES]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled)

    working = df.copy()
    working["Cluster"] = cluster_labels
    centroid_stats = working.groupby("Cluster")[CLUSTER_FEATURES].agg(
        ["mean", "count"]
    )

    median_income = df["Annual Income (k$)"].median()
    median_spending = df["Spending Score (1-100)"].median()
    income_terciles = df["Annual Income (k$)"].quantile([1 / 3, 2 / 3]).tolist()
    spending_terciles = df["Spending Score (1-100)"].quantile([1 / 3, 2 / 3]).tolist()

    persona_names: Dict[int, str] = {}
    high_value_clusters = set()
    for cluster_id in sorted(working["Cluster"].unique()):
        avg_income = centroid_stats.loc[cluster_id, ("Annual Income (k$)", "mean")]
        avg_spending = centroid_stats.loc[
            cluster_id, ("Spending Score (1-100)", "mean")
        ]
        cluster_id = int(cluster_id)
        persona_names[cluster_id] = name_persona(
            avg_income, avg_spending, income_terciles, spending_terciles
        )
        if is_high_value(avg_income, avg_spending, median_income, median_spending):
            high_value_clusters.add(cluster_id)

    sil_score = silhouette_score(scaled, cluster_labels)

    kmeans.scaler_ = scaler
    kmeans.persona_names_ = persona_names
    kmeans.high_value_clusters_ = high_value_clusters
    kmeans.centroid_stats_ = centroid_stats
    kmeans.silhouette_score_ = float(sil_score)
    kmeans.cluster_features_ = CLUSTER_FEATURES
    kmeans.k_evaluation_ = k_eval
    kmeans.dataset_stats_ = {
        "avg_age": float(df["Age"].mean()),
        "avg_income": float(df["Annual Income (k$)"].mean()),
        "avg_spending": float(df["Spending Score (1-100)"].mean()),
    }

    return kmeans, cluster_labels, persona_names


def explain_cluster_assignment(income: float, spending: float, kmeans: KMeans) -> Dict[str, object]:
    """
    Ground the persona assignment in actual model output rather than an
    invented narrative: distance (in standardized units) from the input
    point to every cluster centroid, which cluster is closest vs.
    next-closest, and how the input compares numerically to its assigned
    persona's own average income/spending. Every number here comes
    directly from the fitted KMeans model and the training data's
    centroid statistics.
    """
    point = pd.DataFrame([{
        "Annual Income (k$)": income,
        "Spending Score (1-100)": spending,
    }])[kmeans.cluster_features_]
    scaled_point = kmeans.scaler_.transform(point)

    distances = kmeans.transform(scaled_point)[0]
    order = np.argsort(distances)
    assigned_cluster = int(order[0])
    next_closest_cluster = int(order[1]) if len(order) > 1 else None

    persona_income_avg = float(kmeans.centroid_stats_.loc[assigned_cluster, ("Annual Income (k$)", "mean")])
    persona_spending_avg = float(kmeans.centroid_stats_.loc[assigned_cluster, ("Spending Score (1-100)", "mean")])

    return {
        "assigned_cluster": assigned_cluster,
        "assigned_persona": kmeans.persona_names_[assigned_cluster],
        "distance_to_assigned_centroid": float(distances[assigned_cluster]),
        "next_closest_cluster": next_closest_cluster,
        "next_closest_persona": kmeans.persona_names_.get(next_closest_cluster) if next_closest_cluster is not None else None,
        "distance_to_next_closest_centroid": float(distances[next_closest_cluster]) if next_closest_cluster is not None else None,
        "persona_avg_income": persona_income_avg,
        "persona_avg_spending": persona_spending_avg,
        "income_vs_persona_avg": float(income - persona_income_avg),
        "spending_vs_persona_avg": float(spending - persona_spending_avg),
        "income_vs_dataset_avg": float(income - kmeans.dataset_stats_["avg_income"]),
        "spending_vs_dataset_avg": float(spending - kmeans.dataset_stats_["avg_spending"]),
    }


def derive_high_value_labels(cluster_labels: np.ndarray, kmeans: KMeans) -> np.ndarray:
    """
    Map each row's cluster ID to the binary High-Value target using the
    high_value_clusters_ set computed during fit_clusters. This is the
    array that gets passed to classifier.train_classifier() as `labels`.
    """
    return np.array(
        [1 if c in kmeans.high_value_clusters_ else 0 for c in cluster_labels]
    )
