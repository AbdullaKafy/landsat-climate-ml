"""Urban growth, UTFVI, regression and PCA, as behind Figs. 2 and 8 of the Saudi paper.

What it shows: yearly built-up maps give the urban share, the expanding speed and
intensity, and the gravity center (Fig. 2). Yearly LST maps give UTFVI (Fig. 8).
Each parameter is then regressed on urban expansion (EP = b0 + b1 UE), and PCA
ranks the parameters by their PC1 loading (Table 4). The toolkit uses the
per-pixel UTFVI, (Ts - Tmean) / Ts, not the form printed in the paper.

Synthetic data: numbers will not match the paper.
Run: python papers/2024-jem-saudi-urban-analytics/sample.py [--plot]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from landsat_climate import lulc, stats, thermal, zones

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
args = parser.parse_args()

rng = np.random.default_rng(3)
years = [1987, 1992, 1997, 2002, 2007, 2012, 2017, 2022]
shape = (120, 120)
rr, cc = np.indices(shape)
rows, prev = [], None
for i, y in enumerate(years):
    dist = np.hypot(rr - 50, cc - (40 + 2 * i))  # the city grows and drifts east
    urban = dist < 8 + 2.2 * i + rng.normal(0, 1.5, shape)
    lst = 42 + (2 + 0.4 * i) * urban + rng.normal(0, 1.5, shape)  # deg C
    utf = thermal.utfvi(lst)
    area = urban.sum() * 900 / 1e6  # km2
    r, c = zones.gravity_center(urban)
    row = {"year": y, "urban_km2": area, "gc_row": r, "gc_col": c,
           "UTFVI": float(utf[urban].mean()), "EVI": 0.12 - 0.004 * i + rng.normal(0, 0.003),
           "PM25": 44 + 4 * i + rng.normal(0, 2)}
    if prev is not None:
        idx = lulc.expansion_indices(prev, area, 5, shape[0] * shape[1] * 900 / 1e6)
        row["speed_km2_yr"] = idx["speed_km2_per_year"]
    rows.append(row)
    prev = area
table = pd.DataFrame(rows).set_index("year")
print(table.round(4).to_string())

eps = table[["UTFVI", "EVI", "PM25"]]
print("\nRegression of each parameter on urban area (EP = b0 + b1 UE)")
for name in eps:
    res = stats.correlation(table["urban_km2"], eps[name])
    print(f"{name:6s} b1 = {res['slope']:+.4f}  R2 = {res['r2']:.2f}")
loadings, var = stats.pca_loadings((eps - eps.mean()) / eps.std(), n_components=2)
print("\nPCA loadings (standardized inputs)")
print(loadings.round(2).to_string())

if args.plot:
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].imshow(urban, cmap="Reds")
    axes[0].set_title(f"Built-up, {years[-1]}")
    im = axes[1].imshow(utf, cmap="RdYlGn_r")
    axes[1].set_title(f"UTFVI, {years[-1]}")
    fig.colorbar(im, ax=axes[1], shrink=0.8)
    for ax in axes:
        ax.set_axis_off()
    fig.savefig("sample_output.png", dpi=120, bbox_inches="tight")
    print("Saved sample_output.png")
