"""GeoJSON structure validation."""

SUPPORTED_ROOT_TYPES = {"FeatureCollection", "Feature", "Polygon", "MultiPolygon"}
POLYGON_TYPES = {"Polygon", "MultiPolygon"}


def _validate_ring(ring, context):
    if not isinstance(ring, list) or len(ring) < 4:
        return f"{context}: polygon ring must contain at least 4 coordinate pairs."

    for index, coordinate in enumerate(ring):
        if not isinstance(coordinate, (list, tuple)) or len(coordinate) < 2:
            return f"{context}: coordinate at index {index} must be [longitude, latitude]."
        lng, lat = coordinate[0], coordinate[1]
        if not isinstance(lng, (int, float)) or not isinstance(lat, (int, float)):
            return f"{context}: coordinate at index {index} must be numeric."
        if not (-180.0 <= float(lng) <= 180.0 and -90.0 <= float(lat) <= 90.0):
            return f"{context}: coordinate at index {index} is out of WGS84 bounds."

    first = ring[0]
    last = ring[-1]
    if first[0] != last[0] or first[1] != last[1]:
        return f"{context}: polygon ring must be closed (first and last coordinates must match)."
    return None


def _validate_polygon_coordinates(coordinates, context):
    if not isinstance(coordinates, list) or not coordinates:
        return f"{context}: polygon coordinates are missing."

    for ring_index, ring in enumerate(coordinates):
        error = _validate_ring(ring, f"{context} ring {ring_index}")
        if error:
            return error
    return None


def _validate_geometry(geometry, context="geometry"):
    if not isinstance(geometry, dict):
        return f"{context}: geometry must be an object."

    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geometry_type not in POLYGON_TYPES:
        return (
            f"{context}: unsupported geometry type '{geometry_type}'. "
            "Only Polygon and MultiPolygon are supported."
        )

    if geometry_type == "Polygon":
        return _validate_polygon_coordinates(coordinates, context)

    for part_index, polygon_coords in enumerate(coordinates or []):
        error = _validate_polygon_coordinates(polygon_coords, f"{context} polygon {part_index}")
        if error:
            return error
    return None


def validate_geojson(document):
    """Validate GeoJSON structure for polygon-based regional analysis."""
    if not isinstance(document, dict):
        return {"valid": False, "error": "GeoJSON payload must be a JSON object."}

    root_type = document.get("type")
    if root_type not in SUPPORTED_ROOT_TYPES:
        return {
            "valid": False,
            "error": (
                f"Unsupported GeoJSON type '{root_type}'. "
                "Expected FeatureCollection, Feature, Polygon, or MultiPolygon."
            ),
        }

    feature_count = 0
    geometry_types = set()

    if root_type == "FeatureCollection":
        features = document.get("features")
        if not isinstance(features, list) or not features:
            return {"valid": False, "error": "FeatureCollection must include a non-empty features array."}
        for index, feature in enumerate(features):
            if not isinstance(feature, dict) or feature.get("type") != "Feature":
                return {"valid": False, "error": f"Feature at index {index} must be a GeoJSON Feature."}
            geometry = feature.get("geometry")
            if geometry is None:
                return {"valid": False, "error": f"Feature at index {index} is missing geometry."}
            error = _validate_geometry(geometry, f"features[{index}].geometry")
            if error:
                return {"valid": False, "error": error}
            geometry_types.add(geometry.get("type"))
        feature_count = len(features)

    elif root_type == "Feature":
        geometry = document.get("geometry")
        if geometry is None:
            return {"valid": False, "error": "Feature is missing geometry."}
        error = _validate_geometry(geometry, "geometry")
        if error:
            return {"valid": False, "error": error}
        geometry_types.add(geometry.get("type"))
        feature_count = 1

    else:
        error = _validate_geometry(document, "geometry")
        if error:
            return {"valid": False, "error": error}
        geometry_types.add(root_type)
        feature_count = 1

    return {
        "valid": True,
        "rootType": root_type,
        "geometryTypes": sorted(geometry_types),
        "featureCount": feature_count,
    }


def extract_polygon_rings(document):
    """Extract exterior polygon rings from a validated GeoJSON document."""
    rings = []

    def add_geometry(geometry):
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])
        if geometry_type == "Polygon":
            if coordinates:
                rings.append(coordinates[0])
        elif geometry_type == "MultiPolygon":
            for polygon_coords in coordinates:
                if polygon_coords:
                    rings.append(polygon_coords[0])

    root_type = document.get("type")
    if root_type == "FeatureCollection":
        for feature in document.get("features", []):
            add_geometry(feature.get("geometry", {}))
    elif root_type == "Feature":
        add_geometry(document.get("geometry", {}))
    else:
        add_geometry(document)

    return rings
