# FINAL SUBMISSION CHECK: Retail Customer Intelligence

**Author**: Gullipalli Lakshmi Narayana Karthikeyan (Roll Number: A24126510017)  
**Program**: Artificial Intelligence & Machine Learning — UG Level 2  
**Department**: Computer Science and Engineering  
**College**: ANIL Neerukonda Institute of Technology and Sciences (ANITS)  
**IBM Candidate ID**: IBMP3155  
**Internship Track**: IBM SkillsBuild Internship Program / IBMQ2D Track  
**Date of Sign-Off**: September 26, 2026  
**Final Submission Status**: **COMPLETE, VERIFIED, & SUBMISSION-READY**  

---

## 1. Verified Deliverables & File Paths

Every required submission deliverable has been verified on disk in [`retail-customer-intelligence`](file:///C:/Users/DELL/OneDrive/Desktop/retail-customer-intelligence-mvp/retail-customer-intelligence):

| Deliverable Name | File Path | Format / Size | Status |
| :--- | :--- | :--- | :--- |
| **Internship Report (Word)** | `docs/case_study_report.docx` | DOCX / ~497 KB | Rebuilt with full credentials, tables & figures |
| **Internship Report (Markdown)** | `docs/case_study_report.md` | Markdown / ~4 KB | Synchronized text copy |
| **Presentation Deck (PPTX)** | `docs/presentation.pptx` | PPTX / ~349 KB | 15 widescreen slides with screenshots & cards |
| **Presentation Outline** | `docs/presentation.md` | Markdown / ~1 KB | Slide summary |
| **Viva Voce Prep Guide** | `docs/viva_questions.md` | Markdown / ~14 KB | 32 technical Q&As + technical clarifications |
| **Project Audit Document** | `PROJECT_AUDIT.md` | Markdown / ~6 KB | Full audit & architectural decision record |
| **Final Validation Report** | `FINAL_VALIDATION.md` | Markdown / ~6 KB | Execution checklist & environment verification |
| **Final Submission Check** | `FINAL_SUBMISSION_CHECK.md` | Markdown | This sign-off document |
| **Project README** | `README.md` | Markdown / ~8 KB | Master repository guide with student details |
| **Machine-Readable Metrics (JSON)**| `results/final_metrics.json` | JSON / ~6 KB | Direct exported metrics from trained models |
| **Machine-Readable Metrics (CSV)** | `results/final_metrics.csv` | CSV / ~1 KB | Direct exported summary table |
| **Evaluation Module** | `src/evaluation.py` | Python / ~6 KB | Standalone evaluation & export script |
| **Automated Test Suite** | `tests/test_pipeline.py` | Python / ~15 KB | 32 passed unit & integration tests |
| **Live UI Screenshots** | `screenshots/*.png` | 6 PNG images | Genuine high-resolution application screen captures |
| **Trained Models (Joblib)** | `models/*.pkl` | Serialized artifacts | Cached K-Means & Calibrated Random Forest models |
| **Interactive Streamlit App** | `app.py`, `pages/*.py` | 5 Streamlit pages | Verified with 0 runtime exceptions |

---

## 2. Definitive Final Metrics

All reported numbers are derived from direct execution on `data/mall_customers.csv`:

* **Dataset Size**: Exactly 200 records, 5 features, 0 missing values, 0 duplicate IDs.
* **Optimal Clusters ($K$)**: **5** (Programmatic silhouette score maximization over $K \in [2, 10]$).
* **Peak Silhouette Score**: **0.5547** (Standardized Income and Spending plane).
* **Inertia at $K=5$**: **65.57**.
* **High-Value Cohort**: **39 customers** ($19.5\%$ of the total customer base).
* **Aggregate Spending Score Share**: The Premium Customer segment accounts for **31.90%** of the aggregate Spending Score across the dataset.
* **Classifier Algorithm**: `RandomForestClassifier(n_estimators=200)` wrapped in `CalibratedClassifierCV(method='sigmoid', cv=5)` (Platt scaling).
* **Classifier Features**: `Age`, `Gender` (encoded Male=0, Female=1), `Annual Income (k$)`, `Spending Score (1-100)`.
* **Train / Test Partition**: 80% train ($n=160$), 20% test ($n=40$), stratified by class.
* **Test Accuracy**: **100.0%** ($40 / 40$ correct predictions).
* **Test Precision / Recall / F1-Score**: **1.000 / 1.000 / 1.000**.
* **ROC-AUC Score**: **1.000**.
* **Brier Score Loss**: **0.00358 (~0.0036)**.
* **Feature Importance Ranking**:
  1. Spending Score (1-100): **49.4%**
  2. Annual Income (k$): **34.6%**
  3. Age: **15.6%**
  4. Gender: **0.4%**

---

## 3. Final Test Suite Results

* **Command**: `pytest tests/test_pipeline.py -v`
* **Execution Time**: ~11.8 seconds
* **Pass Rate**: **32 of 32 tests passed (100%)**
* **Failures / Warnings**: **0 failures, 0 warnings**
* **AppTest Integration**: All 5 Streamlit pages (`app.py`, `1_Dashboard.py`, `2_Predict.py`, `3_Insights.py`, `4_Data_Explorer.py`) verified to render cleanly with zero exceptions.

---

## 4. Technical Language Audit & Implementation Parity

1. **High-Value Decision Boundary**:
   All files describe the classifier boundary with technically rigorous phrasing:
   *"The classifier learns the deterministic decision boundary induced by the income and spending thresholds used to define the High-Value cohort."*
2. **Platt Calibration**:
   All files state calibration mechanics accurately:
   *"Sigmoid calibration transforms raw classifier scores into probability estimates intended to be better calibrated."*
3. **Spending Score Metric**:
   All files strictly reflect that the dataset contains `Spending Score (1-100)`, not monetary currency amounts:
   *"The Premium Customer segment accounts for 31.90% of the aggregate Spending Score across the dataset."*
4. **Instant Inference**:
   Misleading real-time claims have been replaced with "interactive", "live prediction", or "instant inference".
5. **Purge of Legacy Claims**:
   Search across all project files confirmed that obsolete strings (`82%`, `0.9272`, `75/25`, `100 trees`, `Vercel`, `Chart.js`, `21 tests`, `static HTML`) have been completely eliminated.
6. **Implementation Parity Confirmation**:
   The report (`case_study_report.docx` & `case_study_report.md`), presentation deck (`presentation.pptx`), viva preparation guide (`viva_questions.md`), audit document (`PROJECT_AUDIT.md`), validation document (`FINAL_VALIDATION.md`), README (`README.md`), and machine-readable metrics (`results/final_metrics.json`) describe the **exact same final implementation**.

---

## 5. Remaining Known Limitations

1. **Static Dataset**: The Kaggle Mall Customer dataset consists of 200 records without time-series transaction dates or seasonal timestamps.
2. **Behavioral Scope**: Features are limited to demographic and broad spending indices (Spending Score 1-100), lacking basket SKU details and return rates.
3. **Prototype Deployment**: Deployed as an interactive local Streamlit prototype (`http://localhost:8501`) designed for academic and internship evaluation rather than a multi-tenant cloud SaaS platform.

---

## 6. Final Sign-Off

The **Retail Customer Intelligence** project is mathematically verified, fully reproducible, defensible in a viva voce examination, and ready for submission to the IBM SkillsBuild internship review committee.
