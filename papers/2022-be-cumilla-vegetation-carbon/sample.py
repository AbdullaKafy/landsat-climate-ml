"""Single-channel LST from thermal DN, then LST ranges by city zone.

Relates to Fig. 6 (LST maps, 1994 to 2019) and Table 6 (share of the city in
each LST range, per zone). Steps as in the paper: DN to radiance with Lmin and
Lmax, radiance to brightness temperature with K1 and K2, a linear Pv from NDVI,
emissivity = 0.004 Pv + 0.986, then LST with lambda = 11.5 um.

Synthetic data: numbers will not match the paper.
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import thermal, zones

# Year: (Lmin, Lmax, K1, K2) as printed in the paper (Landsat 5 band 6, Landsat 8 band 10)
SENSOR = {1994: (1.238, 15.30, 607.76, 1260.56), 2019: (0.10033, 22.00180, 774.89, 1321.08)}
ZONES = ["Residential", "Commercial", "Industrial", "Educational"]  # stand-in zones
rng = np.random.default_rng(3)
n = 100
rr, cc = np.indices((n, n))
core = np.exp(-((rr - 45) ** 2 + (cc - 50) ** 2) / 900)  # dense city core
zone = zones.directional_sectors((n, n), (45, 50), n=4)  # 0..3, one per zone

rows, lst_maps = [], {}
for year, (lmin, lmax, k1, k2) in SENSOR.items():
    loss = 0.0 if year == 1994 else 0.35  # vegetation loss by 2019
    ndvi = np.clip(0.75 - (0.3 + loss) * core - 0.2 * loss + rng.normal(0, 0.08, (n, n)), -0.1, 0.9)
    heat = loss * (14 * core + 6 * (zone == 2))  # hotter core and industrial zone in 2019
    bt_true = 293 + 8 * (0.8 - ndvi) + heat + rng.normal(0, 0.7, (n, n))
    rad_true = k1 / (np.exp(k2 / bt_true) - 1)
    dn = np.round((rad_true - lmin) * 255 / (lmax - lmin))  # what the sensor stores

    radiance = lmin + (lmax - lmin) * dn / 255
    bt = thermal.radiance_to_bt(radiance, k1, k2)
    emis = thermal.emissivity_from_ndvi(ndvi, ndvi_soil=ndvi.min(), ndvi_veg=ndvi.max(),
                                        e_soil=0.986, e_veg=0.990, squared=False)
    lst = thermal.lst_from_bt(bt, emis, wavelength_um=11.5)
    lst_maps[year] = lst

    total_km2 = lst.size * 900 / 1e6
    for z, name in enumerate(ZONES):
        km2 = thermal.range_areas(lst[zone == z], (21, 25, 29, 33))
        row = {"year": year, "zone": name}
        row.update({k: 100 * v / total_km2 for k, v in km2.items()})  # % of whole city
        row["max C"] = lst[zone == z].max()
        rows.append(row)

table = pd.DataFrame(rows).set_index(["year", "zone"]).round(2)
print("Share of the city (%) in each LST range, by zone")
print(table.to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for ax, (year, lst) in zip(axes, lst_maps.items(), strict=True):
        im = ax.imshow(lst, cmap="RdYlGn_r", vmin=18, vmax=36)
        ax.set_title(f"LST {year} (C)")
    fig.colorbar(im, ax=axes)
    fig.savefig("sample_output.png", dpi=120, bbox_inches="tight")
