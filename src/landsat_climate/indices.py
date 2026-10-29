"""Spectral indices from surface reflectance (values 0 to 1).

Pass Landsat bands as numpy or xarray arrays. Band names follow Landsat 8:
blue, green, red, nir, swir1 (1.6 um) and swir2 (2.2 um).
"""

from __future__ import annotations

import numpy as np


def _nd(a, b):
    a = np.asarray(a, dtype="float32")
    b = np.asarray(b, dtype="float32")
    with np.errstate(divide="ignore", invalid="ignore"):
        return (a - b) / (a + b)


def ndvi(nir, red):
    """Normalized Difference Vegetation Index: (NIR - Red) / (NIR + Red)."""
    return _nd(nir, red)


def ndbi(swir1, nir):
    """Normalized Difference Built-up Index: (SWIR1 - NIR) / (SWIR1 + NIR)."""
    return _nd(swir1, nir)


def ndwi(green, nir):
    """Normalized Difference Water Index (McFeeters): (Green - NIR) / (Green + NIR)."""
    return _nd(green, nir)


def mndwi(green, swir1):
    """Modified NDWI (Xu): (Green - SWIR1) / (Green + SWIR1)."""
    return _nd(green, swir1)


def savi(nir, red, L: float = 0.5):
    """Soil Adjusted Vegetation Index: (1 + L)(NIR - Red) / (NIR + Red + L)."""
    nir = np.asarray(nir, dtype="float32")
    red = np.asarray(red, dtype="float32")
    with np.errstate(divide="ignore", invalid="ignore"):
        return (1 + L) * (nir - red) / (nir + red + L)


def bsi(blue, red, nir, swir1):
    """Bare Soil Index: ((SWIR1 + Red) - (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue))."""
    return _nd(np.asarray(swir1) + np.asarray(red), np.asarray(nir) + np.asarray(blue))


def evi(nir, red, blue):
    """Enhanced Vegetation Index: 2.5 (NIR - Red) / (NIR + 6 Red - 7.5 Blue + 1)."""
    nir, red, blue = (np.asarray(x, dtype="float32") for x in (nir, red, blue))
    with np.errstate(divide="ignore", invalid="ignore"):
        return 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
