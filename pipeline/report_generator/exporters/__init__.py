"""Report exporter registry."""

from .json_exporter import JsonReportExporter
from .pdf_exporter import PdfReportExporter

EXPORTER_REGISTRY = {
    JsonReportExporter.format_name: JsonReportExporter,
    PdfReportExporter.format_name: PdfReportExporter,
}


def get_exporter(format_name):
    """Instantiate a registered report exporter."""
    exporter_cls = EXPORTER_REGISTRY.get(format_name)
    if exporter_cls is None:
        available = ", ".join(sorted(EXPORTER_REGISTRY))
        raise ValueError(f"Unsupported format '{format_name}'. Available: {available}")
    return exporter_cls()
