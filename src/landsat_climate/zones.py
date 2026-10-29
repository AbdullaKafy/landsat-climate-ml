"""Directional (gradient) analysis around a city center.

Many urban change studies split a city into compass sectors (N, NE, E ...) and
rings at fixed distances from the center, then report how much of each class or
temperature range falls in each zone. This shows where a city grows or heats up.
"""

from __future__ import annotations

import numpy as np

SECTORS8 = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def _grid(shape, center_rc):
    r, c = np.indices(shape)
    dy = center_rc[0] - r  # rows grow downward, so north is a smaller row
    dx = c - center_rc[1]
    return dx, dy


def directional_sectors(shape, center_rc, n: int = 8) -> np.ndarray:
    """Sector index (0 = N, going clockwise) for every pixel. n = 4, 8 or 16."""
    dx, dy = _grid(shape, center_rc)
    bearing = (np.degrees(np.arctan2(dx, dy)) + 360) % 360
    width = 360 / n
    return (((bearing + width / 2) // width) % n).astype(int)


def concentric_rings(shape, center_rc, ring_m: float, pixel_m: float = 30.0) -> np.ndarray:
    """Ring index (0 = innermost) for rings of width `ring_m` meters."""
    dx, dy = _grid(shape, center_rc)
    return (np.hypot(dx, dy) * pixel_m // ring_m).astype(int)


def share_by_zone(classes: np.ndarray, zones: np.ndarray, code) -> dict:
    """Percent of each zone covered by class `code` (e.g. built-up)."""
    out = {}
    for z in np.unique(zones):
        m = zones == z
        valid = m & (classes > 0) if np.issubdtype(classes.dtype, np.number) else m
        out[int(z)] = 100 * float(np.mean(classes[valid] == code)) if valid.any() else np.nan
    return out


def gravity_center(mask: np.ndarray) -> tuple[float, float]:
    """Center of gravity (row, col) of a class, e.g. built-up pixels.

    Track it across years to see which way a city grows.
    """
    r, c = np.nonzero(mask)
    return float(r.mean()), float(c.mean())
