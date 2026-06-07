"""Climate resilience category classification."""

RESILIENCE_CATEGORIES = (
    ("Critical", 0, 20),
    ("Poor", 21, 40),
    ("Moderate", 41, 60),
    ("Good", 61, 80),
    ("Excellent", 81, 100),
)

COMPONENT_WEIGHTS = {
    "ndvi": 0.25,
    "averageTemperature": 0.25,
    "heatRiskIndex": 0.25,
    "greenCoveragePercentage": 0.25,
}


def classify_resilience_category(score):
    """Map a 0-100 climate resilience score to a categorical label."""
    bounded_score = max(0.0, min(100.0, float(score)))
    for label, lower, upper in RESILIENCE_CATEGORIES:
        if lower <= bounded_score <= upper:
            return label
    return "Excellent"
