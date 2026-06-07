"""Intervention level classification from vegetation deficit scores."""

INTERVENTION_THRESHOLDS = (
    ("Small intervention", 0.0, 0.35),
    ("Moderate intervention", 0.35, 0.60),
    ("Aggressive intervention", 0.60, 1.0001),
)


def classify_intervention_level(deficit_score):
    """Map a vegetation deficit score to an intervention tier."""
    for label, lower, upper in INTERVENTION_THRESHOLDS:
        if lower <= deficit_score < upper:
            return label
    return "Aggressive intervention"
