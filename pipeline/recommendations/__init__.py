"""Tree plantation and green-infrastructure recommendation package."""

from .actions import ALL_ACTIONS, suggest_actions
from .engine import generate_recommendations_from_dataframe
from .intervention import classify_intervention_level
from .scoring import compute_vegetation_deficit_score, is_priority_area, regional_min_max_normalize

__all__ = [
    "ALL_ACTIONS",
    "classify_intervention_level",
    "compute_vegetation_deficit_score",
    "generate_recommendations_from_dataframe",
    "is_priority_area",
    "suggest_actions",
]
