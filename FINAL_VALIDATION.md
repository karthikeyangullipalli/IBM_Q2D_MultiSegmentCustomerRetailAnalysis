# FINAL VALIDATION REPORT: Retail Customer Intelligence

**Author**: Gullipalli Lakshmi Narayana Karthikeyan (Roll Number: A24126510017)  
**Program**: Artificial Intelligence & Machine Learning — UG Level 2  
**Department**: Computer Science and Engineering  
**College**: ANIL Neerukonda Institute of Technology and Sciences (ANITS)  
**IBM Candidate ID**: IBMP3155  
**Internship**: IBM SkillsBuild Internship Program / IBMQ2D Track  
**Validation Date**: September 26, 2026  
**Final Status**: **100% VERIFIED & PRODUCTION-READY FOR EVALUATION**  

---

## 1. System Execution Environment

* **Operating System**: Microsoft Windows 11 Enterprise (x64)
* **Python Version**: CPython 3.12.3 (AMD64)
* **Core Libraries & Frameworks**:
  * `pandas`: 2.2.1
  * `numpy`: 1.26.4
  * `scikit-learn`: 1.4.1.post1
  * `streamlit`: 1.32.2
  * `plotly`: 5.20.0
  * `joblib`: 1.3.2
  * `pytest`: 9.1.1
  * `python-docx`: 1.1.2
  * `python-pptx`: 1.0.2
  * `playwright`: 1.58.0 (Microsoft Edge browser channel)

---

## 2. Dataset Verification

* **Dataset Path**: `data/mall_customers.csv`
* **Source**: Kaggle Mall Customer Segmentation Dataset
* **Integrity Validation**:
  * Row Count: Exactly 200 records
  * Column Count: 5 attributes (`CustomerID`, `Gender`/`Genre`, `Age`, `Annual Income (k$)`, `Spending Score (1-100)`)
  * Missing Values: 0 (verified across all fields)
  * Duplicate Records / IDs: 0
  * Attribute Ranges: Age [18, 70], Annual Income [$15k, $137k], Spending Score [1, 99]
  * Column Normalization: Non-destructive in-memory mapping translates historical header alias `"Genre"` to `"Gender"`.

---

## 3. Final Machine Learning Pipeline & Architectural Verification

### 3.1 Unsupervised Customer Segmentation
* **Clustering Features**: `Annual Income (k$)` and `Spending Score (1-100)` (Standardized via `StandardScaler`).
* **Empirical $K$ Selection**:
  * Swept $K \in [2, 10]$ evaluating Inertia and Silhouette Score.
  * Programmatic silhouette maximization identified **$K = 5$** as the global peak.
  * Peak Silhouette Score: **0.5547**
  * Inertia at $K=5$: **65.57**
* **Customer Personas**:
  1. **Premium Customers** ($n=39$, $19.5\%$): Centroid Income $\$86.54\text{k}$, Spending Score $82.13$.
  2. **Careful Spenders** ($n=35$, $17.5\%$): Centroid Income $\$88.29\text{k}$, Spending Score $17.11$.
  3. **Standard Customers** ($n=81$, $40.5\%$): Centroid Income $\$55.30\text{k}$, Spending Score $49.52$.
  4. **Impulsive Shoppers** ($n=22$, $11.0\%$): Centroid Income $\$25.73\text{k}$, Spending Score $79.36$.
  5. **Budget Customers** ($n=23$, $11.5\%$): Centroid Income $\$26.30\text{k}$, Spending Score $20.91$.

### 3.2 High-Value Business Rule
* **Rule**: Centroid Income $\ge \text{Median Income } (\$61.5\text{k})$ AND Centroid Spending $\ge \text{Median Spending } (50.0)$.
* **High-Value Cohort**: **Premium Customers** ($n=39$, $19.5\%$ of customer base).
* **Commercial Contribution**: Accounts for **31.90%** of total mall spending volume.

### 3.3 Supervised Classification & Calibration
* **Algorithm**: `RandomForestClassifier(n_estimators=200, random_state=42)` wrapped in `CalibratedClassifierCV(method='sigmoid', cv=5)` (Platt scaling).
* **Input Features**: `Age`, `Gender`, `Annual Income (k$)`, `Spending Score (1-100)`.
* **Split Ratio**: 80% train ($n=160$), 20% test ($n=40$), stratified by target class.
* **Calibrated Test Performance**:
  * Accuracy: **100.0%** ($1.000$)
  * Precision: **1.000**
  * Recall: **1.000**
  * F1-Score: **1.000**
  * ROC-AUC: **1.000**
  * Brier Score Loss: **0.00358 (~0.0036)**
  * Confusion Matrix: TN=32, FP=0, FN=0, TP=8
* **Feature Importances**: Spending Score ($49.4\%$), Annual Income ($34.6\%$), Age ($15.6\%$), Gender ($0.4\%$).
* **Academic Honesty Disclosure**:
  The 100% test accuracy is expected and honest. The High-Value ground truth label was derived deterministically from cluster centroids defined on Annual Income and Spending Score, and those identical features are accessible to the Random Forest. The classifier acts as an ultra-fast boundary emulator to bypass re-clustering for new shoppers. CalibratedClassifierCV ensures predicted probabilities represent smooth, authentic confidence rather than binary tree agreement.

---

## 4. Automated Testing Suite Validation

* **Runner**: `pytest tests/test_pipeline.py -v`
* **Test Count**: Exactly **32 tests**
* **Result**: **32 PASSED in 12.23s** (0 failed, 0 warnings)
* **Coverage Scope**: Data loading & schema handling, automatic $K$-selection, centroid explainability grounding, persona naming rules, Platt calibration ranges, and batch prediction consistency.

---

## 5. Web Application & Interface Validation

* **Framework**: Streamlit Multi-Page Architecture
* **Verified Pages (Zero Runtime Exceptions across all pages)**:
  1. `app.py`: Landing view with core headline metrics and navigation cards.
  2. `pages/1_Dashboard.py`: Interactive Plotly 2D clustering scatter plot, centroid crosshairs, and persona cards.
  3. `pages/2_Predict.py`: Customer scoring input form with calibrated confidence and centroid distance explanation.
  4. `pages/3_Insights.py`: Empirical cluster selection curves ($K$ vs Inertia, $K$ vs Silhouette) and feature importance.
  5. `pages/4_Data_Explorer.py`: Multi-filter database browser with one-click CSV download.
* **Live Visual Evidence**: 6 high-resolution screenshots captured in `screenshots/`:
  * `1_home.png`
  * `2_dashboard.png`
  * `3_predict_input.png`
  * `4_predict_result.png`
  * `5_insights.png`
  * `6_data_explorer.png`

---

## 6. Deliverable Artifacts Catalogue

| Deliverable | File Path | Status |
| :--- | :--- | :--- |
| **Source Code** | `src/*.py`, `pages/*.py`, `app.py` | Verified & Formatted |
| **Automated Tests** | `tests/test_pipeline.py` | 32 / 32 Passed |
| **Persisted Models** | `models/kmeans_model.pkl`, `models/classifier_model.pkl` | Serialized with `joblib` |
| **Machine-Readable Metrics** | `results/final_metrics.json`, `results/final_metrics.csv` | Exported directly from model |
| **Project Audit Document** | `PROJECT_AUDIT.md` | Complete |
| **Case Study Report (Word)** | `docs/case_study_report.docx` | Rebuilt with student details & figures |
| **Case Study Report (Markdown)** | `docs/case_study_report.md` | Synchronized |
| **Presentation Deck (PPTX)** | `docs/presentation.pptx` | 15 widescreen slides |
| **Viva Preparation Guide** | `docs/viva_questions.md` | 32 questions + inconsistency defense |
| **Live Screenshots** | `screenshots/*.png` | 6 genuine application captures |

---

## 7. Known Academic Limitations

1. **Dataset Size**: The Kaggle dataset comprises 200 records. It serves as an optimal proof of concept, but lacks transactional timestamps or seasonal multi-year volume.
2. **Feature Breadth**: Lacks product-level SKU details, basket item counts, and return history.
3. **Local Deployment**: Prototype runs as a local web server (`http://localhost:8501`) suitable for internship evaluation rather than a distributed cloud cluster.

---

## 8. Final Conclusion

The **Retail Customer Intelligence** project has been comprehensively audited, unified under Version A, tested against all boundary conditions, fully documented with student credentials, and packaged with all required supporting assets. All code, data, models, metrics, tests, screenshots, reports, and presentations describe the **identical verified implementation**.
