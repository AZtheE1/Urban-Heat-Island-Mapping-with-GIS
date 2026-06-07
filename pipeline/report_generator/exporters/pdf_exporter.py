"""PDF report exporter using matplotlib."""

import io

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

from .base import BaseReportExporter


class PdfReportExporter(BaseReportExporter):
    """Export environmental reports as multi-page PDF documents."""

    format_name = "pdf"

    def _add_text_page(self, pdf, title, lines):
        figure = plt.figure(figsize=(8.5, 11))
        figure.patch.set_facecolor("white")
        axis = figure.add_subplot(111)
        axis.axis("off")

        y_position = 0.95
        axis.text(0.05, y_position, title, fontsize=16, fontweight="bold", va="top")
        y_position -= 0.06

        for line in lines:
            if y_position < 0.05:
                pdf.savefig(figure, bbox_inches="tight")
                plt.close(figure)
                figure = plt.figure(figsize=(8.5, 11))
                figure.patch.set_facecolor("white")
                axis = figure.add_subplot(111)
                axis.axis("off")
                y_position = 0.95
                axis.text(0.05, y_position, f"{title} (continued)", fontsize=12, fontweight="bold", va="top")
                y_position -= 0.05

            axis.text(0.05, y_position, line, fontsize=10, va="top", wrap=True)
            y_position -= 0.035

        pdf.savefig(figure, bbox_inches="tight")
        plt.close(figure)

    def _format_statistics_block(self, label, stats):
        if not stats:
            return [f"{label}: no data"]
        return [
            f"{label}:",
            f"  Min: {stats['min']} | Max: {stats['max']} | Mean: {stats['mean']}",
            f"  Median: {stats['median']} | Std Dev: {stats['std']} | Count: {stats['count']}",
        ]

    def _section_lines(self, section):
        lines = [
            f"Region ID: {section['region']}",
            f"Locations analyzed: {section['locationCount']}",
        ]
        if section.get("description"):
            lines.append(f"Description: {section['description']}")
        lines.append("")
        lines.extend(self._format_statistics_block("Temperature (°C)", section.get("temperatureStatistics")))
        lines.append("")
        lines.extend(self._format_statistics_block("NDVI", section.get("ndviStatistics")))
        lines.append("")

        heat_risk = section.get("heatRiskIndex") or {}
        if heat_risk:
            lines.extend(
                [
                    "Heat Risk Index:",
                    f"  Average: {heat_risk.get('average')} | Min: {heat_risk.get('min')} | Max: {heat_risk.get('max')}",
                    f"  Risk distribution: {heat_risk.get('riskLevelDistribution')}",
                ]
            )
            lines.append("  Top hotspots:")
            for hotspot in heat_risk.get("topHotspots", [])[:3]:
                lines.append(
                    f"    - ({hotspot.get('lat')}, {hotspot.get('lng')}): "
                    f"{hotspot.get('lst')}°C, HRI {hotspot.get('heatRiskIndex')}, {hotspot.get('riskLevel')}"
                )
        lines.append("")

        climate = section.get("climateScore") or {}
        lines.extend(
            [
                "Climate Resilience Score:",
                f"  Score: {climate.get('score')} / 100 ({climate.get('category')})",
            ]
        )
        explanation = climate.get("explanation") or {}
        if explanation.get("summary"):
            lines.append(f"  Summary: {explanation['summary']}")
        lines.append("")

        recommendations = section.get("recommendations") or {}
        summary = recommendations.get("summary") or {}
        lines.extend(
            [
                "Green Infrastructure Recommendations:",
                f"  Priority areas: {summary.get('priorityAreas', 0)}",
                f"  Avg vegetation deficit: {summary.get('avgVegetationDeficitScore', 0)}",
                "  Top recommendations:",
            ]
        )
        for item in recommendations.get("items", [])[:5]:
            location = item.get("locationName") or f"({item.get('lat')}, {item.get('lng')})"
            lines.append(
                f"    - {location}: {item.get('interventionLevel')} | "
                f"{', '.join(item.get('suggestedActions', []))}"
            )
        return lines

    def export(self, report_document):
        buffer = io.BytesIO()
        with PdfPages(buffer) as pdf:
            cover_lines = [
                f"Generated at: {report_document.get('generatedAt')}",
                f"Regions: {', '.join(report_document.get('regions', []))}",
                "",
                "This automated report summarizes temperature, NDVI, heat risk,",
                "climate resilience, and green-infrastructure recommendations.",
            ]
            self._add_text_page(pdf, report_document.get("title", "Environmental Report"), cover_lines)

            for section in report_document.get("sections", []):
                title = f"{section.get('name')} Environmental Analysis"
                self._add_text_page(pdf, title, self._section_lines(section))

        buffer.seek(0)
        return buffer.getvalue()
