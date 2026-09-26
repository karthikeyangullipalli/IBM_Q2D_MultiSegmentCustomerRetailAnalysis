# Retail Customer Intelligence
## A Machine Learning Prototype for Customer Segmentation and High-Value Shopper Prediction

**IBM SkillsBuild Internship Program — IBMQ2D Track (UG Level 2)**  
**Student Name**: Gullipalli Lakshmi Narayana Karthikeyan  
**Roll Number**: A24126510017  
**Department**: Computer Science and Engineering  
**College**: ANIL Neerukonda Institute of Technology and Sciences (ANITS)  
**IBM ID**: IBMP3155  
**Submission Date**: September 26, 2026  

---

### Abstract
Retail businesses frequently treat every customer identically, allocating marketing budgets and customer relationship management resources without regard to behavioral concentration. This project delivers an end-to-end, reproducible customer intelligence prototype combining unsupervised behavioral clustering and calibrated supervised classification on the 200-record Kaggle Mall Customer Segmentation dataset.

Using Annual Income and Spending Score, K-Means clustering was evaluated across $K \in [2, 10]$. Optimal cluster count was determined programmatically via silhouette score maximization, identifying $K=5$ with a peak silhouette score of **0.5547** (inertia: 65.57). Tercile centroid profiling revealed five distinct behavioral personas: Premium Customers, Careful Spenders, Standard Customers, Impulsive Shoppers, and Budget Customers. A transparent business rule designated clusters whose centroid meets or exceeds both median income ($61.5k) and median spending (50.0) as High-Value. Under this rule, the Premium Customers segment (39 shoppers, 19.5% of base) qualifies, accounting for **31.90%** of the aggregate Spending Score across the dataset.

To score customer profiles via instant inference without re-clustering, a 200-tree Random Forest classifier was trained on Age, Gender, Annual Income, and Spending Score using an 80/20 stratified split. The classifier learns the deterministic decision boundary induced by the income and spending thresholds used to define the High-Value cohort. Calibrated with sigmoid (Platt) scaling (`CalibratedClassifierCV`) over 5 folds, sigmoid calibration transforms raw classifier scores into probability estimates intended to be better calibrated, achieving 100% test accuracy, precision, recall, and F1-score with a Brier score loss of 0.00358. The entire pipeline is operationalized as a 5-page interactive Streamlit web application and validated by 32 automated pytest tests.

---

### Key Verified Metrics
- **Dataset Records**: 200 rows, 5 features, 0 missing values
- **Optimal Clusters ($K$)**: 5 (selected by silhouette score maximization)
- **Peak Silhouette Score**: **0.5547** (Inertia: 65.57)
- **High-Value Customers**: 39 ($19.5\%$ of base)
- **Aggregate Spending Score Share**: **31.90%** of aggregate Spending Score across the dataset
- **Classifier Architecture**: `RandomForestClassifier(n_estimators=200)` + `CalibratedClassifierCV(method='sigmoid', cv=5)`
- **Train / Test Split**: 80% train (160), 20% test (40), stratified
- **Test Set Accuracy**: **100.0%**
- **Test Precision / Recall / F1**: **1.000 / 1.000 / 1.000**
- **ROC-AUC**: **1.000**
- **Brier Score Loss**: **0.00358**
- **Feature Importance**: Spending Score (49.4%), Income (34.6%), Age (15.6%), Gender (0.4%)
- **Automated Tests**: **32 tests passed in 12.23s**

---

### Academic Transparency Note on 100% Accuracy
The 100% accuracy on the test set is expected and honest: the High-Value ground truth label was derived deterministically from cluster centroids on Annual Income and Spending Score, and those identical features are accessible to the Random Forest classifier. The classifier learns the deterministic decision boundary induced by the income and spending thresholds used to define the High-Value cohort. Sigmoid calibration transforms raw classifier scores into probability estimates intended to be better calibrated.
