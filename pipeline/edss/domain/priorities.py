"""Priority classification for EDSS policy suggestions."""

from .constants import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
)


def classify_priority(urgency_score):
    """Map an urgency score (0-100) to Critical, High, Medium, or Low."""
    score = max(0.0, min(100.0, float(urgency_score)))
    if score >= 75:
        return PRIORITY_CRITICAL
    if score >= 50:
        return PRIORITY_HIGH
    if score >= 25:
        return PRIORITY_MEDIUM
    return PRIORITY_LOW
