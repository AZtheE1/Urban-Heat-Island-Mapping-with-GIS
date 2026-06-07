"""GeoJSON geometry adapter."""

from .base import BaseGeometryAdapter
from ..validators import extract_polygon_rings, validate_geojson


class GeoJSONAdapter(BaseGeometryAdapter):
    """Load polygon geometry from a validated GeoJSON document."""

    name = "geojson"

    def __init__(self, geojson_document):
        self.document = geojson_document
        self.validation = validate_geojson(geojson_document)

    def get_polygon_rings(self):
        if not self.validation["valid"]:
            raise ValueError(self.validation["error"])
        return extract_polygon_rings(self.document)

    def get_metadata(self):
        return {
            "source": self.name,
            "validation": self.validation,
        }
