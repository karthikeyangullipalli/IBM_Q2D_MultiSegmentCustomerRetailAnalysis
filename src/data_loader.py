"""
data_loader.py
---------------
Loads and validates the Mall Customer Segmentation dataset. Handles the
real-world column-naming variance in this dataset's actual Kaggle
distributions (e.g. the original file uses "Genre" rather than "Gender"
for the gender column) by normalizing recognized aliases internally,
rather than assuming the CSV headers are already exactly as expected.
The original file on disk is never modified — only the in-memory
DataFrame is normalized.

Service-layer contract:
    load_and_clean_data(path) -> DataFrame
"""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "CustomerID",
    "Gender",
    "Age",
    "Annual Income (k$)",
    "Spending Score (1-100)",
]

# Known real-world header variants seen across public copies of this
# dataset, keyed by normalized (lowercase, no separators) form -> the
# canonical column name this project uses internally. "genre" is not a
# typo on our part — it's the actual header in the original Kaggle CSV
# (a known mislabeling of "Gender" in that file).
COLUMN_ALIASES = {
    "customerid": "CustomerID",
    "customer_id": "CustomerID",
    "id": "CustomerID",
    "genre": "Gender",
    "gender": "Gender",
    "sex": "Gender",
    "age": "Age",
    "annualincomek": "Annual Income (k$)",
    "annualincome": "Annual Income (k$)",
    "income": "Annual Income (k$)",
    "spendingscore1100": "Spending Score (1-100)",
    "spendingscore": "Spending Score (1-100)",
    "spending_score": "Spending Score (1-100)",
}


def _normalize_key(col: str) -> str:
    return "".join(ch for ch in str(col).lower() if ch.isalnum())


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map recognized column-name variants (case, separators, known aliases
    like Genre->Gender) onto this project's canonical names, without
    guessing at columns that aren't recognized at all.
    """
    rename_map = {}
    for col in df.columns:
        key = _normalize_key(col)
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
    return df.rename(columns=rename_map)


def load_and_clean_data(path: str) -> pd.DataFrame:
    """
    Load the Mall Customer dataset from `path`, normalize known column
    name variants, validate shape/columns/values, standardize dtypes,
    and return a clean DataFrame ready for clustering.

    Args:
        path: Path to the Mall Customer Segmentation CSV file.

    Returns:
        A cleaned pandas DataFrame with the required columns.

    Raises:
        FileNotFoundError: if `path` does not exist.
        ValueError: if the file is empty, missing required columns
            (after normalization), contains duplicate CustomerIDs, or
            still contains missing/invalid values after cleaning.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("Dataset is empty.")

    df = _normalize_columns(df)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Dataset is missing required columns: {missing_cols}. "
            f"Columns found in file: {list(df.columns)}"
        )

    # Keep only the columns we need, in a consistent order
    df = df[REQUIRED_COLUMNS].copy()

    # Duplicate CustomerIDs indicate a data integrity problem even if the
    # rows aren't byte-identical — flag this rather than silently keeping
    # both, since it would double-count a customer in every downstream KPI.
    dup_ids = df["CustomerID"][df["CustomerID"].duplicated(keep=False)]
    if not dup_ids.empty:
        raise ValueError(
            f"Dataset contains duplicate CustomerID values: "
            f"{sorted(dup_ids.unique().tolist())}"
        )

    # Drop exact duplicate rows, if any
    df = df.drop_duplicates().reset_index(drop=True)

    # Standardize dtypes — surface a clear error rather than letting a
    # non-numeric value silently become NaN.
    for col in ["Age", "Annual Income (k$)", "Spending Score (1-100)"]:
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.isnull().any() and not df[col].isnull().any():
            raise ValueError(f"Column '{col}' contains non-numeric values.")
        df[col] = coerced

    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Age"] = df["Age"].astype(int)
    df["Annual Income (k$)"] = df["Annual Income (k$)"].astype(float)
    df["Spending Score (1-100)"] = df["Spending Score (1-100)"].astype(float)

    df["Gender"] = df["Gender"].astype(str).str.strip().str.title()
    unexpected_genders = set(df["Gender"].unique()) - {"Male", "Female"}
    if unexpected_genders:
        raise ValueError(
            f"Dataset contains unexpected Gender values: {sorted(unexpected_genders)}. "
            "Expected only 'Male' or 'Female'."
        )

    # Fail loudly (not silently) if anything required is still missing
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    if null_counts.any():
        raise ValueError(
            f"Dataset contains missing values after cleaning:\n{null_counts[null_counts > 0]}"
        )

    # Sanity-check value ranges rather than trusting the source blindly
    if not df["Age"].between(0, 120).all():
        raise ValueError("Dataset contains implausible Age values (expected 0-120).")
    if not df["Annual Income (k$)"].ge(0).all():
        raise ValueError("Dataset contains negative Annual Income values.")
    if not df["Spending Score (1-100)"].between(0, 100).all():
        raise ValueError("Dataset contains Spending Score values outside the expected 0-100 range.")

    return df
