"""Seasonal UTFVI now and in the future, as in Kafy et al. (2021), Cumilla.

What it shows: land cover maps for two dates, summer and winter LST, the six
UTFVI classes (Fig. 8, Table 7), a CA-ANN land cover forecast and an ANN that
predicts LST and so UTFVI for the next two steps (Fig. 14, Table 13).
Synthetic data: numbers will not match the paper.
Run: python papers/2021-scs-cumilla-seasonal-utfvi/sample.py [--plot]
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import caann, lstmodel, thermal

rng = np.random.default_rng(42)
N = 120  # 120 x 120 pixels of 30 m
yy, xx = np.mgrid[:N, :N]
dist = np.hypot(yy - N / 2, xx - N / 2) + rng.normal(0, 6, (N, N))
soil = rng.random((N, N))
dem = 10 + 0.05 * yy + rng.normal(0, 0.5, (N, N))
CLASS_LST = {1: 24.0, 2: 34.0, 3: 27.0, 4: 30.0}  # summer mean LST (°C) per class


def land_cover(radius):
    """1 water, 2 built-up, 3 vegetation, 4 bare land."""
    lc = np.where(soil > 0.6, 4, 3).astype("uint8")
    lc[dist < radius] = 2
    lc[np.abs(yy - 0.3 * xx - 80) < 3] = 1  # a river
    return lc


def utfvi_km2(values):
    cls = thermal.classify_utfvi(values)
    return {c: np.sum(cls == c) * 900 / 1e6 for c in thermal.UTFVI_CLASSES}


lc_2009, lc_2019 = land_cover(28), land_cover(38)
ca = caann.CAANN(neighborhood=3, seed=0).fit(lc_2009, lc_2019, dem)
markov = caann.transition_matrix(lc_2009, lc_2019)
lc_2029 = ca.step(lc_2019, dem, markov)
lc_2039 = ca.step(lc_2029, dem, markov)

rows, maps = {}, {}
for season, shift in (("Summer", 0.0), ("Winter", -9.0)):
    lst_2019 = np.vectorize(CLASS_LST.get)(lc_2019) + shift + rng.normal(0, 1.0, (N, N))
    model, score = lstmodel.fit_lst_model(lc_2019, dem, lst_2019, n_splits=3)
    print(f"{season} ANN check: R2 = {score['r2']:.2f}, RMSE = {score['rmse']:.2f} °C")
    rows[f"{season} 2019"] = utfvi_km2(thermal.utfvi(lst_2019))  # (Ts - Tm) / Ts
    for year, lc in ((2029, lc_2029), (2039, lc_2039)):
        ts = lstmodel.predict_lst(model, lc, dem) + 273.15  # Kelvin
        # Same (Ts - Tm) / Ts, but Tm stays at the 2019 mean so future warming shows
        maps[f"{season} {year}"] = (ts - (lst_2019.mean() + 273.15)) / ts
        rows[f"{season} {year}"] = utfvi_km2(maps[f"{season} {year}"])

print("\nUTFVI class area (km²), observed 2019 and predicted 2029, 2039")
print(pd.DataFrame(rows).round(2).to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(8, 7))
    for ax, (name, values) in zip(axes.ravel(), maps.items(), strict=True):
        im = ax.imshow(values, cmap="RdYlGn_r", vmin=-0.02, vmax=0.03)
        ax.set_title(f"Predicted UTFVI, {name}"), ax.axis("off")
    fig.colorbar(im, ax=axes, shrink=0.7, label="UTFVI")
    fig.savefig("sample_output.png", dpi=120)
