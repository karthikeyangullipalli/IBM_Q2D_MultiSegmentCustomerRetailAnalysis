"""
persona_rules.py
-----------------
Business rules for turning cluster centroids into human-readable persona
names, deciding which personas count as "High-Value", mapping each
persona to a recommended marketing action, and deriving deterministic,
data-driven business insights from the actual computed persona summary.
Kept rule-based (not learned, not LLM-generated) so the logic stays
transparent, reproducible, and auditable.
"""

from typing import Dict, List

import pandas as pd

PERSONA_ACTIONS = {
    "Premium Customers": (
        "Highest income and spending. Prioritize for loyalty programs, "
        "early access to new inventory, and premium upsells."
    ),
    "Careful Spenders": (
        "High income but below-average spending. Build trust with "
        "quality-led messaging and personalized outreach to unlock "
        "unrealized spend."
    ),
    "Aspirational Shoppers": (
        "Mid income but high spending. Engage with loyalty rewards and "
        "bundle offers that reward above-average engagement."
    ),
    "Standard Customers": (
        "Average income and spending. Maintain with regular seasonal "
        "promotions and monitor for movement into a higher-value segment."
    ),
    "Impulsive Shoppers": (
        "Lower income but high spending. Target with flash sales and "
        "limited-time offers that convert their spending impulse."
    ),
    "Budget Customers": (
        "Lower income and spending. Lowest priority for premium "
        "campaigns; target with value bundles and discount-led offers."
    ),
}

# Single source of truth for persona colors so every Streamlit page stays
# visually consistent. Palette is the muted, professional business-
# analytics set (navy / slate / copper / earth tones) rather than bright
# startup colors — deliberately excludes the Success Green reserved for
# High-Value status indicators, so that color keeps one consistent meaning
# everywhere it appears.
PERSONA_COLORS = {
    "Premium Customers": "#172033",
    "Standard Customers": "#3B4A68",
    "Careful Spenders": "#C47A44",
    "Impulsive Shoppers": "#6B7A8F",
    "Budget Customers": "#8C7A6B",
    "Aspirational Shoppers": "#A68A5B",
}

DEFAULT_PERSONA_COLOR = "#6B7280"


def _bucket(value: float, terciles: List[float]) -> str:
    """Classify `value` as Low/Mid/High against a [t1, t2] tercile split."""
    t1, t2 = terciles
    if value <= t1:
        return "Low"
    if value <= t2:
        return "Mid"
    return "High"


def name_persona(
    avg_income: float,
    avg_spending: float,
    income_terciles: List[float],
    spending_terciles: List[float],
) -> str:
    """
    Assign a human-readable persona name to a cluster centroid by bucketing
    its average income and spending score into Low/Mid/High tiers (relative
    to the overall dataset's terciles) and mapping the combination to a name.
    """
    income_tier = _bucket(avg_income, income_terciles)
    spending_tier = _bucket(avg_spending, spending_terciles)

    mapping = {
        ("High", "High"): "Premium Customers",
        ("High", "Mid"): "Careful Spenders",
        ("High", "Low"): "Careful Spenders",
        ("Mid", "High"): "Aspirational Shoppers",
        ("Mid", "Mid"): "Standard Customers",
        ("Mid", "Low"): "Standard Customers",
        ("Low", "High"): "Impulsive Shoppers",
        ("Low", "Mid"): "Budget Customers",
        ("Low", "Low"): "Budget Customers",
    }
    return mapping[(income_tier, spending_tier)]


def is_high_value(
    avg_income: float,
    avg_spending: float,
    median_income: float,
    median_spending: float,
) -> bool:
    """
    Business rule (documented in the report methodology): a cluster is
    "High-Value" if its centroid sits at or above the dataset median on
    BOTH annual income and spending score.
    """
    return avg_income >= median_income and avg_spending >= median_spending


PERSONA_INTERPRETATIONS = {
    "Premium Customers": (
        "Customers who both earn well and spend actively at the mall — "
        "the core commercial driver of the business."
    ),
    "Careful Spenders": (
        "Customers with strong earning power but cautious spending — "
        "value is present in this segment but not yet captured."
    ),
    "Aspirational Shoppers": (
        "Customers who spend more than their income alone would predict — "
        "highly engaged but income-constrained."
    ),
    "Standard Customers": (
        "Customers with income and spending close to the overall average — "
        "the broad middle of the customer base."
    ),
    "Impulsive Shoppers": (
        "Customers who spend heavily relative to their income — engaged, "
        "but with a lower revenue ceiling than income-driven segments."
    ),
    "Budget Customers": (
        "Customers with both limited income and limited spending — "
        "the lowest current commercial value segment."
    ),
}


def get_persona_interpretation(persona_name: str) -> str:
    return PERSONA_INTERPRETATIONS.get(
        persona_name, "No interpretation defined for this persona."
    )


def get_marketing_action(persona_name: str) -> str:
    return PERSONA_ACTIONS.get(
        persona_name, "No recommended action defined for this persona."
    )


def _age_channel_note(age: int) -> str:
    """Deterministic, rule-based channel guidance by age band — one of the
    concrete factors (age) the recommendation is required to consider."""
    if age < 30:
        return "Younger profile: digital and social-first channels are likely most effective."
    if age < 50:
        return "Mid-career profile: email and app push notifications are a reasonable primary channel."
    return "Older profile: in-store engagement and direct contact typically outperform app-only outreach."


def generate_marketing_recommendation(
    persona: str, age: int, income: float, spending: float, high_value: bool
) -> str:
    """
    Deterministic, explainable marketing recommendation combining the
    persona-level action with a rule-based channel note derived from age.
    No LLM text generation — every sentence traces back to a fixed rule.
    """
    base = get_marketing_action(persona)
    channel = _age_channel_note(int(age))
    urgency = (
        " This customer already meets the High-Value criteria, so treat outreach as a retention priority."
        if high_value
        else ""
    )
    return f"{base} {channel}{urgency}"


def generate_business_insights(persona_summary: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Derive deterministic, data-driven business insight statements from the
    actual computed persona summary (avg_income, avg_spending, avg_age,
    count, pct_high_value per persona). No generic marketing copy — every
    statement is computed directly from the numbers passed in.
    """
    insights: List[Dict[str, str]] = []
    if persona_summary is None or persona_summary.empty:
        return insights

    total = persona_summary["count"].sum()

    top_spend = persona_summary.loc[persona_summary["avg_spending"].idxmax()]
    insights.append({
        "title": "Highest-spending segment",
        "detail": (
            f"{top_spend['Persona']} has the highest average spending score "
            f"({top_spend['avg_spending']:.1f}/100) across {int(top_spend['count'])} customers."
        ),
    })

    low_spend = persona_summary.loc[persona_summary["avg_spending"].idxmin()]
    insights.append({
        "title": "Lowest-engagement segment",
        "detail": (
            f"{low_spend['Persona']} has the lowest average spending score "
            f"({low_spend['avg_spending']:.1f}/100), indicating the weakest current engagement."
        ),
    })

    hv = persona_summary[persona_summary["pct_high_value"] > 0]
    if not hv.empty:
        names = ", ".join(hv["Persona"].tolist())
        insights.append({
            "title": "High income combined with high spending",
            "detail": (
                f"{names} clears the High-Value rule (income and spending both at or above the "
                f"dataset median), making it the clearest target for premium offers and retention spend."
            ),
        })

    median_income = persona_summary["avg_income"].median()
    median_spending = persona_summary["avg_spending"].median()

    growth = persona_summary[
        (persona_summary["avg_income"] >= median_income) & (persona_summary["avg_spending"] < median_spending)
    ]
    if not growth.empty:
        names = ", ".join(growth["Persona"].tolist())
        insights.append({
            "title": "Growth potential",
            "detail": (
                f"{names} earns at or above the segment median income but spends below the segment "
                f"median — meaningful untapped wallet share if engagement improves."
            ),
        })

    reactivation = persona_summary[
        (persona_summary["avg_income"] < median_income) & (persona_summary["avg_spending"] < median_spending)
    ]
    if not reactivation.empty:
        names = ", ".join(reactivation["Persona"].tolist())
        insights.append({
            "title": "Reactivation candidates",
            "detail": (
                f"{names} sits below the segment median on both income and spending — "
                f"reactivation and win-back offers are more appropriate here than premium upsells."
            ),
        })

    largest = persona_summary.loc[persona_summary["count"].idxmax()]
    insights.append({
        "title": "Largest segment",
        "detail": (
            f"{largest['Persona']} is the largest group ({int(largest['count'])} customers, "
            f"{largest['count'] / total * 100:.1f}% of the base) — broad campaigns should be "
            f"tuned to this segment's profile first for reach."
        ),
    })

    return insights
