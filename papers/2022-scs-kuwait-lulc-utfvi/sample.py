"""From thermal band to UTFVI classes, now and for 2031, as in AlDousari et al. (2022), Kuwait.

What it shows: brightness temperature and NDVI give emissivity (NDVI thresholds)
and single-channel LST. LST gives UHI and the six UTFVI classes per year
(Fig. 8, Table 6). A CA-ANN land cover forecast and an ANN for LST then give
the UTFVI classes for 2031 (Fig. 14, Fig. 15).
Synthetic data: numbers will not match the paper.
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import caann, lstmodel, thermal

rng = np.random.default_rng(3)
N = 120  # 120 x 120 pixels of 30 m
yy, xx = np.mgrid[:N, :N]
dist = np.hypot(yy - 40, xx - 80) + rng.normal(0, 8, (N, N))  # city near the coast
dem = 60 - 0.4 * xx + rng.normal(0, 1, (N, N))  # land slopes down to the Gulf
green = rng.random((N, N)) < 0.08  # scattered irrigated green
NDVI = {1: -0.3, 2: 0.08, 3: 0.45, 4: 0.03}  # water, built-up, vegetation, bare land
BT_K = {1: 300.0, 2: 316.0, 3: 304.0, 4: 312.0}  # band 10 brightness temperature


def land_cover(radius):
    lc = np.full((N, N), 4, dtype="uint8")
    lc[green & (dist < radius + 15)] = 3
    lc[dist < radius] = 2
    lc[xx > 105] = 1  # the Gulf
    return lc


def lst_map(lc):
    ndvi = np.vectorize(NDVI.get)(lc) + rng.normal(0, 0.03, lc.shape)
    bt = np.vectorize(BT_K.get)(lc) + rng.normal(0, 1.0, lc.shape)
    return thermal.lst_from_bt(bt, thermal.emissivity_ndvi_thresholds(ndvi), wavelength_um=10.9)


lc, lst, u = {}, {}, {}
for year, radius in {1991: 12, 2001: 20, 2011: 28, 2021: 36}.items():
    lc[year] = land_cover(radius)
    lst[year] = lst_map(lc[year])
    u[year], h = thermal.utfvi(lst[year]), thermal.uhi(lst[year])
    print(f"{year}: LST {lst[year].min():.1f} to {lst[year].max():.1f} °C, "
          f"UHI {h.min():.2f} to {h.max():.2f}")

ca = caann.CAANN(neighborhood=3, seed=0).fit(lc[2011], lc[2021], dem)
lc[2031] = ca.step(lc[2021], dem, caann.transition_matrix(lc[2011], lc[2021]))
model, score = lstmodel.fit_lst_model(lc[2021], dem, lst[2021], n_splits=3)
print(f"ANN check on 2021: R2 = {score['r2']:.2f}, RMSE = {score['rmse']:.2f} °C")
ts = lstmodel.predict_lst(model, lc[2031], dem) + 273.15
u[2031] = (ts - (lst[2021].mean() + 273.15)) / ts  # Tm fixed at 2021 so warming shows
rows = {y: {c: 100 * np.mean(thermal.classify_utfvi(v) == c) for c in thermal.UTFVI_CLASSES}
        for y, v in u.items()}
print("\nUTFVI class share (% of area); 2031 is predicted")
print(pd.DataFrame(rows).round(2).to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    for ax, year in zip(axes, (2001, 2021, 2031), strict=True):
        im = ax.imshow(u[year], cmap="RdYlGn_r", vmin=-0.03, vmax=0.03)
        ax.set_title(f"UTFVI, {year}" + (" (predicted)" if year == 2031 else ""), fontsize=10)
        ax.set_axis_off()
    fig.colorbar(im, ax=axes, shrink=0.8, label="UTFVI")
    fig.savefig("sample_output.png", dpi=120)
