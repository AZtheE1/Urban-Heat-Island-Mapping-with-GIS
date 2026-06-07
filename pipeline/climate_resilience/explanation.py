"""Human-readable score explanations for climate resilience results."""

COMPONENT_DESCRIPTIONS = {
    "ndvi": "Vegetation density (NDVI) — higher values indicate stronger canopy cooling capacity.",
    "averageTemperature": "Average land surface temperature — lower values reduce heat-stress exposure.",
    "heatRiskIndex": "Composite heat risk — lower values mean reduced combined thermal and vegetation stress.",
    "greenCoveragePercentage": "Estimated green infrastructure coverage — higher values improve shading and evapotranspiration.",
}

CATEGORY_GUIDANCE = {
    "Critical": "Immediate green-infrastructure intervention is required to reduce heat vulnerability.",
    "Poor": "Significant canopy expansion and surface cooling measures should be prioritized.",
    "Moderate": "Targeted tree planting and green retrofits can improve resilience within 2-3 planning cycles.",
    "Good": "Existing green assets provide meaningful cooling; maintain and incrementally expand coverage.",
    "Excellent": "Strong vegetation and thermal balance; focus on preservation and climate-adaptive maintenance.",
}


def build_score_explanation(category, climate_score, components):
    """Generate a concise narrative explaining the composite climate resilience score."""
    strongest = max(
        components.items(),
        key=lambda item: item[1]["componentScore"],
    )
    weakest = min(
        components.items(),
        key=lambda item: item[1]["componentScore"],
    )

    strongest_label = strongest[0]
    weakest_label = weakest[0]
    strongest_score = strongest[1]["componentScore"]
    weakest_score = weakest[1]["componentScore"]

    explanation = (
        f"The region is classified as {category} with a climate resilience score of "
        f"{climate_score}/100. "
        f"The strongest factor is {strongest_label} ({strongest_score}/100), while "
        f"{weakest_label} ({weakest_score}/100) limits overall resilience. "
        f"{CATEGORY_GUIDANCE[category]}"
    )

    component_notes = {
        key: COMPONENT_DESCRIPTIONS[key]
        for key in components
    }

    return {
        "summary": explanation,
        "categoryMeaning": CATEGORY_GUIDANCE[category],
        "componentNotes": component_notes,
        "strongestFactor": {
            "component": strongest_label,
            "componentScore": strongest_score,
        },
        "weakestFactor": {
            "component": weakest_label,
            "componentScore": weakest_score,
        },
    }
