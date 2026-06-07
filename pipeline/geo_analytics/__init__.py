"""GeoJSON polygon analytics package."""

from .adapters import ADAPTER_REGISTRY, get_geometry_adapter
from .adapters.base import BaseGeometryAdapter
from .adapters.geojson_adapter import GeoJSONAdapter
from .adapters.shapefile_adapter import ShapefileAdapter
from .engine import analyze_region_polygon
from .validators import validate_geojson

__all__ = [
    "ADAPTER_REGISTRY",
    "BaseGeometryAdapter",
    "GeoJSONAdapter",
    "ShapefileAdapter",
    "analyze_region_polygon",
    "get_geometry_adapter",
    "validate_geojson",
]
