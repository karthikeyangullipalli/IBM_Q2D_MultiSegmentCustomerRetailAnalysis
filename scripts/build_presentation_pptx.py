"""
scripts/build_presentation_pptx.py
Generates a presentation-ready 15-slide PowerPoint deck for the
Retail Customer Intelligence project using python-pptx.
"""

from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 widescreen layout

    # Color Palette
    NAVY = RGBColor(0x17, 0x20, 0x33)
    SLATE = RGBColor(0x3B, 0x4A, 0x68)
    COPPER = RGBColor(0xC4, 0x7A, 0x44)
    BG_LIGHT = RGBColor(0xF8, 0xFA, 0xFC)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    DARK_TEXT = RGBColor(0x1E, 0x29, 0x3B)
    MUTED_TEXT = RGBColor(0x64, 0x74, 0x8B)
    IBM_BLUE = RGBColor(0x00, 0x43, 0xCE)
    GREEN = RGBColor(0x10, 0x7C, 0x41)

    blank_layout = prs.slide_layouts[6] # Blank slide

    def add_header(slide, title, category="IBMQ2D INTERNSHIP PROJECT"):
        # Header background banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = IBM_BLUE
        
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def add_card(slide, left, top, width, height, title, content_bullets, accent_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = WHITE
        shape.line.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
        shape.line.width = Pt(1)

        if accent_color:
            accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.12), height)
            accent_bar.fill.solid()
            accent_bar.fill.fore_color.rgb = accent_color
            accent_bar.line.fill.background()

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY

        for b in content_bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"•  {b}"
            p_b.font.size = Pt(11.5)
            p_b.font.color.rgb = DARK_TEXT
            p_b.space_before = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(5.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "IBM SKILLSBUILD INTERNSHIP PROGRAM  |  IBMQ2D TRACK (UG LEVEL 2)"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(0x60, 0xA5, 0xFA)

    p1 = tf1.add_paragraph()
    p1.text = "Retail Customer Intelligence"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_before = Pt(16)

    p2 = tf1.add_paragraph()
    p2.text = "A Machine Learning Prototype for Customer Segmentation and High-Value Shopper Prediction"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = (
        "\n\nStudent Name: Gullipalli Lakshmi Narayana Karthikeyan\n"
        "Roll Number: A24126510017   |   Department: Computer Science and Engineering\n"
        "Institution: ANIL Neerukonda Institute of Technology and Sciences (ANITS)\n"
        "IBM Candidate ID: IBMP3155   |   Date: September 26, 2026"
    )
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
    p3.space_before = Pt(24)

    # -------------------------------------------------------------
    # SLIDE 2: Internship & Project Overview
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Internship Track & Project Foundation")
    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "IBM SkillsBuild / IBMQ2D Track", [
        "Track: UG Level 2 Artificial Intelligence & Machine Learning competition.",
        "Focus: Practical, end-to-end applied AI systems over abstract or theoretical notebooks.",
        "Core Philosophy: Transparent algorithms, reproducible metrics, clean architecture, and rigorous validation.",
        "Candidate Details: Karthikeyan (Roll: A24126510017, IBM ID: IBMP3155), CSE Dept, ANITS."
    ], IBM_BLUE)
    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Project Executive Summary", [
        "Dataset: Kaggle Mall Customer Segmentation (200 records, 5 core features).",
        "Dual Machine Learning Methodology: Unsupervised K-Means clustering + Calibrated Random Forest.",
        "Optimal Cluster Count: Evidence-based selection K = 5 (Silhouette score = 0.5547).",
        "High-Value Cohort: 19.5% of customer base commanding 31.90% of aggregate mall spending.",
        "Interactive Deployment: 5-page Streamlit application verified by 32 automated tests."
    ], NAVY)

    # -------------------------------------------------------------
    # SLIDE 3: Problem Statement & Industrial Need
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Problem Statement: The Retail Marketing Dilemma")
    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "The Core Retail Challenge", [
        "Homogeneous Marketing Trap: Many retailers allocate marketing spend evenly across all shoppers.",
        "Extreme Asymmetry: Spending contribution is highly uneven; treating top spenders and bargain hunters identically creates waste.",
        "Under-Investment: High-margin premium shoppers receive generic promotional noise.",
        "Over-Investment: Budget shoppers receive expensive loyalty discounts that never yield margin."
    ], COPPER)
    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "The Solution Requirements", [
        "Automated Persona Discovery: Segment customer base into actionable behavioral clusters from real income & spend data.",
        "Auditable High-Value Rule: Transparent, explainable threshold identifying top commercial contributors.",
        "Sub-Second Classification: Score brand new customers instantly from basic attributes without re-running K-Means.",
        "Actionable Business Guidance: Map every persona directly to a tailored marketing action."
    ], NAVY)

    # -------------------------------------------------------------
    # SLIDE 4: Project Objectives & Scope
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Project Objectives & Execution Scope")
    add_card(s4, Inches(0.8), Inches(1.8), Inches(3.7), Inches(5.0), "1. Empirical Clustering", [
        "Evaluate K=2..10 using both Inertia and Silhouette Score.",
        "Programmatically maximize silhouette score rather than guessing K.",
        "Standardize features with zero-mean unit-variance scaling."
    ], NAVY)
    add_card(s4, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.0), "2. Calibrated Classifier", [
        "Train 200-tree Random Forest on Age, Gender, Income, Spending Score.",
        "Apply CalibratedClassifierCV (Platt scaling) over 5-fold CV.",
        "Achieve authentic posterior likelihoods instead of extreme 0/1 tree votes."
    ], IBM_BLUE)
    add_card(s4, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.0), "3. Production Web App", [
        "Interactive 5-page Streamlit UI with custom typography and CSS cards.",
        "Dynamic Plotly 2D clustering and silhouette curves.",
        "Zero-exception reliability backed by 32 automated pytest tests."
    ], GREEN)

    # -------------------------------------------------------------
    # SLIDE 5: Dataset & Preprocessing Pipeline
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Dataset Ingestion & Non-Destructive Cleaning")
    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Dataset Characteristics", [
        "Source: Kaggle Mall Customer Segmentation Data.",
        "Dimensions: Exactly 200 rows and 5 attribute columns.",
        "Attributes: CustomerID, Gender (or Genre), Age, Annual Income (k$), Spending Score (1-100).",
        "Data Hygiene: 0 missing values, 0 duplicate IDs, 0 invalid range outliers."
    ], NAVY)
    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Ingestion & Normalization Rules", [
        "Alias Normalization: Non-destructive in-memory mapping translates Kaggle's historical 'Genre' header to 'Gender'.",
        "Strict Domain Validation: Age [18, 70], Income [$15k, $137k], Spending Score [1, 99].",
        "StandardScaler Normalization: Rescales Annual Income and Spending Score for accurate Euclidean distance clustering.",
        "Zero File Mutation: The original CSV on disk is never altered."
    ], IBM_BLUE)

    # -------------------------------------------------------------
    # SLIDE 6: System Architecture Diagram
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Modular Four-Tier System Architecture")
    arch_img = DOCS_DIR / "architecture_diagram.png"
    if arch_img.exists():
        s6.shapes.add_picture(str(arch_img), Inches(0.8), Inches(1.8), Inches(7.2), Inches(5.0))
    add_card(s6, Inches(8.3), Inches(1.8), Inches(4.2), Inches(5.0), "Architectural Principles", [
        "1. Data Layer: Ingests & validates CSV source.",
        "2. Service Core Layer: Modular modules for clustering, persona rules, and classification.",
        "3. Persistence Layer: Joblib caches fitted models and summaries for instant boot.",
        "4. Presentation Layer: 5-page Streamlit interface with zero business logic in UI files."
    ], NAVY)

    # -------------------------------------------------------------
    # SLIDE 7: Unsupervised Segmentation & Optimal K Selection
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Unsupervised Segmentation: Evidence-Based K Selection")
    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Empirical Evaluation (K=2..10)", [
        "K=2: Inertia = 269.69, Silhouette = 0.3213",
        "K=3: Inertia = 157.70, Silhouette = 0.4666",
        "K=4: Inertia = 108.92, Silhouette = 0.4939",
        "K=5 (Optimal): Inertia = 65.57, Silhouette = 0.5547",
        "K=6: Inertia = 55.06, Silhouette = 0.5399",
        "K=7: Inertia = 44.86, Silhouette = 0.5281",
        "K=8: Inertia = 37.23, Silhouette = 0.4552",
        "K=9: Inertia = 32.39, Silhouette = 0.4571",
        "K=10: Inertia = 29.98, Silhouette = 0.4432"
    ], GREEN)
    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Why K = 5 is Defensible", [
        "Silhouette Maximization: K = 5 achieves the global peak silhouette score of 0.5547 across the entire search space.",
        "Diminishing Returns: Increasing K beyond 5 fragments natural clusters without meaningful inertia reduction.",
        "Feature Set Justification: Using Income + Spending yields 0.555 silhouette. Adding Age or Gender degrades score to 0.428.",
        "Automated Selection: Programmatic select_optimal_k() avoids manual guessing."
    ], NAVY)

    # -------------------------------------------------------------
    # SLIDE 8: Discovered Customer Personas
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Customer Personas: Centroid-Based Behavioral Profiling")
    add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "The Five Natural Personas", [
        "Premium Customers (n=39, 19.5%): Avg Income $86.5k, Avg Spend 82.1. Top revenue drivers.",
        "Careful Spenders (n=35, 17.5%): Avg Income $88.3k, Avg Spend 17.1. High income, low engagement.",
        "Standard Customers (n=81, 40.5%): Avg Income $55.3k, Avg Spend 49.5. The broad middle class.",
        "Impulsive Shoppers (n=22, 11.0%): Avg Income $25.7k, Avg Spend 79.4. Low income, heavy spending.",
        "Budget Customers (n=23, 11.5%): Avg Income $26.3k, Avg Spend 20.9. Frugal, price-sensitive shoppers."
    ], NAVY)
    add_card(s8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Actionable Marketing Strategies", [
        "Premium: Exclusive VIP loyalty privileges, early access to new inventory, premium concierge.",
        "Careful Spenders: Trust-building communications, luxury quality messaging, personalized outreach.",
        "Standard: Seasonal promotional calendars, category cross-sell, loyalty tier upgrades.",
        "Impulsive: Flash sales, limited-time countdown promotions, impulse checkout bundles.",
        "Budget: Value bundles, clearance alerts, price-match guarantees."
    ], COPPER)

    # -------------------------------------------------------------
    # SLIDE 9: High-Value Customer Definition
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "High-Value Definition: Auditable & Transparent Rule")
    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "The Ground-Truth High-Value Rule", [
        "Rule Formulation: A cluster is High-Value iff Centroid Income >= Median Income ($61.5k) AND Centroid Spending >= Median Spending (50.0).",
        "Transparent & Auditable: Defensible in a single sentence to executive stakeholders.",
        "Deterministic Target: Grounded in real population medians, not arbitrary scoring thresholds.",
        "Exclusive Qualification: Exactly one persona qualifies — Premium Customers (Cluster 3)."
    ], IBM_BLUE)
    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Disproportionate Commercial Impact", [
        "Cohort Count: 39 customers (19.5% of total base).",
        "Income Share: High-Value customers represent 27.86% of total customer income.",
        "Spending Share: High-Value customers command 31.90% of total store spending volume.",
        "Strategic Justification: Prioritizing loyalty spend on this 19.5% cohort directly protects ~32% of total retail turnover."
    ], GREEN)

    # -------------------------------------------------------------
    # SLIDE 10: Supervised Classification & Platt Calibration
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Supervised Classification & Probability Calibration")
    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Classifier Architecture", [
        "Base Model: RandomForestClassifier(n_estimators=200, random_state=42).",
        "Input Features: Age, Gender (binary encoded), Annual Income (k$), Spending Score (1-100).",
        "Train / Test Partition: 80% train (160 rows), 20% test (40 rows), stratified by High-Value class.",
        "Purpose: Real-time customer inference in milliseconds without re-running K-Means."
    ], NAVY)
    add_card(s10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Why Platt Scaling is Essential", [
        "The Collapse Problem: Because the target is deterministically separable, raw Random Forest tree votes collapse to extreme 0% or 100%.",
        "CalibratedClassifierCV: Wraps the forest with sigmoid (Platt) scaling across 5-fold cross-validation.",
        "Empirical Posterior: Maps decision margins into authentic posterior likelihoods matching empirical outcomes.",
        "Brier Score Loss: Achieves 0.00358, confirming superior calibration accuracy."
    ], IBM_BLUE)

    # -------------------------------------------------------------
    # SLIDE 11: Quantitative Model Evaluation
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Model Performance & Feature Importance")
    add_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Quantitative Test Metrics (40 Test Customers)", [
        "Test Accuracy: 100.0% (40 / 40 correct)",
        "Precision: 1.000  |  Recall: 1.000  |  F1-Score: 1.000",
        "ROC-AUC: 1.000 (Perfect rank separation)",
        "Brier Score Loss: 0.00358 (Calibrated confidence error)",
        "Confusion Matrix: TN=32, FP=0, FN=0, TP=8"
    ], GREEN)
    add_card(s11, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Feature Importance Distribution", [
        "Spending Score (1-100): 49.4% (Primary separator)",
        "Annual Income (k$): 34.6% (Secondary separator)",
        "Age: 15.6% (Demographic discriminator)",
        "Gender: 0.4% (Minimal commercial impact)",
        "Key Finding: Income and Spending drive 84.0% of classification power, validating the 2D clustering design."
    ], NAVY)

    # -------------------------------------------------------------
    # SLIDE 12: Application Architecture & Live UI
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Interactive Streamlit Web Application (5 Pages)")
    dash_img = SCREENSHOTS_DIR / "2_dashboard.png"
    if dash_img.exists():
        s12.shapes.add_picture(str(dash_img), Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))
    add_card(s12, Inches(7.9), Inches(1.8), Inches(4.6), Inches(5.0), "Application Page Overview", [
        "1. Home (app.py): System purpose & headline metrics.",
        "2. Dashboard: 2D customer scatter plot with centroid markers & persona summary cards.",
        "3. Predict: Real-time customer scoring with grounded centroid explanations.",
        "4. Insights: Elbow/silhouette curves, feature importances & business insights.",
        "5. Data Explorer: Multi-column filterable customer database with CSV export."
    ], NAVY)

    # -------------------------------------------------------------
    # SLIDE 13: Live Prediction & Grounded Explainability
    # -------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Live Inference & Grounded Mathematical Reasoning")
    pred_img = SCREENSHOTS_DIR / "4_predict_result.png"
    if pred_img.exists():
        s13.shapes.add_picture(str(pred_img), Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))
    add_card(s13, Inches(7.9), Inches(1.8), Inches(4.6), Inches(5.0), "Explainable AI by Design", [
        "Instant Scoring: Inputs Age, Gender, Income, Spending -> Predicts Persona & High-Value status.",
        "Calibrated Confidence: Reports realistic percentage likelihood rather than raw agreement.",
        "Distance Grounding: Computes Euclidean distance to assigned vs next-closest centroid.",
        "Delta Explanations: Quantifies exact distance from dataset & segment averages."
    ], IBM_BLUE)

    # -------------------------------------------------------------
    # SLIDE 14: Limitations & Academic Transparency
    # -------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Limitations & Academic Transparency")
    add_card(s14, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Honest Disclosure on 100% Accuracy", [
        "Deterministic Target: The High-Value label is derived from cluster centroids defined on Income and Spending.",
        "Accessible Features: Because Income and Spending are also classifier inputs, the model acts as an ultra-fast boundary emulator.",
        "Academically Sound: The 100% score is expected and honest; it does not claim to predict noisy real-world churn.",
        "Platt Scaling Role: Calibration ensures probabilities reflect real uncertainty near decision boundaries."
    ], COPPER)
    add_card(s14, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Data & System Constraints", [
        "Sample Size: 200 customer rows — suitable for proof-of-concept, but lacks seasonal depth.",
        "Feature Dimensions: No transactional logs (basket size, recency, SKU margins).",
        "Single-Tenant Prototype: Local deployment without distributed database persistence.",
        "Production Reality: Real transactional data with noise would typically achieve 80–90% accuracy."
    ], NAVY)

    # -------------------------------------------------------------
    # SLIDE 15: Conclusion & Future Roadmap
    # -------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Conclusion & Future Production Roadmap")
    add_card(s15, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), "Internship Achievements", [
        "Rigorous Methodology: Fully automated K-selection (K=5, Silhouette 0.5547).",
        "Transparent Business Logic: Median-based High-Value definition (19.5% base = 31.9% spend).",
        "Operational Deployment: 5-page Streamlit web application with professional design.",
        "Complete QA Verification: 32 unit and integration tests passing with 100% success."
    ], GREEN)
    add_card(s15, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), "Future Production Roadmap", [
        "Data Warehouse Integration: Direct SQL connector to Snowflake or BigQuery for real-time batch scoring.",
        "Multi-Dimensional RFM: Incorporate purchase recency, basket frequency, and category affinity.",
        "Microservice API: Wrap core inference in FastAPI with Docker containerization.",
        "Automated Retraining: Scheduled Drift detection & automated model recalibration pipeline."
    ], NAVY)

    pptx_out = DOCS_DIR / "presentation.pptx"
    prs.save(str(pptx_out))
    print(f"Successfully generated {pptx_out}")

    # Generate Markdown Summary
    md_out = DOCS_DIR / "presentation.md"
    with open(md_out, "w", encoding="utf-8") as f:
        f.write("# Retail Customer Intelligence — Presentation Deck Summary\n")
        f.write("15 Slides built with python-pptx covering complete project lifecycle.\n")
    print(f"Successfully generated {md_out}")

if __name__ == "__main__":
    create_deck()
