"""Pure-Python spatial helpers for polygon analytics."""

import math


def point_in_ring(lng, lat, ring):
    """Ray-casting point-in-polygon test for a single exterior ring."""
    inside = False
    count = len(ring)
    if count < 4:
        return False

    j = count - 1
    for i in range(count):
        xi, yi = float(ring[i][0]), float(ring[i][1])
        xj, yj = float(ring[j][0]), float(ring[j][1])
        intersects = ((yi > lat) != (yj > lat)) and (
            lng < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-15) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def point_in_any_polygon(lng, lat, rings):
    """Return True when a point falls inside any provided polygon ring."""
    return any(point_in_ring(lng, lat, ring) for ring in rings)


def compute_bounding_box(rings):
    """Compute min/max latitude and longitude for polygon rings."""
    lng_values = []
    lat_values = []
    for ring in rings:
        for coordinate in ring:
            lng_values.append(float(coordinate[0]))
            lat_values.append(float(coordinate[1]))

    if not lng_values:
        return None

    return {
        "minLng": round(min(lng_values), 6),
        "maxLng": round(max(lng_values), 6),
        "minLat": round(min(lat_values), 6),
        "maxLat": round(max(lat_values), 6),
    }


def approximate_polygon_area_sq_km(ring):
    """
    Estimate polygon area in square kilometers using the shoelace formula
    with longitude/latitude converted to planar meters at mean latitude.
    """
    if len(ring) < 4:
        return 0.0

    lats = [float(coordinate[1]) for coordinate in ring]
    mean_lat_rad = math.radians(sum(lats) / len(lats))
    meters_per_degree_lat = 111_320.0
    meters_per_degree_lng = 111_320.0 * math.cos(mean_lat_rad)

    projected = [
        (float(coordinate[0]) * meters_per_degree_lng, float(coordinate[1]) * meters_per_degree_lat)
        for coordinate in ring
    ]

    area = 0.0
    for i in range(len(projected) - 1):
        x1, y1 = projected[i]
        x2, y2 = projected[i + 1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0 / 1_000_000.0
