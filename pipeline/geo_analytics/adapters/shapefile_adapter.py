"""Shapefile adapter stub for future GIS integration."""

from .base import BaseGeometryAdapter


class ShapefileAdapter(BaseGeometryAdapter):
    """
    Placeholder adapter for future shapefile uploads.

    Integrate geopandas or fiona here when shapefile support is enabled:
      adapter = ShapefileAdapter(path_to_shp)
      rings = adapter.get_polygon_rings()
    """

    name = "shapefile"

    def __init__(self, file_path):
        self.file_path = file_path

    def get_polygon_rings(self):
        raise NotImplementedError(
            "Shapefile support is not enabled yet. "
            "Install geopandas/fiona and implement ShapefileAdapter, "
            "or upload GeoJSON via GeoJSONAdapter."
        )

    def get_metadata(self):
        return {
            "source": self.name,
            "filePath": self.file_path,
            "status": "not_implemented",
        }
