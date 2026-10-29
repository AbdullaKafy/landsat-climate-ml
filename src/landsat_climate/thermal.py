"""Land surface temperature (LST), urban heat island (UHI) and UTFVI.

Two ways to get LST:

* Landsat Collection 2 Level-2 already gives surface temperature (see `data.py`).
* For Level-1 thermal bands, `lst_from_bt` applies the single-channel method used
  in many published studies: brightness temperature, NDVI-based emissivity, then

      LST = BT / (1 + (lambda * BT / rho) * ln(emissivity))

All temperatures in this module are in °C unless a name says Kelvin.
"""

from __future__ import annotations

import numpy as np

RHO = 1.438e-2  # h * c / sigma, in m K

# Widely used UTFVI ecological evaluation classes (after Zhang et al., 2006).
UTFVI_BREAKS = (0.0, 0.005, 0.010, 0.015, 0.020)
UTFVI_CLASSES = ("None", "Weak", "Middle", "Strong", "Stronger", "Strongest")


def radiance_to_bt(radiance, k1: float, k2: float):
    """Top-of-atmosphere brightness temperature (Kelvin) from thermal radiance.

    K1 and K2 are in the Landsat MTL file (for example Landsat 8 band 10:
    K1 = 774.8853, K2 = 1321.0789).
    """
    rad = np.asarray(radiance, dtype="float64")
    with np.errstate(divide="ignore", invalid="ignore"):
        return k2 / np.log(k1 / rad + 1)


def emissivity_from_ndvi(ndvi, ndvi_soil: float = 0.2, ndvi_veg: float = 0.5,
                         e_soil: float = 0.97, e_veg: float = 0.99, squared: bool = True):
    """Land surface emissivity from the proportion of vegetation (Pv).

    Pv = ((NDVI - NDVIs) / (NDVIv - NDVIs)), squared by default, clipped to 0..1.
    Emissivity = e_veg * Pv + e_soil * (1 - Pv). Water (NDVI < 0) gets 0.991.
    Some studies use a linear Pv and emissivity = 0.004 Pv + 0.986; for that,
    call with squared=False, e_soil=0.986, e_veg=0.990.
    """
    v = np.asarray(ndvi, dtype="float64")
    pv = np.clip((v - ndvi_soil) / (ndvi_veg - ndvi_soil), 0, 1)
    if squared:
        pv = pv**2
    e = e_veg * pv + e_soil * (1 - pv)
    return np.where(v < 0, 0.991, e)


def emissivity_ndvi_thresholds(ndvi):
    """Emissivity from NDVI thresholds (after Sobrino et al., 2004, as used in several studies).

    NDVI < -0.185: 0.995 (water); -0.185 to 0.157: 0.970 (soil);
    0.157 to 0.727: 1.0094 + 0.047 ln(NDVI) (mixed); > 0.727: 0.990 (dense vegetation).
    """
    v = np.asarray(ndvi, dtype="float64")
    with np.errstate(divide="ignore", invalid="ignore"):
        mixed = 1.0094 + 0.047 * np.log(v)
    return np.select([v < -0.185, v < 0.157, v <= 0.727], [0.995, 0.970, mixed], 0.990)


def lst_from_bt(bt_kelvin, emissivity, wavelength_um: float = 10.895):
    """Single-channel LST in °C. Default wavelength is Landsat 8 band 10.

    Use 11.45 um for Landsat 5 TM band 6.
    """
    bt = np.asarray(bt_kelvin, dtype="float64")
    lam = wavelength_um * 1e-6
    lst_k = bt / (1 + (lam * bt / RHO) * np.log(np.asarray(emissivity, dtype="float64")))
    return lst_k - 273.15


def uhi(lst_c):
    """Normalized urban heat island: (LST - mean) / standard deviation."""
    t = np.asarray(lst_c, dtype="float64")
    return (t - np.nanmean(t)) / np.nanstd(t)


def utfvi(lst_c, denominator: str = "ts"):
    """UTFVI = (Ts - Tmean) / Ts, with temperatures in Kelvin.

    Most studies divide by the pixel temperature Ts (the default). Some divide by
    the mean Tmean instead; use denominator="tmean" to match those.
    """
    ts = np.asarray(lst_c, dtype="float64") + 273.15
    tm = np.nanmean(ts)
    return (ts - tm) / (ts if denominator == "ts" else tm)


def classify_utfvi(values):
    """Map UTFVI values to the six ecological evaluation classes."""
    v = np.asarray(values, dtype="float64")
    idx = np.searchsorted(np.asarray(UTFVI_BREAKS), v, side="right")
    out = np.asarray(UTFVI_CLASSES, dtype=object)[idx]
    out[~np.isfinite(v)] = None
    return out


def range_areas(lst_c, breaks, pixel_area_m2: float = 900.0) -> dict:
    """Area (km²) in each temperature range, e.g. breaks=(20, 25, 30, 35).

    Returns {"<20": km2, "20-25": km2, ..., ">35": km2}.
    """
    t = np.asarray(lst_c, dtype="float64")
    t = t[np.isfinite(t)]
    edges = [-np.inf, *breaks, np.inf]
    out = {}
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        if lo == -np.inf:
            name = f"<{hi:g}"
        elif hi == np.inf:
            name = f">{lo:g}"
        else:
            name = f"{lo:g}-{hi:g}"
        out[name] = float(np.sum((t >= lo) & (t < hi))) * pixel_area_m2 / 1e6
    return out


def stats_by_class(values, classes, names: dict) -> dict:
    """Mean, min, max and standard deviation of `values` inside each class."""
    v = np.asarray(values, dtype="float64")
    c = np.asarray(classes)
    out = {}
    for code, name in names.items():
        x = v[(c == code) & np.isfinite(v)]
        out[name] = {"mean": float(np.mean(x)) if x.size else np.nan,
                     "min": float(np.min(x)) if x.size else np.nan,
                     "max": float(np.max(x)) if x.size else np.nan,
                     "std": float(np.std(x)) if x.size else np.nan}
    return out
