"""EDSS domain constants."""

from pipeline.hotspot_ranking.constants import ANALYZED_REGIONS

SUPPORTED_REGIONS = ANALYZED_REGIONS

PRIORITY_CRITICAL = "Critical"
PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"

PRIORITY_RANK = {
    PRIORITY_CRITICAL: 4,
    PRIORITY_HIGH: 3,
    PRIORITY_MEDIUM: 2,
    PRIORITY_LOW: 1,
}

POLICY_INCREASE_TREE_COVERAGE = "increase_tree_coverage"
POLICY_CREATE_POCKET_PARKS = "create_pocket_parks"
POLICY_DEPLOY_COOL_PAVEMENTS = "deploy_cool_pavements"
POLICY_INSTALL_ROOFTOP_GARDENS = "install_rooftop_gardens"

POLICY_CATALOG = {
    POLICY_INCREASE_TREE_COVERAGE: {
        "id": POLICY_INCREASE_TREE_COVERAGE,
        "title": "Increase tree coverage",
        "category": "urban_forestry",
        "implementationDifficulty": "Moderate",
        "implementationDifficultyScore": 3,
        "estimatedNdviLift": 0.08,
        "directCoolingC": None,
        "impactScope": "City-wide canopy expansion & street shading",
        "timeframe": "12–36 months",
    },
    POLICY_CREATE_POCKET_PARKS: {
        "id": POLICY_CREATE_POCKET_PARKS,
        "title": "Create pocket parks",
        "category": "public_green_space",
        "implementationDifficulty": "Moderate",
        "implementationDifficultyScore": 3,
        "estimatedNdviLift": 0.06,
        "directCoolingC": None,
        "impactScope": "Localized cool islands in priority heat zones",
        "timeframe": "6–18 months",
    },
    POLICY_DEPLOY_COOL_PAVEMENTS: {
        "id": POLICY_DEPLOY_COOL_PAVEMENTS,
        "title": "Deploy cool pavements",
        "category": "surface_cooling",
        "implementationDifficulty": "Hard",
        "implementationDifficultyScore": 4,
        "estimatedNdviLift": 0.0,
        "directCoolingC": 1.2,
        "impactScope": "Built-up corridors & high-albedo surfacing",
        "timeframe": "18–48 months",
    },
    POLICY_INSTALL_ROOFTOP_GARDENS: {
        "id": POLICY_INSTALL_ROOFTOP_GARDENS,
        "title": "Install rooftop gardens",
        "category": "building_greening",
        "implementationDifficulty": "Easy",
        "implementationDifficultyScore": 2,
        "estimatedNdviLift": 0.04,
        "directCoolingC": None,
        "impactScope": "Building-level heat flux reduction",
        "timeframe": "6–24 months",
    },
}
