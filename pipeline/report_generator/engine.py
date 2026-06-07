"""Environmental report generation engine."""

from datetime import datetime, timezone

from .collector import collect_multi_region_report
from .constants import DEFAULT_FORMAT, FORMAT_JSON, SUPPORTED_FORMATS, SUPPORTED_REGIONS
from .exporters import get_exporter


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


def generate_environmental_report(
    base_dir,
    regions,
    export_format=DEFAULT_FORMAT,
    regional_descriptions=None,
):
    """
    Generate an automated environmental report for selected regions.

    Returns the structured report document and serialized export payload.
    """
    if export_format not in SUPPORTED_FORMATS:
        available = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(f"Unsupported export format '{export_format}'. Available: {available}")

    selected_regions = _parse_regions(regions)
    sections = collect_multi_region_report(
        base_dir,
        selected_regions,
        regional_descriptions=regional_descriptions,
    )

    report_document = {
        "reportId": f"env-report-{'-'.join(selected_regions)}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "title": "Urban Heat Island Environmental Report",
        "generatedAt": _utc_timestamp(),
        "regions": selected_regions,
        "sectionCount": len(sections),
        "sections": sections,
    }

    exporter = get_exporter(export_format)
    exported = exporter.export(report_document)

    return report_document, exported, export_format


def generate_environmental_report_json(base_dir, regions, regional_descriptions=None):
    """Convenience helper for JSON-only report generation."""
    document, exported, _ = generate_environmental_report(
        base_dir,
        regions,
        export_format=FORMAT_JSON,
        regional_descriptions=regional_descriptions,
    )
    return document, exported
