# PROJECT AUDIT: Retail Customer Intelligence

**Author**: Gullipalli Lakshmi Narayana Karthikeyan (Roll: A24126510017)  
**Program**: Artificial Intelligence & Machine Learning — UG Level 2  
**Institution**: ANIL Neerukonda Institute of Technology and Sciences (ANITS)  
**IBM Track**: IBM SkillsBuild Internship Program / IBMQ2D (IBM ID: IBMP3155)  
**Date of Audit**: September 26, 2026  
**Auditor**: Antigravity Autonomous Pair Programmer  

---

## 1. Executive Summary & Objective

This internal audit document establishes the definitive ground-truth state of the **Retail Customer Intelligence** codebase. It resolves prior conflicts between divergent draft designs ("Version A" vs. "Version B"), records executable verification data, catalogues reproducible machine learning metrics, audits codebase structure and tests, and highlights components requiring standardization and packaging for the final internship submission.

---

## 2. Definitive Architecture & System Design

### 2.1 Final Selected Version
* **Standardized Version**: **Version A** (Multi-page Streamlit application, Calibrated Random Forest, evidence-based K-Means, 32-test automated test suite).
* **Discarded Artifacts**: References to "Version B" (Static HTML/CSS/JS, Chart.js, Vercel, 75/25 split, 100 trees, 82% accuracy) have been identified as outdated legacy concepts and are formally excluded from this project.

### 2.2 Technology Stack
* **Language & Runtime**: Python 3.12.3 (CPython on Windows 11 64-bit).
* **Data Manipulation**: `pandas` (>=2.0.0), `numpy` (>=1.26.0).
* **Machine Learning**: `scikit-learn` (>=1.3.0) — `KMeans`, `StandardScaler`, `silhouette_score`, `RandomForestClassifier`, `CalibratedClassifierCV`, `brier_score_loss`.
* **Model Serialization**: `joblib` (>=1.3.0) — persister for fitted models and pipeline summary dictionaries.
* **Interactive Frontend**: `streamlit` (>=1.32.0) with custom HTML/CSS theming.
* **Visualization Engine**: `plotly` (>=5.18.0) — interactive 2D scatter plots, centroids, and bar graphs.
* **Testing & Quality Assurance**: `pytest` (>=7.4.0) with 32 unit and integration tests.
* **Deployment Target**: Streamlit local web server (`http://localhost:8501`).

---

## 3. Dataset Audit

* **Source File**: `data/mall_customers.csv` (Kaggle Mall Customer Segmentation Dataset).
* **Row Count**: 200 records.
* **Columns in File**: `CustomerID`, `Genre`, `Age`, `Annual Income (k$)`, `Spending Score (1-100)`.
* **Data Integrity Checks**:
  * Missing values: 0 across all fields.
  * Duplicate CustomerIDs: 0.
  * Exact row duplicates: 0.
  * Range integrity: Age [18, 70], Income [$15k, $137k], Spending Score [1, 99]. All strictly within permissible bounds.
* **Column Normalization**: Kaggle's historical typo `Genre` is dynamically mapped to `Gender` in memory via `src/data_loader.py` without mutating the disk file.

---

## 4. Machine Learning Pipeline Audit

### 4.1 Feature Selection & Justification
* **Clustering Features**: `Annual Income (k$)` and `Spending Score (1-100)`.
  * *Empirical Justification*: Evaluated silhouette score across candidate sets:
    * Income + Spending: **0.5547** ($K=5$)
    * Age + Income + Spending: **0.4281** ($K=6$)
    * Age + Income + Spending + Gender: **0.4210** ($K=10$, non-actionable)
  * Adding Age or Gender dilutes cluster density and degrades separability. Hence, 2D Income/Spending clustering is empirically superior. Age and Gender are preserved for supervised scoring and demographic profiling.
* **Feature Scaling**: `StandardScaler()` applied prior to Euclidean distance calculations in K-Means.

### 4.2 K-Means Clustering & Optimal $K$ Selection
* **Evaluation Range**: $K \in [2, 10]$ evaluated by Inertia and Silhouette Score (`random_state=42`, `n_init=10`).
* **Reproducible Evaluation Curve**:
  * $K=2$: Inertia = 269.69, Silhouette = 0.3213
  * $K=3$: Inertia = 157.70, Silhouette = 0.4666
  * $K=4$: Inertia = 108.92, Silhouette = 0.4939
  * **$K=5$ (Optimal)**: Inertia = 65.57, Silhouette = **0.5547** (Global maximum)
  * $K=6$: Inertia = 55.06, Silhouette = 0.5399
  * $K=7$: Inertia = 44.86, Silhouette = 0.5281
  * $K=8$: Inertia = 37.23, Silhouette = 0.4552
  * $K=9$: Inertia = 32.39, Silhouette = 0.4571
  * $K=10$: Inertia = 29.98, Silhouette = 0.4432
* **Optimal Selection Rule**: The algorithm programmatically chooses $K=5$ via silhouette score maximization (`select_optimal_k`), rather than arbitrarily hardcoding $K$.

### 4.3 Persona Formation Logic
Dataset tercile thresholds on Annual Income and Spending Score categorize cluster centroids:
1. **Premium Customers** ($n=39$, $19.5\%$): High Income ($86.54k), High Spending ($82.13).
2. **Careful Spenders** ($n=35$, $17.5\%$): High Income ($88.29k), Low Spending ($17.11).
3. **Standard Customers** ($n=81$, $40.5\%$): Mid Income ($55.30k), Mid Spending ($49.52).
4. **Impulsive Shoppers** ($n=22$, $11.0\%$): Low Income ($25.73k), High Spending ($79.36).
5. **Budget Customers** ($n=23$, $11.5\%$): Low Income ($26.30k), Low Spending ($20.91).

### 4.4 High-Value Customer Definition
* **Rule**: A customer cluster is classified as "High-Value" if and only if its centroid satisfies:
  $$\text{Centroid Income} \ge \text{Median Income } (\$61.5\text{k}) \quad \text{AND} \quad \text{Centroid Spending} \ge \text{Median Spending } (50.0)$$
* **Outcome**: Exactly one cluster meets this criterion: **Premium Customers**.
* **Cohort Metrics**: 39 customers (19.5% of total base) who account for **31.90%** of total mall spending.

### 4.5 Supervised Classifier & Calibration
* **Model**: `RandomForestClassifier(n_estimators=200, random_state=42)` wrapped in `CalibratedClassifierCV(estimator=base_rf, method='sigmoid', cv=5)`.
* **Input Features**: `Age`, `Gender` (Male=0, Female=1), `Annual Income (k$)`, `Spending Score (1-100)`.
* **Split**: 80% train ($n=160$), 20% test ($n=40$), stratified by target $y$ (`random_state=42`).
* **Calibrated Test Metrics**:
  * Accuracy: **1.0000 (100.0%)**
  * Precision: **1.0000 (100.0%)**
  * Recall: **1.0000 (100.0%)**
  * F1-Score: **1.0000 (100.0%)**
  * Brier Score Loss: **0.00358 (~0.0036)**
* **Academic Honesty on 100% Metric**:
  The 100% accuracy on the test set is NOT an indicator of general real-world omniscient prediction. It occurs because the High-Value ground truth label was derived deterministically from Annual Income and Spending Score, and those identical features are directly accessible to the Random Forest. The classifier perfectly learns the cluster boundary hyperplane. Calibrated probability scaling (Platt scaling) was specifically incorporated to convert raw binary tree votes into informative, smooth risk probabilities.

---

## 5. Application Pages & Frontend Audit

The application is structured into five distinct Streamlit pages:
1. `app.py`: System overview, key dataset KPIs (Total Customers, Segments, High-Value count, Silhouette Score), and page directory.
2. `pages/1_Dashboard.py`: Interactive Plotly 2D scatter plot with persona colors, centroid crosshairs, and KPI cards showing count, spending share, and strategy.
3. `pages/2_Predict.py`: Real-time interactive scoring form taking Age, Gender, Income, and Spending Score, outputting predicted persona, High-Value badge, calibrated probability, centroid distance breakdown, and marketing recommendation.
4. `pages/3_Insights.py`: Empirical cluster selection graphs (Elbow Curve & Silhouette Plot), persona metric comparisons, classifier feature importance chart, and automated business insights.
5. `pages/4_Data_Explorer.py`: Multi-column filtering by persona, gender, age range, income range, spending score range, and high-value status, with one-click CSV export.

---

## 6. Automated Test Suite Audit

* **Test Runner**: `pytest`
* **Test File**: `tests/test_pipeline.py`
* **Total Executed Tests**: **32 tests**
* **Result**: **32 passed, 0 failed, 0 skipped** (Execution time: ~50.6 seconds).
* **Coverage Categories**:
  * Data Loading & Schema: Aliases (`Genre` -> `Gender`), missing columns, invalid ranges, duplicate IDs, non-numeric values.
  * Clustering: $K$-range evaluation, silhouette score calculation, optimal $K$ selection, centroid assignment.
  * Business Logic: Tercile bucketing, persona naming, High-Value median threshold rule, marketing action generation.
  * Classifier: 80/20 train/test split, CalibratedClassifierCV fitting, Platt scaling, inference integrity, probability bounds ($[0, 1]$), feature importance aggregation.
  * Explainability: Centroid distance grounding and delta computations.

---

## 7. Known Discrepancies & Required Remedies

| Identified Discrepancy | Location | Required Resolution |
| :--- | :--- | :--- |
| Old test count claim ("21 tests") | Legacy Word report draft | Update report to reflect verified **32 tests** |
| Placeholders (`[Your Name]`, etc.) | Legacy Word report draft | Replace with Karthikeyan's student credentials |
| Conflicting Version B numbers (82% acc) | Legacy design notes | Completely purge Version B; document Version A exclusively |
| Missing machine-readable results | `results/` folder | Implement `src/evaluation.py` and output JSON & CSV |
| Missing presentation slides | `docs/` folder | Create comprehensive 15-slide `presentation.pptx` |
| Missing viva preparation guide | `docs/` folder | Create `docs/viva_questions.md` covering all 30+ questions |
| Missing UI screenshots | `screenshots/` folder | Capture genuine high-res screenshots of all 5 pages |

---

## 8. Audit Conclusion

The codebase is technically sound, modular, fully executable, and supported by a robust 32-test verification suite. The subsequent phases will formalize evaluation artifacts, update documentation, rebuild reports and presentations, capture genuine visual evidence, and package the complete submission for IBM evaluation.
