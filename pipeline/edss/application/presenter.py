"""Human-readable EDSS presentation layer."""

from ..domain.constants import PRIORITY_RANK


def build_human_readable_recommendations(snapshot, policy_suggestions):
    """Convert machine-readable EDSS output into planner-facing narrative text."""
    region_name = snapshot["name"]
    avg_lst = snapshot["lst"]["mean"]
    avg_ndvi = snapshot["ndvi"]["mean"]
    avg_hri = snapshot["heatRiskIndex"]["average"]
    climate_score = snapshot["climateScore"]["score"]
    climate_category = snapshot["climateScore"]["category"]
    priority_areas = snapshot["recommendations"]["summary"].get("priorityAreas", 0)

    if not policy_suggestions:
        return {
            "executiveSummary": f"No policy actions were generated for {region_name}.",
            "priorityActions": [],
            "fullNarrative": f"Environmental conditions in {region_name} did not trigger EDSS policy rules.",
        }

    top_policy = policy_suggestions[0]
    executive_summary = (
        f"{region_name} requires {top_policy['priority'].lower()}-priority intervention focused on "
        f"{top_policy['title'].lower()}. "
        f"Current conditions: average LST {avg_lst}°C, NDVI {avg_ndvi}, Heat Risk Index {avg_hri}, "
        f"and climate resilience score {climate_score}/100 ({climate_category}). "
        f"{priority_areas} locations are flagged as heat-vegetation priority areas."
    )

    priority_actions = [
        f"[{policy['priority']}] {policy['title']}: {policy['rationale']}"
        for policy in policy_suggestions
        if policy["priorityRank"] >= PRIORITY_RANK["Medium"]
    ]

    narrative_lines = [
        f"Environmental Decision Support analysis for {region_name}:",
        f"- Land Surface Temperature (LST): average {avg_lst}°C (max {snapshot['lst']['max']}°C)",
        f"- NDVI: average {avg_ndvi}",
        f"- Heat Risk Index: average {avg_hri}",
        f"- Climate resilience: {climate_score}/100 ({climate_category})",
        f"- Priority intervention areas: {priority_areas}",
        "",
        "Recommended policy pathway (highest priority first):",
    ]
    for index, policy in enumerate(policy_suggestions, start=1):
        narrative_lines.append(
            f"{index}. [{policy['priority']}] {policy['title']} — {policy['rationale']}"
        )

    return {
        "executiveSummary": executive_summary,
        "priorityActions": priority_actions,
        "fullNarrative": "\n".join(narrative_lines),
    }
