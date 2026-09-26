"""
theme.py
--------
Shared design system for the Streamlit UI: the professional color
palette, typography, and a single injectable CSS block so every page
(app.py and everything in pages/) looks consistent without duplicating
styling code. Deliberately avoids gradients, glassmorphism, drop shadows
beyond a hairline, and any emoji glyphs — see inject_theme_css().
"""

import streamlit as st

COLORS = {
    "background": "#F7F8FA",
    "primary": "#172033",     # Deep Navy — headings, primary text, primary persona
    "secondary": "#3B4A68",   # Secondary Slate
    "accent": "#C47A44",      # Muted Copper — interactive accents
    "success": "#2F6B5F",     # High-Value / success indicator only
    "border": "#E2E5EA",
    "card": "#FFFFFF",
    "text_secondary": "#5B6472",
    "text_muted": "#8A94A6",
    "danger": "#8C4A4A",
}

FONT_IMPORT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"


def inject_theme_css() -> None:
    """Call once near the top of every page (app.py and each pages/ file)."""
    st.markdown(
        f"""
        <style>
        @import url('{FONT_IMPORT_URL}');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .stApp {{
            background-color: {COLORS['background']};
        }}

        h1, h2, h3, h4 {{
            color: {COLORS['primary']} !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }}

        h1 {{ font-size: 1.7rem !important; }}
        h2 {{ font-size: 1.25rem !important; }}
        h3 {{ font-size: 1.05rem !important; }}

        p, li, span, label, div {{
            color: {COLORS['primary']};
        }}

        .app-subtitle {{
            color: {COLORS['text_secondary']};
            font-size: 0.95rem;
            margin-top: -0.6rem;
            margin-bottom: 1.2rem;
        }}

        .section-label {{
            color: {COLORS['text_muted']};
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }}

        /* Metric cards */
        [data-testid="stMetric"] {{
            background-color: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 1rem 1.1rem;
        }}
        [data-testid="stMetricLabel"] {{
            color: {COLORS['text_secondary']} !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {COLORS['primary']} !important;
            font-weight: 700 !important;
        }}

        /* Buttons */
        .stButton > button, .stFormSubmitButton > button {{
            background-color: {COLORS['primary']};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            padding: 0.55rem 1.2rem;
            transition: background-color 0.15s ease;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            background-color: {COLORS['secondary']};
            color: #FFFFFF;
        }}

        /* Generic card container used across pages */
        .ui-card {{
            background-color: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 0.9rem;
        }}

        .ui-badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .ui-divider {{
            border: none;
            border-top: 1px solid {COLORS['border']};
            margin: 1.1rem 0;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {COLORS['card']};
            border-right: 1px solid {COLORS['border']};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def persona_color(persona: str) -> str:
    from src.persona_rules import DEFAULT_PERSONA_COLOR, PERSONA_COLORS
    return PERSONA_COLORS.get(persona, DEFAULT_PERSONA_COLOR)
