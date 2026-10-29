"""Urban growth and seasonal LST, now and predicted, as in Saha et al. (2022), Sylhet.

What it shows: a city that grows every five years, its summer and winter LST
in six temperature ranges (Fig. 5, Table 3), the link between built-up area and
mean LST, then a CA-ANN land cover forecast and an ANN that predicts LST for
2025 and 2030 (Fig. 16, Fig. 17).
Synthetic data: numbers will not match the paper.
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import caann, lstmodel, lulc, stats, thermal

rng = np.random.default_rng(11)
N = 120  # 120 x 120 pixels of 30 m
yy, xx = np.mgrid[:N, :N]
dist = np.hypot(yy - N / 2, xx - N / 2) + rng.normal(0, 6, (N, N))
soil = rng.random((N, N))
dem = 15 + 0.08 * yy + rng.normal(0, 0.5, (N, N))
CLASS_LST = {1: 26.0, 2: 35.5, 3: 28.0, 4: 31.0}  # summer mean LST (°C) per class
SEASON_SHIFT = {"Summer": 0.0, "Winter": -10.0}
BREAKS = (18, 22, 26, 30, 34)  # LST ranges used in the paper, °C


def land_cover(radius):
    lc = np.where(soil > 0.7, 4, 3).astype("uint8")
    lc[dist < radius] = 2
    lc[np.abs(yy - 0.4 * xx - 75) < 3] = 1  # the Surma river
    return lc


lc = {y: land_cover(r) for y, r in zip(range(1995, 2021, 5), range(18, 39, 4), strict=True)}
weather = rng.normal(0, 0.3, (2, len(lc)))  # year-to-year weather, °C
lst = {(s, y): np.vectorize(CLASS_LST.get)(m) + d + weather[i, j] + rng.normal(0, 1.2, (N, N))
       for j, (y, m) in enumerate(lc.items()) for i, (s, d) in enumerate(SEASON_SHIFT.items())}
built = [lulc.class_areas(lc[y])["Built-up"] for y in lc]
for s in SEASON_SHIFT:
    r = stats.correlation(built, [lst[s, y].mean() for y in lc])["r"]
    print(f"Built-up area vs mean {s.lower()} LST: r = {r:.3f}")

ca = caann.CAANN(neighborhood=3, seed=0).fit(lc[2015], lc[2020], dem)
markov = caann.transition_matrix(lc[2015], lc[2020])
lc[2025] = ca.step(lc[2020], dem, markov)
lc[2030] = ca.step(lc[2025], dem, markov)
for s in SEASON_SHIFT:
    model, score = lstmodel.fit_lst_model(lc[2020], dem, lst[s, 2020], n_splits=3)
    print(f"{s} ANN check on 2020: R2 = {score['r2']:.2f}, RMSE = {score['rmse']:.2f} °C")
    for y in (2025, 2030):
        lst[s, y] = lstmodel.predict_lst(model, lc[y], dem)

panels = [(s, y) for s in SEASON_SHIFT for y in (2020, 2025, 2030)]
rows = {f"{s} {y}": thermal.range_areas(lst[s, y], BREAKS) for s, y in panels}
print("\nArea (km²) in each LST range (°C); 2025 and 2030 are predicted")
print(pd.DataFrame(rows).round(2).to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(10, 6.5))
    for ax, (s, y) in zip(axes.ravel(), panels, strict=True):
        im = ax.imshow(lst[s, y], cmap="RdYlBu_r", vmin=16, vmax=36)
        ax.set_title(f"{s} LST, {y}", fontsize=10)
        ax.set_axis_off()
    fig.colorbar(im, ax=axes, shrink=0.7, label="LST (°C)")
    fig.savefig("sample_output.png", dpi=120)
