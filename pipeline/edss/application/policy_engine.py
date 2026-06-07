"""Policy suggestion engine for the EDSS."""

from ..domain.constants import (
    POLICY_CATALOG,
    POLICY_CREATE_POCKET_PARKS,
    POLICY_DEPLOY_COOL_PAVEMENTS,
    POLICY_INCREASE_TREE_COVERAGE,
    POLICY_INSTALL_ROOFTOP_GARDENS,
    PRIORITY_RANK,
)
from ..domain.priorities import classify_priority


def _estimate_cooling_effect(policy, snapshot):
    """Estimate LST reduction (°C) from regression or direct surface cooling."""
    if policy.get("directCoolingC") is not None:
        return round(float(policy["directCoolingC"]), 2)
    beta = snapshot.get("regressionBeta", 6.5)
    ndvi_lift = policy.get("estimatedNdviLift", 0.0)
    return round(beta * ndvi_lift, 2)


def _estimate_impact_label(urgency_score, cooling_c):
    """Map urgency and cooling potential to a planner-facing impact tier."""
    if urgency_score >= 75 or cooling_c >= 1.5:
        return "Very High"
    if urgency_score >= 50 or cooling_c >= 0.8:
        return "High"
    if urgency_score >= 25 or cooling_c >= 0.4:
        return "Moderate"
    return "Low"


def _policy_record(policy_id, urgency_score, rationale, snapshot, extra=None):
    policy = POLICY_CATALOG[policy_id]
    priority = classify_priority(urgency_score)
    cooling_c = _estimate_cooling_effect(policy, snapshot)
    impact_label = _estimate_impact_label(urgency_score, cooling_c)
    machine_readable = {
        "policyId": policy_id,
        "priority": priority,
        "priorityRank": PRIORITY_RANK[priority],
        "urgencyScore": round(urgency_score, 2),
        "region": snapshot["region"],
        "metricsUsed": extra or {},
    }
    return {
        "id": policy_id,
        "title": policy["title"],
        "category": policy["category"],
        "priority": priority,
        "priorityRank": PRIORITY_RANK[priority],
        "urgencyScore": round(urgency_score, 2),
        "rationale": rationale,
        "estimatedImpact": impact_label,
        "estimatedImpactScore": round(min(100.0, urgency_score * 0.85 + cooling_c * 12), 1),
        "estimatedCoolingEffectC": cooling_c,
        "implementationDifficulty": policy["implementationDifficulty"],
        "implementationDifficultyScore": policy["implementationDifficultyScore"],
        "impactScope": policy["impactScope"],
        "timeframe": policy["timeframe"],
        "machineReadable": machine_readable,
    }


def generate_policy_suggestions(snapshot):
    """Derive ranked policy suggestions from aggregated environmental metrics."""
    avg_lst = snapshot["lst"]["mean"]
    avg_ndvi = snapshot["ndvi"]["mean"]
    avg_hri = snapshot["heatRiskIndex"]["average"]
    max_lst = snapshot["lst"]["max"]
    climate_score = snapshot["climateScore"]["score"]
    climate_category = snapshot["climateScore"]["category"]
    rec_summary = snapshot["recommendations"]["summary"]
    priority_areas = rec_summary.get("priorityAreas", 0)
    location_count = snapshot["locationCount"]
    built_up_pct = snapshot["surfaceProfile"]["builtUpPercentage"]
    priority_ratio = (priority_areas / location_count) if location_count else 0.0

    policies = []

    tree_urgency = 0
    if avg_ndvi < 0.35:
        tree_urgency += 45
    elif avg_ndvi < 0.45:
        tree_urgency += 30
    if priority_ratio >= 0.4:
        tree_urgency += 35
    elif priority_ratio >= 0.25:
        tree_urgency += 20
    if avg_hri >= 0.35:
        tree_urgency += 20
    policies.append(
        _policy_record(
            POLICY_INCREASE_TREE_COVERAGE,
            tree_urgency,
            (
                f"Average NDVI is {avg_ndvi} with {priority_areas} priority heat-exposure areas. "
                "Expanding tree canopy will lower surface temperatures and improve shading."
            ),
            snapshot,
            {"avgNdvi": avg_ndvi, "priorityAreas": priority_areas},
        )
    )

    parks_urgency = 0
    if priority_areas >= 5:
        parks_urgency += 40
    elif priority_areas >= 3:
        parks_urgency += 25
    if rec_summary.get("avgVegetationDeficitScore", 0) >= 0.45:
        parks_urgency += 35
    elif rec_summary.get("avgVegetationDeficitScore", 0) >= 0.3:
        parks_urgency += 20
    if climate_score < 50:
        parks_urgency += 25
    policies.append(
        _policy_record(
            POLICY_CREATE_POCKET_PARKS,
            parks_urgency,
            (
                f"{priority_areas} locations show high temperature and low vegetation deficits. "
                "Pocket parks can create localized cool islands and community cooling corridors."
            ),
            snapshot,
            {
                "priorityAreas": priority_areas,
                "avgVegetationDeficitScore": rec_summary.get("avgVegetationDeficitScore"),
            },
        )
    )

    pavement_urgency = 0
    if avg_lst >= 32:
        pavement_urgency += 40
    elif avg_lst >= 30:
        pavement_urgency += 25
    if max_lst >= 35:
        pavement_urgency += 30
    elif max_lst >= 32:
        pavement_urgency += 15
    if built_up_pct >= 50:
        pavement_urgency += 30
    elif built_up_pct >= 35:
        pavement_urgency += 15
    policies.append(
        _policy_record(
            POLICY_DEPLOY_COOL_PAVEMENTS,
            pavement_urgency,
            (
                f"Mean LST is {avg_lst}°C with {built_up_pct}% built-up surfaces. "
                "Cool pavements and high-albedo coatings can reduce absorbed heat on roads and plazas."
            ),
            snapshot,
            {"avgLst": avg_lst, "builtUpPercentage": built_up_pct},
        )
    )

    rooftop_urgency = 0
    if avg_hri >= 0.4:
        rooftop_urgency += 40
    elif avg_hri >= 0.25:
        rooftop_urgency += 25
    if built_up_pct >= 40:
        rooftop_urgency += 25
    if climate_category in {"Critical", "Poor", "Moderate"}:
        rooftop_urgency += 20
    policies.append(
        _policy_record(
            POLICY_INSTALL_ROOFTOP_GARDENS,
            rooftop_urgency,
            (
                f"Heat Risk Index averages {avg_hri} across the region with climate score "
                f"{climate_score} ({climate_category}). Rooftop gardens reduce building heat flux "
                "and improve neighborhood cooling."
            ),
            snapshot,
            {"avgHeatRiskIndex": avg_hri, "climateScore": climate_score},
        )
    )

    policies.sort(key=lambda item: (item["priorityRank"], item["urgencyScore"]), reverse=True)
    return policies
