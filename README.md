# Retail Customer Intelligence

IBMQ2D Project Competition — UG Level 2 (AIML) — individual submission.

Segments mall customers into buying personas with K-Means clustering (cluster
count chosen automatically by evaluating K=2 through K=10, not assumed), applies
a transparent, documented rule to flag High-Value customers, and trains a
calibrated Random Forest classifier so new customers can be scored instantly
from Age, Gender, Annual Income, and Spending Score alone — without re-running
clustering.

**Dataset**: Kaggle Mall Customer Segmentation Data
(`data/mall_customers.csv` — 200 rows: CustomerID, Gender, Age, Annual Income
(k$), Spending Score (1-100)). The loader also accepts the original dataset's
"Genre" column header and other common naming variants, normalizing them
internally without modifying the source file.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Models train automatically on first run
(a few seconds) and are cached in `models/` after that.

## Pages

- **Home** — problem statement + headline KPIs
- **Dashboard** — segmentation scatter plot with cluster centroids, persona
  breakdown cards (count, share, averages, High-Value rate, interpretation,
  strategy), and a raw-data expander
- **Predict** — the primary demo page: enter a hypothetical customer, click
  Analyze Customer, and see predicted persona, High-Value status, a
  calibrated confidence score, a deterministic marketing recommendation, and
  a "Why this prediction" explanation grounded in real centroid distances
- **Insights** — cluster-selection evidence (K vs Inertia, K vs Silhouette),
  persona comparison charts, classifier feature importance, High-Value
  analytics, and deterministic business insights
- **Data Explorer** — filter customers by persona/gender/age/income/spending
  and export the filtered result as CSV

## How it works

1. `src/data_loader.py` loads, normalizes column-name variants, and validates
   `data/mall_customers.csv` (missing values, duplicate CustomerIDs,
   unexpected values, invalid ranges)
2. `src/clustering.py` evaluates K=2..10 by silhouette score
   (`evaluate_k_range` / `select_optimal_k`), fits K-Means on Annual Income +
   Spending Score at the selected K, names each cluster a persona from its
   centroid, flags "High-Value" clusters (median income AND median spending
   or above), and grounds prediction explanations in real centroid distances
   (`explain_cluster_assignment`)
3. `src/classifier.py` trains a Random Forest, wrapped in
   `CalibratedClassifierCV` (sigmoid/Platt scaling), on Age/Gender/Income/
   Spending to predict the High-Value label directly — new customers get
   scored without re-running K-Means, and the reported probability is a
   genuine calibrated likelihood, not a raw tree-vote fraction
4. `src/persona_rules.py` holds every business rule as a maintainable,
   auditable function: persona naming, the High-Value rule, marketing
   recommendations, and deterministic business-insight generation
5. `src/utils.py` wires the pipeline together and persists both models with
   `joblib`
6. `src/theme.py` is the single source of truth for the color palette and
   injected CSS so every page stays visually consistent

## Tests

```bash
pytest tests/test_pipeline.py -v
```

32 tests covering: data loading and validation (including the dataset's
"Genre" column alias, duplicate CustomerIDs, invalid values), automatic
K-selection, clustering correctness, persona/business-rule logic, classifier
training and calibration, prediction validity, and explainability grounding.

## Project status

Complete: 5-page Streamlit application (Home, Dashboard, Predict, Insights,
Data Explorer), evidence-based cluster count selection, calibrated
classifier, CSV export, and a professional design system (Inter typography,
navy/slate/copper palette, no emojis). Passing a 32-test pytest suite and a
scripted Streamlit integration test across all 5 pages with zero runtime
exceptions, including live form submission and filter interaction.
