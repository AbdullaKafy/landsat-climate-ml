"""Carbon stock from a land cover map (InVEST Carbon style).

Each land cover class gets a carbon density for four pools (Mg C per hectare):
above-ground, below-ground, soil and dead organic matter. Stock per pixel is the
sum of pools times pixel area. Change between two dates is read as sequestration
(gain) or emission (loss). Pool values must come from field data or literature for
your region: the numbers you pass decide the result.
"""

from __future__ import annotations

import numpy as np

POOLS = ("above", "below", "soil", "dead")
CO2_PER_C = 44.0 / 12.0  # convert carbon mass to CO2 equivalent

# Example pools (Mg C / ha) used for the Chittagong Hill Tracts study
# (Kafy et al., 2023, Ecological Indicators 152:110374, Table 3; printed there in
# Mg/km², divided by 100 here). Class codes follow that paper's legend.
CHT_2023_CLASSES = {1: "Water", 2: "Vegetation", 3: "Built-up", 4: "Cropland", 5: "Bare land"}
CHT_2023_POOLS = {
    1: {"above": 0.0, "below": 0.0, "soil": 119.0, "dead": 1.23},
    2: {"above": 4.10, "below": 56.40, "soil": 226.0, "dead": 0.22},
    3: {"above": 2.10, "below": 45.10, "soil": 115.30, "dead": 0.27},
    4: {"above": 46.50, "below": 80.70, "soil": 108.40, "dead": 1.00},
    5: {"above": 22.60, "below": 90.30, "soil": 146.60, "dead": 2.94},
}


def stock_map(lulc: np.ndarray, pools: dict, pixel_area_m2: float = 900.0) -> np.ndarray:
    """Carbon stock per pixel (Mg C).

    pools: {class_code: {"above": x, "below": y, "soil": z, "dead": w}} in Mg C / ha.
    Missing pools count as zero.
    """
    ha = pixel_area_m2 / 1e4
    out = np.zeros(lulc.shape, dtype="float64")
    for code, p in pools.items():
        out[lulc == code] = sum(float(p.get(k, 0.0)) for k in POOLS) * ha
    return out


def stock_change(lulc_before, lulc_after, pools: dict, pixel_area_m2: float = 900.0) -> dict:
    """Total stock at both dates, net change and CO2 equivalent (Mg)."""
    a = stock_map(lulc_before, pools, pixel_area_m2)
    b = stock_map(lulc_after, pools, pixel_area_m2)
    diff = b - a
    return {"stock_before_mg": float(a.sum()), "stock_after_mg": float(b.sum()),
            "net_change_mg": float(diff.sum()),
            "emission_mg": float(-diff[diff < 0].sum()),
            "sequestration_mg": float(diff[diff > 0].sum()),
            "net_co2e_mg": float(diff.sum() * CO2_PER_C),
            "change_map_mg": diff}
