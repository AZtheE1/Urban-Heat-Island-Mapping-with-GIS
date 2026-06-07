"""JSON report exporter."""

import json

from .base import BaseReportExporter


class JsonReportExporter(BaseReportExporter):
    """Export environmental reports as JSON."""

    format_name = "json"

    def export(self, report_document):
        return json.dumps(report_document, indent=2, ensure_ascii=False)
