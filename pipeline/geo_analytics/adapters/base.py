"""Abstract geometry source adapters for spatial analytics."""

from abc import ABC, abstractmethod


class BaseGeometryAdapter(ABC):
    """Interface for pluggable geometry sources (GeoJSON, shapefile, etc.)."""

    name = "base"

    @abstractmethod
    def get_polygon_rings(self):
        """
        Return polygon exterior rings as lists of [longitude, latitude] pairs.

        Each ring must be closed (first coordinate equals last).
        """

    @abstractmethod
    def get_metadata(self):
        """Return source-specific metadata for API responses."""
