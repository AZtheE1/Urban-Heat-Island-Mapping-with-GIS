"""Abstract report exporter interface."""

from abc import ABC, abstractmethod


class BaseReportExporter(ABC):
    """Interface for pluggable report export formats."""

    format_name = "base"

    @abstractmethod
    def export(self, report_document) -> bytes:
        """Serialize a report document to the target format. Returns raw bytes."""
