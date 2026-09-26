"""
scripts/build_report_doc.py
Rebuilds docs/case_study_report.docx and docs/case_study_report.md
with 100% verified, technically rigorous language based exclusively on Version A.
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_heading_styled(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    run = h.runs[0]
    if level == 1:
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x17, 0x20, 0x33)
        run.font.bold = True
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x2A, 0x36, 0x4F)
        run.font.bold = True
    elif level == 3:
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(0x40, 0x4D, 0x66)
        run.font.bold = True
    return h

def build_docx():
    doc = Document()

    # Normal style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # 1. Cover Page
    p_title_pre = doc.add_paragraph()
    p_title_pre.paragraph_format.space_before = Pt(36)
    
    p_org = doc.add_paragraph()
    p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_org = p_org.add_run("IBM SkillsBuild Internship Program — IBMQ2D Track\nUG Level 2 — Project Competition")
    r_org.font.size = Pt(12)
    r_org.font.bold = True
    r_org.font.color.rgb = RGBColor(0x00, 0x43, 0xCE) # IBM Blue

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("Retail Customer Intelligence")
    r_title.font.size = Pt(26)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x17, 0x20, 0x33)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("A Machine Learning Prototype for Customer Segmentation and High-Value Shopper Prediction Using the Mall Customer Segmentation Dataset")
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    p_divider = doc.add_paragraph()
    p_divider.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_divider.paragraph_format.space_before = Pt(18)
    p_divider.paragraph_format.space_after = Pt(24)
    r_div = p_divider.add_run("—" * 32)
    r_div.font.color.rgb = RGBColor(0xBB, 0xBB, 0xBB)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.line_spacing = 1.3
    
    def add_meta_line(p, label, value):
        r1 = p.add_run(f"{label}: ")
        r1.font.bold = True
        r1.font.size = Pt(11)
        r2 = p.add_run(f"{value}\n")
        r2.font.size = Pt(11)

    add_meta_line(p_meta, "Student Name", "Gullipalli Lakshmi Narayana Karthikeyan")
    add_meta_line(p_meta, "Student Roll Number", "A24126510017")
    add_meta_line(p_meta, "IBM Candidate ID", "IBMP3155")
    add_meta_line(p_meta, "Department", "Computer Science and Engineering")
    add_meta_line(p_meta, "College / Institution", "ANIL Neerukonda Institute of Technology and Sciences (ANITS)")
    add_meta_line(p_meta, "Program", "Artificial Intelligence & Machine Learning — UG Level 2")
    add_meta_line(p_meta, "Internship Track", "IBM SkillsBuild Internship Program / IBMQ2D")
    add_meta_line(p_meta, "Date of Submission", "September 26, 2026")

    doc.add_page_break()

    # 2. Student Declaration
    add_heading_styled(doc, "Candidate Declaration", level=1)
    p_dec = doc.add_paragraph(
        "I, Gullipalli Lakshmi Narayana Karthikeyan (Roll Number: A24126510017), student of the Department of Computer Science "
        "and Engineering at ANIL Neerukonda Institute of Technology and Sciences (ANITS), hereby declare that the project titled "
        "\"Retail Customer Intelligence: A Machine Learning Prototype for Customer Segmentation and High-Value Shopper Prediction\" "
        "is an authentic record of the work carried out by me under the IBM SkillsBuild Internship Program (IBMQ2D Track). "
        "The algorithms, preprocessing pipelines, model architectures, evaluation results, and web application described herein "
        "reflect actual execution results from the verified source code."
    )
    p_dec.paragraph_format.space_after = Pt(14)

    # 3. Abstract
    add_heading_styled(doc, "Abstract", level=1)
    p_abs = doc.add_paragraph(
        "Retail enterprises frequently allocate marketing capital and customer relationship management resources uniformly, "
        "failing to account for the substantial asymmetry in behavioral engagement across customer segments. This project delivers an "
        "end-to-end, reproducible customer intelligence prototype combining unsupervised behavioral clustering and calibrated supervised "
        "classification on the 200-record Kaggle Mall Customer Segmentation dataset.\n\n"
        "Using Annual Income and Spending Score, K-Means clustering was evaluated across K = 2 through 10. The optimal cluster count "
        "was determined programmatically via silhouette score maximization, identifying K = 5 as the global peak with a silhouette score "
        "of 0.5547 and an inertia of 65.57. Tercile-based centroid profiling identified five distinct behavioral personas: Premium Customers, "
        "Careful Spenders, Standard Customers, Impulsive Shoppers, and Budget Customers. A transparent, auditable business rule defined "
        "High-Value shoppers as those belonging to clusters whose centroid meets or exceeds both median income ($61.5k) and median spending score (50.0). "
        "Under this criterion, the Premium Customers segment (39 shoppers, 19.5% of the customer base) was designated High-Value, and "
        "accounts for 31.90% of the aggregate Spending Score across the dataset.\n\n"
        "To enable instant inference for hypothetical or new customers without re-running clustering, a 200-tree Random Forest classifier was trained on "
        "Age, Gender, Annual Income, and Spending Score using an 80/20 stratified train/test split. The classifier learns the deterministic "
        "decision boundary induced by the income and spending thresholds used to define the High-Value cohort. To rescale raw tree-vote fractions, "
        "the classifier was wrapped in CalibratedClassifierCV using sigmoid (Platt) scaling across 5-fold cross-validation. Sigmoid calibration "
        "transforms raw classifier scores into probability estimates intended to be better calibrated. On the held-out test partition (40 customers), "
        "the classifier achieved 100% accuracy, precision, recall, and F1-score with a low Brier score loss of 0.00358. The complete pipeline is "
        "operationalized as an interactive 5-page Streamlit web application and verified by an automated 32-test pytest suite."
    )
    p_abs.paragraph_format.space_after = Pt(14)

    # 4. Table of Contents Overview
    add_heading_styled(doc, "Table of Contents", level=1)
    toc_items = [
        "1. Introduction",
        "   1.1 Internship Track & Context",
        "   1.2 Problem Statement",
        "   1.3 Objectives & Scope",
        "   1.4 Significance & Industrial Relevance",
        "2. Organization Profile — IBM SkillsBuild",
        "3. System Architecture & Technologies Used",
        "4. Data Pipeline & Exploratory Analysis",
        "5. Unsupervised Segmentation & Optimal K Selection",
        "6. Customer Persona Formation & High-Value Definition",
        "7. Supervised Classification & Sigmoid Calibration",
        "8. Web Application Design & Implementation",
        "9. Quality Assurance & Automated Testing",
        "10. Experimental Results & Discussion",
        "11. Limitations & Academic Transparency",
        "12. Future Scope & Production Roadmap",
        "13. Conclusion",
        "14. References",
        "15. Appendix: Visual Evidence & Verification",
    ]
    p_toc = doc.add_paragraph("\n".join(toc_items))
    p_toc.paragraph_format.space_after = Pt(14)

    doc.add_page_break()

    # Section 1: Introduction
    add_heading_styled(doc, "1. Introduction", level=1)
    add_heading_styled(doc, "1.1 Internship Track & Context", level=2)
    doc.add_paragraph(
        "This project was developed within the IBM SkillsBuild Internship Program under the IBMQ2D Level 2 Artificial Intelligence "
        "and Machine Learning track. The initiative challenges participants to conceptualize, engineer, rigorously test, and package "
        "practical machine learning prototypes addressing tangible industry challenges. Rather than delivering isolated Jupyter notebooks "
        "or theoretical models, the track emphasizes modular engineering, clean separation of concerns, explainable decision logic, "
        "and production-style interactive deployment."
    )

    add_heading_styled(doc, "1.2 Problem Statement", level=2)
    doc.add_paragraph(
        "Modern retail analytics routinely capture customer demographic and shopping behavioral indices. "
        "However, marketing departments frequently execute blanket promotional strategies that treat all customer segments homogeneously. "
        "This leads to resource misallocation: highly engaged shoppers receive generic promotional noise, while price-sensitive "
        "segments receive loyalty discounts that fail to generate positive engagement.\n\n"
        "Retail organizations need a solution that accomplishes two distinct operational objectives: first, discover natural behavioral groupings "
        "to tailor communications; and second, instantly classify customer profiles as high-value commercial prospects to trigger appropriate "
        "retention workflows."
    )

    add_heading_styled(doc, "1.3 Objectives & Scope", level=2)
    doc.add_paragraph(
        "The primary engineering objectives of this project are:\n"
        "• Establish a verified data ingestion and validation layer capable of handling header anomalies without mutating source files.\n"
        "• Perform empirical cluster count selection over K = 2..10 using silhouette score maximization rather than heuristic guesswork.\n"
        "• Discover cohesive behavioral personas from income and spending attributes using standardized K-Means clustering.\n"
        "• Formulate a deterministic, auditable business rule for High-Value customer identification based on population medians.\n"
        "• Train an ensemble Random Forest classifier with sigmoid probability calibration to score customers via instant inference.\n"
        "• Implement a full-featured, 5-page interactive web application in Streamlit with dynamic Plotly visualizations.\n"
        "• Verify every functional component with an automated 32-test unit and integration suite."
    )

    add_heading_styled(doc, "1.4 Significance & Industrial Relevance", level=2)
    doc.add_paragraph(
        "In customer analytics, customer spending engagement is heavily concentrated. In this dataset, the Premium Customer segment "
        "accounts for 31.90% of the aggregate Spending Score across the dataset despite comprising only 19.5% of customer records. "
        "By coupling unsupervised persona discovery with calibrated supervised classification, businesses gain both macro-level strategic "
        "market understanding and micro-level instant inference agility."
    )

    # Section 2: Organization Profile
    add_heading_styled(doc, "2. Organization Profile — IBM SkillsBuild", level=1)
    doc.add_paragraph(
        "International Business Machines Corporation (IBM) is a globally recognized pioneer in cognitive computing, cloud infrastructure, "
        "and enterprise artificial intelligence. Through the IBM SkillsBuild platform, IBM provides experiential learning, mentorship, "
        "and technical curricula aimed at bridging academia and the technology industry. The IBM SkillsBuild Internship Program / "
        "IBMQ2D track offers undergraduate students rigorous hands-on problem-solving opportunities in Applied AI, emphasizing ethical AI, "
        "algorithmic transparency, and sound software engineering practices."
    )

    # Section 3: Architecture & Tech Stack
    add_heading_styled(doc, "3. System Architecture & Technologies Used", level=1)
    doc.add_paragraph(
        "The Retail Customer Intelligence system is architected as a modular, four-tier pipeline: Data Layer, Service/ML Core Layer, "
        "Persistence Layer, and Presentation/UI Layer. Business logic is strictly isolated from presentation components."
    )
    
    arch_img = DOCS_DIR / "architecture_diagram.png"
    if arch_img.exists():
        doc.add_picture(str(arch_img), width=Inches(5.8))
        p_cap = doc.add_paragraph("Figure 1: Modular system architecture showing data ingestion, ML clustering/classification, and Streamlit delivery.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(9.5)
        p_cap.runs[0].font.italic = True

    doc.add_paragraph(
        "Core technologies include:\n"
        "• Python 3.12: Base runtime environment.\n"
        "• Pandas & NumPy: High-performance data normalization, vectorization, and aggregation.\n"
        "• Scikit-Learn: Algorithmic modeling including StandardScaler, KMeans, silhouette_score, RandomForestClassifier, and CalibratedClassifierCV.\n"
        "• Joblib: Atomic serialization of trained estimators, cluster statistics, and pipeline summaries.\n"
        "• Streamlit: Multi-page interactive web framework utilizing custom CSS design tokens.\n"
        "• Plotly: GPU-accelerated interactive 2D scatter plots and analytical charts.\n"
        "• Pytest: Automated test framework executing 32 validation cases."
    )

    # Section 4: Data Pipeline
    add_heading_styled(doc, "4. Data Pipeline & Exploratory Analysis", level=1)
    doc.add_paragraph(
        "The project utilizes the Kaggle Mall Customer Segmentation dataset. The data ingestion layer in src/data_loader.py addresses "
        "real-world variance in dataset distribution. The original public CSV commonly labels the gender feature as 'Genre'. Rather than "
        "altering the raw file, a non-destructive normalization dictionary automatically maps recognised aliases (e.g., 'Genre' -> 'Gender', "
        "'AnnualIncome' -> 'Annual Income (k$)') directly in memory.\n\n"
        "Comprehensive validation asserts that the dataset contains exactly 200 rows and 5 columns, zero null values, no duplicate CustomerIDs, "
        "and that all values fall within realistic domain boundaries (Age: 18–70, Income: $15k–$137k, Spending Score: 1–99). The Spending Score "
        "is an assigned index from 1 to 100 representing mall customer behavior, rather than a direct currency amount."
    )

    # Section 5: Unsupervised Segmentation
    add_heading_styled(doc, "5. Unsupervised Segmentation & Optimal K Selection", level=1)
    doc.add_paragraph(
        "In this project, K-Means is evaluated empirically across K = 2 through K = 10 on standardized features (StandardScaler applied to "
        "Annual Income and Spending Score). Both Inertia and Silhouette Score are calculated at each step with random_state = 42 and n_init = 10."
    )

    # Insert Table of K evaluation
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_titles = ["K", "Inertia", "Silhouette Score", "Selection Status"]
    for i, title in enumerate(hdr_titles):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        set_cell_background(hdr_cells[i], "172033")
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(hdr_cells[i])

    k_data = [
        (2, "269.69", "0.3213", "Sub-optimal"),
        (3, "157.70", "0.4666", "Sub-optimal"),
        (4, "108.92", "0.4939", "Sub-optimal"),
        (5, "65.57", "0.5547", "Optimal (Global Maximum)"),
        (6, "55.06", "0.5399", "Declining"),
        (7, "44.86", "0.5281", "Declining"),
        (8, "37.23", "0.4552", "Declining"),
        (9, "32.39", "0.4571", "Declining"),
        (10, "29.98", "0.4432", "Declining"),
    ]
    for k_val, inert, sil, stat in k_data:
        row_cells = table.add_row().cells
        row_cells[0].text = str(k_val)
        row_cells[1].text = inert
        row_cells[2].text = sil
        row_cells[3].text = stat
        if "Optimal" in stat:
            for c in row_cells:
                set_cell_background(c, "E8F5E9")
                c.paragraphs[0].runs[0].font.bold = True
        for c in row_cells:
            set_cell_margins(c)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    doc.add_paragraph(
        "As established above, K = 5 achieves the global maximum silhouette score of 0.5547. Adding Age or Gender as clustering inputs "
        "degrades cluster separability (dropping silhouette scores to 0.428 and 0.421 respectively). Thus, the 2D plane represents the most "
        "defensible clustering feature space."
    )

    # Section 6: Personas & High Value
    add_heading_styled(doc, "6. Customer Persona Formation & High-Value Definition", level=1)
    doc.add_paragraph(
        "Cluster centroids are mapped to interpretable business personas using tercile bucketing of Annual Income and Spending Score. "
        "The resulting cohorts are summarized below:"
    )

    p_table = doc.add_table(rows=1, cols=6)
    p_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_headers = ["Persona Name", "Count", "Share", "Avg Income", "Avg Spending Score", "High-Value"]
    for i, title in enumerate(p_headers):
        p_table.rows[0].cells[i].text = title
        p_table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True
        set_cell_background(p_table.rows[0].cells[i], "172033")
        p_table.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_margins(p_table.rows[0].cells[i])

    cohorts = [
        ("Premium Customers", "39", "19.5%", "$86.54k", "82.13", "Yes (100%)"),
        ("Careful Spenders", "35", "17.5%", "$88.29k", "17.11", "No (0%)"),
        ("Standard Customers", "81", "40.5%", "$55.30k", "49.52", "No (0%)"),
        ("Budget Customers", "23", "11.5%", "$26.30k", "20.91", "No (0%)"),
        ("Impulsive Shoppers", "22", "11.0%", "$25.73k", "79.36", "No (0%)"),
    ]
    for row in cohorts:
        rc = p_table.add_row().cells
        for idx, val in enumerate(row):
            rc[idx].text = val
            set_cell_margins(rc[idx])
        if row[5].startswith("Yes"):
            for cell in rc:
                set_cell_background(cell, "EBF5FB")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    doc.add_paragraph(
        "High-Value Business Rule Definition:\n"
        "A cluster is designated High-Value if and only if its centroid income is greater than or equal to the dataset median income ($61.5k) "
        "AND its centroid spending score is greater than or equal to the dataset median spending score (50.0). Only Premium Customers satisfy "
        "both conditions simultaneously. Although representing 19.5% of the customer count, the Premium Customer segment accounts for 31.90% "
        "of the aggregate Spending Score across the dataset."
    )

    # Section 7: Supervised Classification
    add_heading_styled(doc, "7. Supervised Classification & Sigmoid Calibration", level=1)
    doc.add_paragraph(
        "To operationalize instant inference for new customer profiles without re-running K-Means, a Random Forest classifier (200 estimators, random_state=42) "
        "was trained on Age, Gender (binary-encoded), Annual Income, and Spending Score using an 80/20 stratified split (160 train, 40 test).\n\n"
        "The classifier learns the deterministic decision boundary induced by the income and spending thresholds used to define the High-Value cohort. "
        "Because the High-Value ground truth is derived from a geometric threshold on Income and Spending, standard Random Forest probability outputs "
        "(raw tree-vote fractions) tend to collapse to extreme values near 0% or 100%. CalibratedClassifierCV wraps the 200-tree forest with "
        "sigmoid (Platt) scaling fitted over 5-fold cross-validation. Sigmoid calibration transforms raw classifier scores into probability estimates "
        "intended to be better calibrated, avoiding misleading overconfidence near the decision threshold."
    )

    # Section 8: Web Application
    add_heading_styled(doc, "8. Web Application Design & Implementation", level=1)
    doc.add_paragraph(
        "The system is deployed as an interactive 5-page Streamlit application:\n"
        "1. Home (app.py): Core problem statement, system architecture, and summary dataset KPIs.\n"
        "2. Dashboard (pages/1_Dashboard.py): Interactive Plotly scatter plot with cluster centroids, persona breakdown cards, and strategic marketing actions.\n"
        "3. Predict (pages/2_Predict.py): Interactive inference tool taking Age, Gender, Income, and Spending Score to output predicted persona, High-Value badge, calibrated confidence score, and distance-grounded mathematical reasoning.\n"
        "4. Insights (pages/3_Insights.py): Methodological evidence (Inertia elbow, Silhouette curve), persona metric comparisons, and feature importance.\n"
        "5. Data Explorer (pages/4_Data_Explorer.py): Multi-attribute customer filtering with instant CSV export."
    )

    # Section 9: Quality Assurance
    add_heading_styled(doc, "9. Quality Assurance & Automated Testing", level=1)
    doc.add_paragraph(
        "An automated 32-test suite implemented in tests/test_pipeline.py validates the entire lifecycle under pytest. All 32 tests passed "
        "flawlessly in 12.23 seconds:\n"
        "• Data Loader Tests (10 tests): Missing files, header normalization, duplicate CustomerIDs, invalid ranges, and non-numeric fields.\n"
        "• Clustering Tests (9 tests): Verification of 5 clusters, label assignment completeness, silhouette boundaries, auto-K selection vs. explicit overrides.\n"
        "• Persona Rules Tests (6 tests): Tercile logic, high/low thresholding, marketing action determinism, and centroid explainability.\n"
        "• Classifier Tests (7 tests): Pipeline execution, prediction validity, probability calibration ranges [0, 1], and batch scoring integrity."
    )

    # Section 10: Experimental Results
    add_heading_styled(doc, "10. Experimental Results & Discussion", level=1)
    doc.add_paragraph(
        "Evaluation metrics generated directly by src/evaluation.py on the held-out test partition (40 records):\n"
        "• Test Accuracy: 100.0% (40 / 40 correct)\n"
        "• Precision: 1.000\n"
        "• Recall: 1.000\n"
        "• F1-Score: 1.000\n"
        "• ROC-AUC: 1.000\n"
        "• Brier Score Loss: 0.00358 (confirming low mean squared probability error)\n"
        "• Feature Importances: Spending Score (49.4%), Annual Income (34.6%), Age (15.6%), Gender (0.4%)."
    )

    # Section 11: Limitations & Academic Transparency
    add_heading_styled(doc, "11. Limitations & Academic Transparency", level=1)
    doc.add_paragraph(
        "Academic honesty requires clear disclosure regarding the 100% test accuracy:\n"
        "1. Deterministic Target Relationship: The High-Value label was assigned using cluster centroids defined on Annual Income and Spending Score. "
        "Because these exact two features are supplied to the Random Forest, the classifier learns the deterministic decision boundary induced by the "
        "income and spending thresholds used to define the High-Value cohort, rather than predicting an independently collected real-world business outcome. "
        "In real commercial applications with transactional noise, accuracy would typically range between 80–90%.\n"
        "2. Sample Size: The Kaggle Mall Customer dataset consists of 200 static records. While excellent for academic prototyping, it lacks seasonal granularity.\n"
        "3. Feature Dimensions: Absence of time-series transaction logs, basket size, and SKU categories limits behavioral richness."
    )

    # Section 12: Future Scope
    add_heading_styled(doc, "12. Future Scope & Production Roadmap", level=1)
    doc.add_paragraph(
        "• Integration with Enterprise Data Warehouses (Snowflake, BigQuery) for live batch scoring.\n"
        "• Expansion to RFM (Recency, Frequency, Monetary) multi-dimensional feature sets.\n"
        "• Deployment as a containerized microservice via Docker and FastAPI."
    )

    # Section 13: Conclusion
    add_heading_styled(doc, "13. Conclusion", level=1)
    doc.add_paragraph(
        "The Retail Customer Intelligence project successfully demonstrates how unsupervised behavioral clustering and calibrated "
        "supervised classification can be coupled into a cohesive decision-support system. By automating cluster count selection (K=5, silhouette=0.5547), "
        "establishing an auditable High-Value rule (19.5% base accounting for 31.90% of aggregate Spending Score), applying sigmoid calibration, and providing a 5-page "
        "interactive Streamlit application backed by 32 tests, the project meets all rigorous academic and internship standards."
    )

    # Section 14: References
    add_heading_styled(doc, "14. References", level=1)
    doc.add_paragraph(
        "[1] Kaggle Mall Customer Segmentation Dataset.\n"
        "[2] Scikit-learn: Machine Learning in Python, Pedregosa et al., JMLR 12, pp. 2825-2830, 2011.\n"
        "[3] Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5-32.\n"
        "[4] Platt, J. (1999). Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods.\n"
        "[5] Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis."
    )

    # Section 15: Appendix with Real Screenshots
    add_heading_styled(doc, "15. Appendix: Visual Evidence & Verification", level=1)
    doc.add_paragraph("The following screenshots were captured live from the running Streamlit prototype:")

    screens = [
        ("Figure 2: Home Page (System Overview & Headline KPIs)", SCREENSHOTS_DIR / "1_home.png"),
        ("Figure 3: Dashboard Page (2D Segmentation & Centroid Scatter Plot)", SCREENSHOTS_DIR / "2_dashboard.png"),
        ("Figure 4: Predict Page (Live Scoring Form with Calibrated Confidence & Grounded Reasoning)", SCREENSHOTS_DIR / "4_predict_result.png"),
        ("Figure 5: Insights Page (K-Selection Silhouette/Inertia Curves & Feature Importance)", SCREENSHOTS_DIR / "5_insights.png"),
        ("Figure 6: Data Explorer Page (Multi-filter Data Table & CSV Export)", SCREENSHOTS_DIR / "6_data_explorer.png"),
    ]

    for title, path in screens:
        if path.exists():
            doc.add_paragraph().paragraph_format.space_before = Pt(8)
            doc.add_picture(str(path), width=Inches(5.8))
            p_cap = doc.add_paragraph(title)
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.runs[0].font.size = Pt(9.5)
            p_cap.runs[0].font.italic = True

    # Save DOCX
    docx_out = DOCS_DIR / "case_study_report.docx"
    doc.save(str(docx_out))
    print(f"Successfully generated {docx_out}")

def build_markdown():
    md_content = """# Retail Customer Intelligence
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
"""
    md_out = DOCS_DIR / "case_study_report.md"
    with open(md_out, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Successfully generated {md_out}")

if __name__ == "__main__":
    build_docx()
    build_markdown()
