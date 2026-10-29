"""Daytime LST zones and InVEST-style carbon stock classes for two dates.

Relates to Fig. 5 (daytime LST zone maps) and Fig. 12 (carbon stock classes),
with the carbon pools of Table 2 and the class breaks of Table 3. LST comes from
brightness temperature with emissivity = 0.004 Pv + 0.986 (Pv squared). Carbon
stock is the sum of four pools for each land cover class.

Synthetic data: numbers will not match the paper.
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import carbon, thermal

# Table 2 pools in Mg/km2 (above, below, soil, dead); the toolkit wants Mg/ha (divide by 100)
T2 = {"Bare": (2260, 9030, 14660, 294), "Built-up": (210, 4510, 11530, 27),
      "Crop": (4650, 8070, 10840, 100), "Forest": (7070, 22410, 17980, 555),
      "Grass": (3530, 8650, 9990, 190), "Vegetation": (410, 5640, 22600, 22),
      "Water": (0, 0, 11900, 123)}
POOLS = {i + 1: dict(zip(carbon.POOLS, np.array(v) / 100, strict=True))
         for i, v in enumerate(T2.values())}
CS_BREAKS = [22360, 23660, 26244, 28672, 48015]  # Table 3, Mg/km2
CS_NAMES = ["None", "Very Low", "Low", "Moderate", "High", "Very High"]
NDVI = np.array([0.15, 0.05, 0.35, 0.70, 0.45, 0.55, -0.20])  # typical NDVI per class
BT_K = np.array([304.0, 306.0, 300.0, 296.0, 299.0, 298.0, 295.0])  # warm built-up, cool water

rng = np.random.default_rng(7)
shares = {1996: [0.06, 0.04, 0.20, 0.30, 0.15, 0.20, 0.05],
          2021: [0.08, 0.20, 0.18, 0.15, 0.12, 0.22, 0.05]}
lst_rows, cs_rows, maps = {}, {}, {}
for year, p in shares.items():
    lulc = rng.choice(np.arange(1, 8), size=(150, 150), p=p)
    ndvi = NDVI[lulc - 1] + rng.normal(0, 0.05, lulc.shape)
    bt = BT_K[lulc - 1] + rng.normal(0, 1.2, lulc.shape) + (1.5 if year == 2021 else 0.0)
    emis = thermal.emissivity_from_ndvi(ndvi, ndvi_soil=ndvi.min(), ndvi_veg=ndvi.max(),
                                        e_soil=0.986, e_veg=0.990, squared=True)
    lst = thermal.lst_from_bt(bt, emis)
    lst[lst > lst.mean() + 3 * lst.std()] = np.nan  # drop hot outliers, as in the paper
    km2 = thermal.range_areas(lst, (24, 26, 28, 30, 32))
    lst_rows[year] = {k: 100 * v / sum(km2.values()) for k, v in km2.items()}
    lst_rows[year]["mean C"] = np.nanmean(lst)
    density = np.round(carbon.stock_map(lulc, POOLS) / 0.0009)  # Mg per pixel -> Mg/km2
    cs = np.digitize(density, CS_BREAKS)
    cs_rows[year] = {n: 100 * np.mean(cs == i) for i, n in enumerate(CS_NAMES)}
    maps[year] = (lst, cs)

print("Daytime LST zones (% of area) and mean LST (C)")
print(pd.DataFrame(lst_rows).T.round(2).to_string())
print("\nCarbon stock classes (% of area)")
print(pd.DataFrame(cs_rows).T.round(2).to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    for i, year in enumerate(maps):
        axes[0, i].imshow(maps[year][0], cmap="RdYlGn_r", vmin=22, vmax=36)
        axes[1, i].imshow(maps[year][1], cmap="RdYlGn", vmin=0, vmax=5)
        axes[0, i].set_title(f"LST {year}")
        axes[1, i].set_title(f"Carbon class {year}")
    fig.savefig("sample_output.png", dpi=120, bbox_inches="tight")
