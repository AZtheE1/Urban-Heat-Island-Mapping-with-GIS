"""Automated environmental report generator package."""

from .constants import DEFAULT_FORMAT, FORMAT_JSON, FORMAT_PDF, SUPPORTED_FORMATS, SUPPORTED_REGIONS
from .engine import generate_environmental_report, generate_environmental_report_json
from .exporters.base import BaseReportExporter

__all__ = [
    "BaseReportExporter",
    "DEFAULT_FORMAT",
    "FORMAT_JSON",
    "FORMAT_PDF",
    "SUPPORTED_FORMATS",
    "SUPPORTED_REGIONS",
    "generate_environmental_report",
    "generate_environmental_report_json",
]
