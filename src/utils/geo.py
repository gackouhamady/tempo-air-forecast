from __future__ import annotations


def point_to_bbox(lat: float, lon: float, delta: float = 0.1):
    return (lat - delta, lon - delta, lat + delta, lon + delta)
