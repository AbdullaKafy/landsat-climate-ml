"""Carbon storage change from two land cover maps, as in Fig. 8 of the CHT paper.

What it shows: how the InVEST-style carbon model turns a land cover map into
carbon stock per pixel (four pools per class, Table 3), and how two dates give a
map of carbon loss and gain (S = C(T2) - C(T1)), summed per district.
Relates to Fig. 8 (carbon storage change maps) and Fig. 9 (change by district).

Synthetic data: numbers will not match the paper.
Run: python papers/2023-ei-cht-forest-carbon/sample.py [--plot]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from landsat_climate import carbon

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
args = parser.parse_args()

rng = np.random.default_rng(42)
# Classes follow the paper: 1 water, 2 vegetation, 3 built-up, 4 crop land, 5 bare land.
shape = (150, 100)
lulc_1996 = rng.choice([1, 2, 3, 4, 5], size=shape, p=[0.03, 0.75, 0.02, 0.17, 0.03])
lulc_2021 = lulc_1996.copy()
# Vegetation near the coast (left side) is cleared for crops and built-up land.
cols = np.indices(shape)[1]
cleared = (lulc_1996 == 2) & (rng.random(shape) < 0.35 * np.exp(-cols / 40))
lulc_2021[cleared] = rng.choice([3, 4], size=cleared.sum(), p=[0.3, 0.7])
# Some crop land in the hills (right side) grows back to forest.
regrown = (lulc_1996 == 4) & (rng.random(shape) < 0.25 * cols / shape[1])
lulc_2021[regrown] = 2

pools = carbon.CHT_2023_POOLS  # Mg C per ha, from Table 3 divided by 100
districts = np.repeat(np.arange(5), 20)[None, :].repeat(shape[0], axis=0)
names = ["Chittagong", "Cox's Bazar", "Khagrachari", "Rangamati", "Bandarban"]

rows = []
for d, name in enumerate(names):
    m = districts == d
    res = carbon.stock_change(lulc_1996[m], lulc_2021[m], pools, pixel_area_m2=900.0)
    rows.append({"district": name, "stock_1996_Mg": res["stock_before_mg"],
                 "stock_2021_Mg": res["stock_after_mg"], "loss_Mg": -res["emission_mg"],
                 "gain_Mg": res["sequestration_mg"], "net_Mg": res["net_change_mg"]})
table = pd.DataFrame(rows).set_index("district")
table.loc["Total"] = table.sum()
print(table.round(0).to_string())

if args.plot:
    change = carbon.stock_change(lulc_1996, lulc_2021, pools)["change_map_mg"]
    fig, ax = plt.subplots(figsize=(4, 5))
    im = ax.imshow(change, cmap="RdYlGn", vmin=-3, vmax=3)
    fig.colorbar(im, ax=ax, label="Carbon change 1996 to 2021 (Mg per pixel)")
    ax.set_title("Synthetic carbon loss (red) and gain (green)")
    ax.set_axis_off()
    fig.savefig("sample_output.png", dpi=120, bbox_inches="tight")
    print("Saved sample_output.png")
