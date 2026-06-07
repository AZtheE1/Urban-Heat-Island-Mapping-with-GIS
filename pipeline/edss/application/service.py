"""EDSS application service orchestrating decision support generation."""

from datetime import datetime, timezone

from ..domain.constants import SUPPORTED_REGIONS
from ..infrastructure.data_gateway import load_environmental_snapshot
from .policy_engine import generate_policy_suggestions
from .presenter import build_human_readable_recommendations


def _utc_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_regions(regions):
    if isinstance(regions, str):
        parsed = [item.strip() for item in regions.split(",") if item.strip()]
    else:
        parsed = [str(item).strip() for item in regions if str(item).strip()]

    if not parsed:
        raise ValueError("At least one region must be selected.")

    invalid = [region for region in parsed if region not in SUPPORTED_REGIONS]
    if invalid:
        raise ValueError(
            f"Unsupported region(s): {', '.join(invalid)}. "
            f"Supported: {', '.join(SUPPORTED_REGIONS)}"
        )
    return parsed


def generate_decision_support(base_dir, regions, regional_descriptions=None):
    """
    Build a complete Environmental Decision Support System response.

    Aggregates LST, NDVI, Heat Risk Index, climate score, and recommendations,
    then produces ranked policy suggestions with machine-readable and human-readable output.
    """
    selected_regions = _parse_regions(regions)
    regional_reports = []

    for region in selected_regions:
        snapshot = load_environmental_snapshot(base_dir, region)
        if regional_descriptions:
            snapshot["description"] = regional_descriptions.get(region)
        policy_suggestions = generate_policy_suggestions(snapshot)
        human_readable = build_human_readable_recommendations(snapshot, policy_suggestions)

        regional_reports.append(
            {
                "region": region,
                "name": snapshot["name"],
                "description": snapshot.get("description"),
                "aggregatedMetrics": {
                    "lst": snapshot["lst"],
                    "ndvi": snapshot["ndvi"],
                    "heatRiskIndex": snapshot["heatRiskIndex"],
                    "climateScore": snapshot["climateScore"],
                    "recommendations": snapshot["recommendations"],
                    "surfaceProfile": snapshot["surfaceProfile"],
                },
                "policySuggestions": policy_suggestions,
                "humanReadableRecommendations": human_readable,
            }
        )

    if len(regional_reports) == 1:
        report = regional_reports[0]
        return {
            "system": "Environmental Decision Support System",
            "generatedAt": _utc_timestamp(),
            **report,
        }

    return {
        "system": "Environmental Decision Support System",
        "generatedAt": _utc_timestamp(),
        "regions": selected_regions,
        "regionCount": len(regional_reports),
        "reports": regional_reports,
    }
