"""Report generator constants and supported export formats."""

from pipeline.hotspot_ranking.constants import ANALYZED_REGIONS

SUPPORTED_REGIONS = ANALYZED_REGIONS

FORMAT_JSON = "json"
FORMAT_PDF = "pdf"

SUPPORTED_FORMATS = {
    FORMAT_JSON,
    FORMAT_PDF,
}

DEFAULT_FORMAT = FORMAT_JSON
