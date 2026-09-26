# Comprehensive Viva Preparation Guide: Retail Customer Intelligence

**Author**: Gullipalli Lakshmi Narayana Karthikeyan (Roll: A24126510017)  
**Program**: Artificial Intelligence & Machine Learning — UG Level 2  
**Institution**: ANIL Neerukonda Institute of Technology and Sciences (ANITS)  
**IBM Track**: IBM SkillsBuild Internship Program / IBMQ2D (IBM ID: IBMP3155)  
**Date**: September 26, 2026  

---

## Part 1: Core Machine Learning & Methodology Questions

### 1. Why did you choose K-Means for customer segmentation?
**Answer**: K-Means is a centroid-based, computationally efficient ($O(n \cdot k \cdot d \cdot i)$) unsupervised clustering algorithm well-suited for spherical, continuous feature distributions like Annual Income and Spending Score. It produces clearly defined mathematical centroids that represent the "average customer" in each persona, which provides a transparent baseline for both persona naming and distance-based explainability.

### 2. Why did you use only Annual Income and Spending Score for clustering instead of all features?
**Answer**: Feature selection was determined empirically by comparing silhouette scores across candidate feature sets:
* **Income + Spending Score**: Best silhouette score of **0.5547** at $K=5$.
* **Age + Income + Spending**: Peak silhouette dropped to **0.4281** at $K=6$.
* **Age + Income + Spending + Gender**: Peak silhouette dropped further to **0.4210** at $K=10$ (a non-actionable number of segments).
Adding Age or Gender introduces noise and dilutes cluster density in Euclidean distance space. Annual Income and Spending Score represent the purest commercial behavioral plane. Age and Gender are preserved for downstream supervised classification and persona demographic profiling.

### 3. Why is feature scaling (StandardScaler) necessary before running K-Means?
**Answer**: K-Means calculates cluster assignment based on Euclidean distance:
$$d(x, c) = \sqrt{\sum_{j=1}^{p} (x_j - c_j)^2}$$
Annual Income ranges from $\$15\text{k}$ to $\$137\text{k}$ (variance $\approx 689$), while Spending Score ranges from $1$ to $99$ (variance $\approx 667$). Without standardization, whichever feature has larger numerical variance dominates distance calculations. `StandardScaler` transforms features to zero mean ($\mu = 0$) and unit variance ($\sigma = 1$), ensuring equal geometric weighting.

### 4. How was the optimal number of clusters ($K$) selected?
**Answer**: The value of $K$ was not hardcoded or assumed. We evaluated an empirical sweep of $K \in [2, 10]$ measuring both Inertia (within-cluster sum of squares) and Silhouette Score. Silhouette score was selected as the sole programmatic decision rule because it possesses a well-defined global mathematical maximum, whereas the inertia "elbow" method requires subjective visual estimation. The algorithm identified $K=5$ as the global peak silhouette score of **0.5547**.

### 5. What is the Silhouette Score and how is it interpreted?
**Answer**: The silhouette coefficient for a sample $i$ measures how cohesive it is within its own cluster compared to how separated it is from the nearest neighboring cluster:
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
where $a(i)$ is the mean intra-cluster distance, and $b(i)$ is the mean nearest-cluster distance. Scores range from $-1$ (incorrectly assigned) to $+1$ (dense, highly separated). A score of **0.5547** at $K=5$ indicates robust, well-defined cluster separation.

### 6. What is Inertia (Within-Cluster Sum of Squares)?
**Answer**: Inertia measures cluster compactness by summing squared Euclidean distances from each data point to its assigned centroid:
$$\text{Inertia} = \sum_{j=1}^{K} \sum_{x \in C_j} \|x - \mu_j\|^2$$
Lower inertia denotes denser clusters. However, inertia monotonically decreases with increasing $K$ (reaching zero when $K=N$). Hence, it must be paired with silhouette score or an elbow inflection test to avoid overfitting.

### 7. What is a cluster centroid?
**Answer**: A centroid $\mu_j$ is the geometric center of cluster $j$, computed as the mean coordinate of all points belonging to that cluster:
$$\mu_j = \frac{1}{|C_j|} \sum_{x \in C_j} x$$
In our system, centroids represent the archetypal profile of each persona (e.g., the Premium Customers centroid is $\$86.54\text{k}$ income, $82.13$ spending score).

### 8. How were the customer personas named?
**Answer**: Personas are named deterministically using tercile bucketing of Annual Income and Spending Score across the dataset ($33\text{rd}$ and $67\text{th}$ percentiles). Each centroid coordinate is categorized as Low, Mid, or High:
* **High Income, High Spending**: Premium Customers ($n=39$)
* **High Income, Low Spending**: Careful Spenders ($n=35$)
* **Mid Income, Mid Spending**: Standard Customers ($n=81$)
* **Low Income, High Spending**: Impulsive Shoppers ($n=22$)
* **Low Income, Low Spending**: Budget Customers ($n=23$)
This ensures naming is reproducible and grounded in data rather than subjective guessing.

### 9. What is your exact definition of a "High-Value Customer"?
**Answer**: A customer is High-Value if and only if their cluster centroid meets or exceeds both dataset medians:
$$\text{Centroid Income} \ge \text{Median Income } (\$61.5\text{k}) \quad \text{AND} \quad \text{Centroid Spending} \ge \text{Median Spending } (50.0)$$
Under this transparent rule, exactly one cluster qualifies: **Premium Customers**. They represent 39 customers (19.5% of base), and the Premium Customer segment accounts for **31.90%** of the aggregate Spending Score across the dataset.

### 10. Why use Random Forest for the supervised classification stage?
**Answer**: Random Forest is an ensemble of decision trees utilizing bagging (bootstrap aggregating) and random feature subspace projection. It handles non-linear decision boundaries without requiring explicit kernel transformations, exhibits resistance to overfitting, and provides natural feature importance measures. In our system, it learns the cluster boundaries to score customer profiles via instant inference without re-running K-Means.

### 11. What features are fed to the Random Forest classifier?
**Answer**: Four features: `Age`, `Gender` (binary encoded: Male=0, Female=1), `Annual Income (k$)`, and `Spending Score (1-100)`.

### 12. Why not use a simpler model like Logistic Regression?
**Answer**: Logistic Regression creates a linear boundary. While the High-Value quadrant is broadly separable in 2D, Random Forest naturally captures multi-feature non-linear interactions across Age, Gender, Income, and Spending without requiring manual polynomial feature engineering.

### 13. What is train/test split and why is it used?
**Answer**: Splitting data into distinct training (80%, $n=160$) and testing (20%, $n=40$) partitions evaluates model generalization on unseen observations, ensuring the model has not merely memorized the training samples.

### 14. What is stratification and why was it applied?
**Answer**: Stratification preserves the class distribution ratio in both training and test partitions. Since High-Value customers represent only 19.5% of the population, random splitting without stratification could result in severe test set imbalance. With `stratify=y`, both train and test partitions contain exactly 19.5% positive instances.

### 15. What is Accuracy and why is it insufficient on its own?
**Answer**: Accuracy is the proportion of total correct predictions:
$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
In imbalanced datasets (e.g., 90% negative, 10% positive), a naive model predicting all negatives achieves 90% accuracy while failing completely at identifying the target. Hence, Precision, Recall, F1, and Brier score must be evaluated.

### 16. What is Precision?
**Answer**: Precision measures exactness — out of all instances predicted as High-Value, what proportion were actually High-Value:
$$\text{Precision} = \frac{TP}{TP + FP}$$
Our model achieved 1.000 (0 false positives).

### 17. What is Recall (Sensitivity)?
**Answer**: Recall measures completeness — out of all actual High-Value customers in the test partition, what proportion did the model correctly identify:
$$\text{Recall} = \frac{TP}{TP + FN}$$
Our model achieved 1.000 (0 false negatives).

### 18. What is the F1-Score?
**Answer**: F1-Score is the harmonic mean of Precision and Recall:
$$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
It penalizes extreme trade-offs between precision and recall. Our model achieved 1.000.

### 19. What is ROC-AUC?
**Answer**: Receiver Operating Characteristic — Area Under Curve (ROC-AUC) measures the probability that a randomly chosen positive instance receives a higher predicted probability than a randomly chosen negative instance across all possible classification thresholds. Our model achieved 1.000.

### 20. What is Brier Score Loss?
**Answer**: Brier score measures the mean squared difference between predicted probabilities and actual binary outcomes ($y \in \{0, 1\}$):
$$\text{Brier} = \frac{1}{N} \sum_{i=1}^{N} (p_i - y_i)^2$$
Scores range from 0 (perfect probability calibration) to 1. Our model achieved an exceptionally low Brier score of **0.00358**, confirming low mean squared probability error.

### 21. What is Platt Scaling (Sigmoid Calibration) and why was it necessary?
**Answer**: In standard Random Forest, `predict_proba()` is simply the fraction of trees voting for the positive class. When predicting a cleanly separable cluster-derived label, almost all 200 trees vote identically, collapsing probabilities to extreme 0% or 100% values. Platt scaling (`CalibratedClassifierCV(method='sigmoid', cv=5)`) fits a 1-D logistic regression model on held-out cross-validation folds. Sigmoid calibration transforms raw classifier scores into probability estimates intended to be better calibrated.

### 22. What is Feature Importance and which features matter most?
**Answer**: Gini impurity-based feature importance measures the total reduction in criterion brought by that feature across all trees:
* **Spending Score**: **49.4%**
* **Annual Income**: **34.6%**
* **Age**: **15.6%**
* **Gender**: **0.4%**
Income and Spending account for 84.0% of decision weight, which validates that clustering and classification are mutually coherent.

### 23. What is overfitting and how did you prevent it?
**Answer**: Overfitting occurs when a model learns noise in training data rather than underlying patterns. We mitigated overfitting by:
* Using an ensemble of 200 trees with bootstrap aggregation.
* Implementing 5-fold cross-validation during probability calibration.
* Evaluating on an untouched, stratified 20% held-out test partition.

### 24. What are the limitations of the Mall Customer dataset?
**Answer**:
* Sample size is modest ($N = 200$).
* Static snapshot lacking time-series purchase history (recency, frequency).
* The Spending Score is an assigned index (1-100), not actual currency amounts.
* No product categories, return rates, or margins.

### 25. How would you adapt this system for enterprise transactional data?
**Answer**:
* Engineer RFM (Recency, Frequency, Monetary) features from point-of-sale logs.
* Extract basket diversity, return rates, and seasonal purchase trends.
* Replace static CSV loading with streaming data warehouse connectors.
* Implement rolling retraining to accommodate seasonal customer drift.

### 26. What changes would you make to deploy this in production?
**Answer**:
* Package inference inside a containerized FastAPI service with Docker.
* Store model artifacts in an enterprise model registry.
* Connect persistent database for inference audit logging.
* Set up automated CI/CD pipelines with regression testing.

---

## Part 2: Technical Accuracy & Evaluator Clarifications

### 27. "Your test set accuracy is 100%. Did your model overfit or is there an explanation?"
**Answer**:
"The 100% test accuracy is expected, genuine, and academically transparent. It is not an artifact of data leakage or overfitting. In our hybrid pipeline, the High-Value ground truth label was derived deterministically from cluster centroids defined on Annual Income and Spending Score. Because those exact two features are provided as inputs to the Random Forest, the classifier learns the deterministic decision boundary induced by the income and spending thresholds used to define the High-Value cohort. Rather than predicting noisy, unobservable real-world human behavior, the classifier's purpose is to bypass re-clustering for new customer profiles. To avoid misleading overconfidence from raw tree votes, we wrapped the model in `CalibratedClassifierCV` with Platt scaling. Sigmoid calibration transforms raw classifier scores into probability estimates intended to be better calibrated, yielding a Brier score loss of 0.00358."

### 28. "How does your test suite verify the pipeline?"
**Answer**:
"The verified, executable test suite contains exactly 32 tests (`pytest tests/test_pipeline.py`), covering data loading, schema validation, non-destructive header normalization, automated K-selection, business rules, Platt calibration probability bounds, non-degenerate batch predictions, and centroid explainability grounding, all of which pass cleanly in 12.23 seconds."

### 29. "Why are Income and Spending Score the primary drivers?"
**Answer**:
"Feature importance analysis confirms that Spending Score (49.4%) and Annual Income (34.6%) together account for 84.0% of classification power. This confirms that the supervised classifier aligns closely with the 2D behavioral segmentation plane, while Age (15.6%) and Gender (0.4%) provide secondary demographic profiling."

### 30. "Why is Streamlit the chosen deployment framework?"
**Answer**:
"The system requires an active Python execution runtime to serve dynamic Plotly visualizations and execute Scikit-Learn machine learning inference models (`joblib`). Streamlit provides an interactive, stateful multi-page Python web application architecture designed for local execution or containerized deployment."

### 31. "How do you explain the distance grounding in your prediction page?"
**Answer**:
"In `pages/2_Predict.py`, when a user enters customer attributes, the system does not present an arbitrary black-box label. It transforms the inputs using the fitted `StandardScaler` and calculates the exact Euclidean distance to every cluster centroid. It displays the ratio between the distance to the assigned centroid and the distance to the next-closest centroid, giving stakeholders a quantitative measure of whether the customer is a core segment member or a borderline case."

### 32. "Why use Joblib instead of Pickle for model serialization?"
**Answer**:
"`joblib.dump` and `joblib.load` are optimized specifically for Python objects containing large internal NumPy arrays, which Scikit-Learn estimators rely on. Joblib uses efficient memory-mapping and compression, resulting in faster disk I/O and lower runtime overhead than standard Python `pickle`."
