"""Index-based agricultural drought: VCI, TCI and VHI (after Kogan, 1995).

Each index compares one date with the range seen over many years for the same
pixel and season. Pass a stack with time on axis 0 to get the min and max.
"""

from __future__ import annotations

import numpy as np

# VHI drought severity classes (lower VHI = more severe drought).
VHI_BREAKS = (10, 20, 30, 40)
VHI_CLASSES = ("Extreme", "Severe", "Moderate", "Mild", "No drought")


def vci(ndvi, ndvi_min, ndvi_max):
    """Vegetation Condition Index (0 to 100): 100 (NDVI - min) / (max - min)."""
    ndvi = np.asarray(ndvi, dtype="float64")
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100 * (ndvi - ndvi_min) / (np.asarray(ndvi_max) - ndvi_min)


def tci(temp, temp_min, temp_max):
    """Temperature Condition Index (0 to 100): 100 (max - T) / (max - min)."""
    t = np.asarray(temp, dtype="float64")
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100 * (np.asarray(temp_max) - t) / (np.asarray(temp_max) - temp_min)


def vhi(vci_values, tci_values, alpha: float = 0.5):
    """Vegetation Health Index: alpha VCI + (1 - alpha) TCI."""
    return alpha * np.asarray(vci_values) + (1 - alpha) * np.asarray(tci_values)


def from_stack(ndvi_stack, temp_stack):
    """VCI, TCI and VHI for every date in a (time, rows, cols) stack."""
    n = np.asarray(ndvi_stack, dtype="float64")
    t = np.asarray(temp_stack, dtype="float64")
    v = vci(n, np.nanmin(n, axis=0), np.nanmax(n, axis=0))
    c = tci(t, np.nanmin(t, axis=0), np.nanmax(t, axis=0))
    return v, c, vhi(v, c)


def classify_vhi(values, breaks=VHI_BREAKS, names=VHI_CLASSES):
    """Drought severity class for each VHI value."""
    v = np.asarray(values, dtype="float64")
    out = np.asarray(names, dtype=object)[np.searchsorted(np.asarray(breaks), v, side="right")]
    out[~np.isfinite(v)] = None
    return out
