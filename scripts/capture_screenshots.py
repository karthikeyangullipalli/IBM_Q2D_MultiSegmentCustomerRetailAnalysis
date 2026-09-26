"""
scripts/capture_screenshots.py
Captures genuine high-resolution screenshots from the running Streamlit application.
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        # 1. Home Page
        print("Navigating to Home...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS_DIR / "1_home.png"), full_page=True)
        print("Captured 1_home.png")

        # 2. Dashboard Page
        print("Navigating to Dashboard...")
        page.goto("http://localhost:8501/Dashboard", wait_until="networkidle", timeout=30000)
        time.sleep(4)
        page.screenshot(path=str(SCREENSHOTS_DIR / "2_dashboard.png"), full_page=True)
        print("Captured 2_dashboard.png")

        # 3. Predict Page (Initial state)
        print("Navigating to Predict...")
        page.goto("http://localhost:8501/Predict", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS_DIR / "3_predict_input.png"), full_page=True)
        print("Captured 3_predict_input.png")

        # 4. Predict Page (Submit Prediction)
        print("Submitting prediction form on Predict page...")
        # Click the "Analyze Customer" submit button
        submit_btn = page.locator("button:has-text('Analyze Customer')")
        if submit_btn.count() > 0:
            submit_btn.first.click()
            time.sleep(3)
            page.screenshot(path=str(SCREENSHOTS_DIR / "4_predict_result.png"), full_page=True)
            print("Captured 4_predict_result.png")

        # 5. Insights Page
        print("Navigating to Insights...")
        page.goto("http://localhost:8501/Insights", wait_until="networkidle", timeout=30000)
        time.sleep(4)
        page.screenshot(path=str(SCREENSHOTS_DIR / "5_insights.png"), full_page=True)
        print("Captured 5_insights.png")

        # 6. Data Explorer Page
        print("Navigating to Data Explorer...")
        page.goto("http://localhost:8501/Data_Explorer", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS_DIR / "6_data_explorer.png"), full_page=True)
        print("Captured 6_data_explorer.png")

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    capture_all()
