"""Supported hotspot ranking regions and sort modes."""

ANALYZED_REGIONS = (
    "mirpur12",
    "dhaka_all",
    "sylhet",
    "rajshahi",
    "chittagong",
)

SORT_BY_TEMPERATURE = "temperature"
SORT_BY_HEAT_RISK = "heatRiskIndex"

SORT_OPTIONS = {
    SORT_BY_TEMPERATURE,
    SORT_BY_HEAT_RISK,
}

DEFAULT_SORT = SORT_BY_TEMPERATURE
DEFAULT_LIMIT = 10
