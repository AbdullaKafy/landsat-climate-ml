"""Summer UTFVI over time and in the future, as in Kafy et al. (2022), Sylhet.

What it shows: a city that grows every five years, its summer LST and the six
UTFVI classes per year (Fig. 8, Fig. 10), then a CA-ANN land cover forecast and
an ANN that predicts summer UTFVI for 2025 and 2030 (Fig. 16, Fig. 17).
This paper divides by the mean temperature, so we use denominator="tmean".
Synthetic data: numbers will not match the paper.
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import caann, lstmodel, thermal

rng = np.random.default_rng(7)
N = 120  # 120 x 120 pixels of 30 m
yy, xx = np.mgrid[:N, :N]
dist = np.hypot(yy - N / 2, xx - N / 2) + rng.normal(0, 6, (N, N))
soil = rng.random((N, N))
dem = 15 + 0.08 * yy + rng.normal(0, 0.5, (N, N))
CLASS_LST = {1: 24.0, 2: 32.0, 3: 26.0, 4: 29.0}  # summer mean LST (°C) per class
YEARS = {1995: 18, 2000: 22, 2005: 26, 2010: 30, 2015: 34, 2020: 38}  # built-up radius


def land_cover(radius):
    """1 water, 2 built-up, 3 vegetation, 4 bare land."""
    lc = np.where(soil > 0.7, 4, 3).astype("uint8")
    lc[dist < radius] = 2
    lc[np.abs(yy - 0.4 * xx - 75) < 3] = 1  # the Surma river
    return lc


def class_pct(values):  # percent of the city in each of the six UTFVI classes
    return {c: 100 * np.mean(thermal.classify_utfvi(values) == c) for c in thermal.UTFVI_CLASSES}


rows, lc, lst, u = {}, {}, {}, {}
for year, radius in YEARS.items():
    lc[year] = land_cover(radius)
    lst[year] = np.vectorize(CLASS_LST.get)(lc[year]) + rng.normal(0, 1.0, (N, N))
    u[year] = thermal.utfvi(lst[year], denominator="tmean")
    rows[year] = class_pct(u[year])

ca = caann.CAANN(neighborhood=3, seed=0).fit(lc[2015], lc[2020], dem)
markov = caann.transition_matrix(lc[2015], lc[2020])
model, score = lstmodel.fit_lst_model(lc[2020], dem, lst[2020], n_splits=3)
print(f"ANN check on 2020: R2 = {score['r2']:.2f}, RMSE = {score['rmse']:.2f} °C")
future, t_ref = lc[2020], lst[2020].mean() + 273.15
for year in (2025, 2030):
    future = ca.step(future, dem, markov)
    ts = lstmodel.predict_lst(model, future, dem) + 273.15
    u[year] = (ts - t_ref) / t_ref  # Tm fixed at the 2020 mean so warming shows
    rows[year] = class_pct(u[year])

print("\nSummer UTFVI class share (% of city); 2025 and 2030 are predicted")
print(pd.DataFrame(rows).round(1).to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    for ax, year in zip(axes, (2020, 2025, 2030), strict=True):
        im = ax.imshow(u[year], cmap="RdYlGn_r", vmin=-0.02, vmax=0.03)
        ax.set_title(f"UTFVI, {year}" + (" (predicted)" if year > 2020 else ""), fontsize=10)
        ax.set_axis_off()
    fig.colorbar(im, ax=axes, shrink=0.8, label="UTFVI")
    fig.savefig("sample_output.png", dpi=120)
