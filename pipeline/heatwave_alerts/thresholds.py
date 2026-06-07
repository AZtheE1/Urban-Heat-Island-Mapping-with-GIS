"""Heatwave alert threshold definitions."""

ALERT_THRESHOLDS = (
    ("Extreme", 40.0),
    ("Severe", 38.0),
    ("Warning", 35.0),
)

LEVEL_NORMAL = "Normal"


def classify_alert_level(temperature):
    """
    Classify temperature into the highest applicable heatwave alert level.

    Thresholds (strictly greater than):
      >40°C Extreme, >38°C Severe, >35°C Warning
    """
    temp = float(temperature)
    for level, threshold in ALERT_THRESHOLDS:
        if temp > threshold:
            return level
    return LEVEL_NORMAL


def threshold_reference():
    """Return configured thresholds for API consumers."""
    return {
        "warning": 35.0,
        "severe": 38.0,
        "extreme": 40.0,
    }
