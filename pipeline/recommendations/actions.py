"""Suggested green-infrastructure actions by intervention level and surface type."""

ACTION_TREE_PLANTATION = "Tree plantation"
ACTION_GREEN_ROOFS = "Green roofs"
ACTION_VERTICAL_GARDENS = "Vertical gardens"
ACTION_COMMUNITY_PARKS = "Community parks"

ALL_ACTIONS = (
    ACTION_TREE_PLANTATION,
    ACTION_GREEN_ROOFS,
    ACTION_VERTICAL_GARDENS,
    ACTION_COMMUNITY_PARKS,
)

BASE_ACTIONS_BY_INTERVENTION = {
    "Small intervention": (ACTION_TREE_PLANTATION,),
    "Moderate intervention": (
        ACTION_TREE_PLANTATION,
        ACTION_GREEN_ROOFS,
        ACTION_VERTICAL_GARDENS,
    ),
    "Aggressive intervention": ALL_ACTIONS,
}

BUILT_UP_SURFACES = {"Asphalt", "Concrete", "Bare Soil", "Mixed"}
HIGH_TRAFFIC = {"High", "Medium"}


def suggest_actions(intervention_level, surface_type=None, traffic_density=None):
    """
    Return ranked green-infrastructure actions for a location.

    Surface type and traffic density refine the default action set without
    removing required intervention-tier actions.
    """
    actions = list(BASE_ACTIONS_BY_INTERVENTION.get(intervention_level, ALL_ACTIONS))
    surface = str(surface_type or "").strip()

    if surface == "Vegetation":
        if ACTION_COMMUNITY_PARKS not in actions:
            actions.append(ACTION_COMMUNITY_PARKS)
        if intervention_level == "Small intervention":
            return [ACTION_COMMUNITY_PARKS, ACTION_TREE_PLANTATION]

    if surface in {"Concrete", "Asphalt"} and ACTION_GREEN_ROOFS not in actions:
        actions.append(ACTION_GREEN_ROOFS)

    if str(traffic_density or "") in HIGH_TRAFFIC:
        if ACTION_VERTICAL_GARDENS not in actions:
            actions.append(ACTION_VERTICAL_GARDENS)

    if surface in BUILT_UP_SURFACES and intervention_level == "Aggressive intervention":
        actions = list(ALL_ACTIONS)

    seen = set()
    ordered = []
    for action in actions:
        if action not in seen:
            seen.add(action)
            ordered.append(action)
    return ordered
