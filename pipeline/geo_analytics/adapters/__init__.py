"""Geometry adapter registry."""

from .geojson_adapter import GeoJSONAdapter
from .shapefile_adapter import ShapefileAdapter

ADAPTER_REGISTRY = {
    GeoJSONAdapter.name: GeoJSONAdapter,
    ShapefileAdapter.name: ShapefileAdapter,
}


def get_geometry_adapter(source_type, payload):
    """Instantiate a registered geometry adapter."""
    adapter_cls = ADAPTER_REGISTRY.get(source_type)
    if adapter_cls is None:
        available = ", ".join(sorted(ADAPTER_REGISTRY))
        raise ValueError(f"Unknown geometry source '{source_type}'. Available: {available}")
    return adapter_cls(payload)
