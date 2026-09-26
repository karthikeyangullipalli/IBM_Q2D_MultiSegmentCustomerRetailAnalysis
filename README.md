# Retail Customer Intelligence
### A Machine Learning Prototype for Customer Segmentation and High-Value Shopper Prediction

**IBM SkillsBuild Internship Program — IBMQ2D Track (UG Level 2 AIML)**  
**Student Name**: Gullipalli Lakshmi Narayana Karthikeyan  
**Roll Number**: A24126510017  
**Department**: Computer Science and Engineering  
**Institution**: ANIL Neerukonda Institute of Technology and Sciences (ANITS)  
**IBM Candidate ID**: IBMP3155  
**Submission Date**: September 26, 2026  

---

## 1. Project Overview

Retail businesses frequently treat every customer identically, allocating marketing budgets and CRM resources uniformly without regard to behavioral concentration. This project delivers an end-to-end, reproducible customer intelligence prototype that couples unsupervised behavioral clustering with calibrated supervised classification on the 200-record Kaggle Mall Customer Segmentation dataset.

1. **Unsupervised Segmentation**: Discovers natural customer buying personas using K-Means clustering on Annual Income and Spending Score. The cluster count ($K=5$) is chosen programmatically by evaluating $K \in [2, 10]$ through silhouette score maximization, not assumed.
2. **Transparent Business Rule**: Applies an auditable median-based threshold to identify High-Value shoppers (19.5% of the customer base accounting for **31.90%** of the aggregate Spending Score across the dataset).
3. **Calibrated Classification**: Trains a 200-tree Random Forest wrapped in `CalibratedClassifierCV` (sigmoid/Platt scaling) so customer profiles are scored via instant inference from Age, Gender, Income, and Spending Score alone — without re-running K-Means.
4. **Interactive Delivery**: Deployed as an interactive 5-page Streamlit application with custom typography, responsive Plotly charts, grounded mathematical explanations, and CSV export.
5. **Quality Assurance**: Verified by an automated 32-test pytest suite passing with zero errors.

---

## 2. Dataset Information

* **Dataset**: Kaggle Mall Customer Segmentation Dataset (`data/mall_customers.csv`).
* **Volume**: Exactly 200 rows, 5 features, 0 missing values, 0 duplicate IDs.
* **Attributes**: `CustomerID`, `Gender` (or Kaggle's historical alias `Genre`), `Age` (18–70), `Annual Income (k$)` ($15k–$137k), and `Spending Score (1-100)` (1–99).
* **Metric Nature**: Spending Score is an assigned behavioral index (1-100), not a direct currency amount.
* **Non-Destructive Ingestion**: Kaggle's historical `"Genre"` column header and other common aliases are normalized in memory by `src/data_loader.py` without mutating the underlying CSV file on disk.

---

## 3. Quick Start & Execution

### 3.1 Installation
```bash
pip install -r requirements.txt
```

### 3.2 Run the Web Application
```bash
streamlit run app.py
```
Opens in your browser at `http://localhost:8501`. Models bootstrap and train automatically on first run in seconds and are cached in `models/` for sub-second subsequent startup.

### 3.3 Run Automated Tests
```bash
pytest tests/test_pipeline.py -v
```
Executes all 32 unit and integration tests covering data validation, K-selection, persona rules, calibration bounds, and prediction consistency.

### 3.4 Generate Final Evaluation Metrics
```bash
python src/evaluation.py
```
Generates comprehensive machine-readable results in `results/final_metrics.json` and `results/final_metrics.csv`.

---

## 4. Key Reproducible Results

All metrics below are derived directly from model execution on the dataset:

| Category | Metric | Verified Value | Ground-Truth Source |
| :--- | :--- | :--- | :--- |
| **Clustering** | Optimal Clusters ($K$) | **5** | Programmatic silhouette maximization ($K=2..10$) |
| **Clustering** | Peak Silhouette Score | **0.5547** | $K=5$ on Standardized Income & Spending |
| **Clustering** | Inertia ($K=5$) | **65.57** | Within-cluster sum of squared errors |
| **High-Value Cohort** | Customer Count | **39** ($19.5\%$ of base) | Centroid Income $\ge \$61.5\text{k}$ & Spend $\ge 50.0$ |
| **High-Value Cohort** | Aggregate Spending Score Share | **31.90%** | Premium Customers account for 31.90% of aggregate score |
| **Classification** | Test Set Accuracy | **100.0%** | Stratified held-out test split (40 customers) |
| **Classification** | Precision / Recall / F1 | **1.000 / 1.000 / 1.000** | Stratified held-out test split (40 customers) |
| **Classification** | ROC-AUC Score | **1.000** | Perfect separation of ranking probabilities |
| **Classification** | Brier Score Loss | **0.00358 (~0.0036)** | Platt calibrated confidence error |
| **Feature Importance** | Spending Score | **49.4%** | Primary separator |
| **Feature Importance** | Annual Income | **34.6%** | Secondary separator |
| **Feature Importance** | Age & Gender | **15.6%** (Age), **0.4%** (Gender) | Demographic attributes |
| **Quality Assurance** | Automated Test Suite | **32 tests passed in ~12s** | `pytest tests/test_pipeline.py` |

---

## 5. Customer Personas

Using dataset terciles on Annual Income and Spending Score, the five discovered clusters represent distinct commercial archetypes:

1. **Premium Customers** ($n=39$, $19.5\%$): High Income ($86.54k), High Spending ($82.13). High-Value (100%). **Strategy**: VIP loyalty rewards, exclusive concierge, early inventory access.
2. **Careful Spenders** ($n=35$, $17.5\%$): High Income ($88.29k), Low Spending ($17.11). **Strategy**: Trust-building campaigns, quality-led messaging, personalized outreach to unlock spend.
3. **Standard Customers** ($n=81$, $40.5\%$): Mid Income ($55.30k), Mid Spending ($49.52). **Strategy**: Seasonal promotions, category cross-selling, loyalty program upgrades.
4. **Impulsive Shoppers** ($n=22$, $11.0\%$): Low Income ($25.73k), High Spending ($79.36). **Strategy**: Flash sales, limited-time promotions, impulse checkout bundles.
5. **Budget Customers** ($n=23$, $11.5\%$): Low Income ($26.30k), Low Spending ($20.91). **Strategy**: Value bundles, clearance deals, price-match guarantees.

---

## 6. High-Value Definition & Classifier Calibration

* **Business Rule**: A cluster is High-Value iff:
  $$\text{Centroid Income} \ge \text{Median Income } (\$61.5\text{k}) \quad \text{AND} \quad \text{Centroid Spending Score} \ge \text{Median Spending Score } (50.0)$$
* **Why Calibration is Required**: Because the High-Value ground truth label is a deterministic function of Income and Spending Score, raw Random Forest tree votes collapse to extreme ~0% or ~100% agreement. `CalibratedClassifierCV` (sigmoid / Platt scaling over 5 folds) transforms raw classifier scores into probability estimates intended to be better calibrated, achieving a calibrated Brier score loss of **0.00358**.

---

## 7. Academic Transparency on 100% Accuracy

The 100% test accuracy is expected, genuine, and academically transparent. It is not an artifact of data leakage or overfitting:
1. In this hybrid architecture, the High-Value target label was derived deterministically from cluster centroids defined on Annual Income and Spending Score.
2. Because Annual Income and Spending Score are also supplied as inputs to the Random Forest, the classifier learns the deterministic decision boundary induced by the income and spending thresholds used to define the High-Value cohort.
3. Its purpose is operational: scoring customer profiles via instant inference without re-clustering the entire historical dataset.
4. In real-world enterprise deployments with noisy, independent transactional churn data, accuracy would typically range between 80% and 90%.

---

## 8. Application Pages

The application is structured into five cohesive Streamlit pages:
* **Home (`app.py`)**: Problem statement, architectural overview, and headline dataset KPIs.
* **Dashboard (`pages/1_Dashboard.py`)**: 2D customer scatter plot with centroid markers, persona cards, and strategic actions.
* **Predict (`pages/2_Predict.py`)**: Interactive inference interface taking Age, Gender, Income, and Spending Score to output persona, High-Value status, calibrated confidence, and grounded centroid distance explanations.
* **Insights (`pages/3_Insights.py`)**: Empirical cluster selection curves ($K$ vs Inertia, $K$ vs Silhouette), feature importances, and automated business insights.
* **Data Explorer (`pages/4_Data_Explorer.py`)**: Multi-column filterable customer table with one-click CSV export.

---

## 9. Project Directory Structure

```text
retail-customer-intelligence/
├── .gitignore                       # Git ignore file (virtualenvs, pycache, OS files)
├── .streamlit/
│   └── config.toml                  # Streamlit layout & theme configuration
├── app.py                           # Application entry point & model bootstrapper
├── README.md                        # Project documentation (this file)
├── PROJECT_AUDIT.md                 # Complete architectural audit document
├── FINAL_VALIDATION.md              # Final validation report & checklist
├── FINAL_SUBMISSION_CHECK.md        # Submission sign-off & technical consistency check
├── requirements.txt                 # Python dependencies
├── data/
│   └── mall_customers.csv           # Cleaned Kaggle customer segmentation dataset
├── docs/
│   ├── architecture_diagram.png     # Modular architecture diagram
│   ├── case_study_report.docx       # Full internship report (Word document with figures)
│   ├── case_study_report.md         # Full internship report (Markdown copy)
│   ├── presentation.pptx            # 15-slide widescreen PowerPoint deck
│   ├── presentation.md              # Presentation slide deck outline
│   └── viva_questions.md            # 32 viva questions, answers & technical clarifications
├── models/                          # Serialized model artifacts (joblib)
│   ├── classifier_model.pkl
│   ├── kmeans_model.pkl
│   ├── scored_customers.csv
│   └── training_summary.pkl
├── pages/                           # Streamlit multi-page interface
│   ├── 1_Dashboard.py
│   ├── 2_Predict.py
│   ├── 3_Insights.py
│   └── 4_Data_Explorer.py
├── results/                         # Machine-readable output metrics
│   ├── final_metrics.csv
│   └── final_metrics.json
├── screenshots/                     # High-resolution application screenshots
│   ├── 1_home.png
│   ├── 2_dashboard.png
│   ├── 3_predict_input.png
│   ├── 4_predict_result.png
│   ├── 5_insights.png
│   └── 6_data_explorer.png
├── scripts/                         # Automation & generation utilities
│   ├── build_presentation_pptx.py
│   ├── build_report_doc.py
│   └── capture_screenshots.py
├── src/                             # Core Python service layer
│   ├── __init__.py
│   ├── classifier.py                # Random Forest with Platt scaling
│   ├── clustering.py                # K-Means, auto K-selection, centroid explainability
│   ├── data_loader.py               # CSV loader, alias normalizer, data validator
│   ├── evaluation.py                # Machine-readable metrics exporter
│   ├── persona_rules.py             # Tercile bucketing, High-Value rule, marketing actions
│   ├── theme.py                     # Central styling tokens & CSS injection
│   └── utils.py                     # Pipeline orchestration & artifact persistence
└── tests/
    └── test_pipeline.py             # 32 automated unit and integration tests
```

---

## 10. Limitations & Future Scope

### Limitations
* **Sample Size**: 200 customer rows serve as an effective academic proof of concept, but lack multi-year seasonal depth.
* **Feature Scope**: Does not capture transactional timestamps, recency, SKU categories, or return rates. Spending Score is an index (1-100), not currency amounts.
* **Single-Tenant Local Deployment**: Developed as a local web prototype (`http://localhost:8501`) rather than a multi-tenant cloud application.

### Future Scope
* **Enterprise Warehouse Integration**: Connect SQL streams from Snowflake or BigQuery for batch customer scoring.
* **RFM Feature Engineering**: Expand clustering to include Recency, Frequency, and Monetary metrics.
* **Containerized Microservice**: Wrap the inference engine in a Dockerized FastAPI service exposing RESTful `/predict` and `/batch` endpoints.
