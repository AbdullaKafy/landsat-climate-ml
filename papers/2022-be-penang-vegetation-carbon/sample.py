"""Normalized UHI maps and tree carbon stock linked to LST and UHI.

Relates to Fig. 6 (UHI maps), Fig. 8 (carbon stock maps) and Tables 5 and 6
(carbon against LST and UHI, N = 46 points per year). UHI = (LST - mean) / SD.
Carbon stock per point uses the paper's allometric equation,
AGB (kg) = 0.0673 * (rho * DBH^2 * H)^0.976 with rho = 1.54, and carbon = 0.5 * AGB.
The paper turns stock into emission; this sample stops at stock, so r is negative.

Synthetic data: numbers will not match the paper.
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import stats, thermal

rng = np.random.default_rng(11)
n = 90
rr, cc = np.indices((n, n))
city = np.exp(-((rr - 40) ** 2 + (cc - 35) ** 2) / 600)  # built-up core
hot = np.exp(-((rr - 70) ** 2 + (cc - 65) ** 2) / 40)  # small industrial hot spot
pts = rng.integers(0, n, size=(46, 2))  # 46 sample points, as in the paper

rows, uhi_maps = [], {}
for k, year in enumerate((1996, 2006, 2016, 2021)):
    growth = 1 + 0.5 * k  # the city spreads and warms over time
    urban = np.clip(city * growth, 0, 1)
    lst = 22 + 1.6 * k + 7 * urban + 3 * k * hot + rng.normal(0, 0.8, (n, n))
    uhi = thermal.uhi(lst)
    uhi_maps[year] = uhi

    u = urban[pts[:, 0], pts[:, 1]]
    dbh = np.clip(45 * (1 - 0.7 * u) + rng.normal(0, 4, 46), 5, None)  # cm
    height = np.clip(22 * (1 - 0.6 * u) + rng.normal(0, 2, 46), 3, None)  # m
    agb = 0.0673 * (1.54 * dbh**2 * height) ** 0.976  # kg
    stock = 0.5 * agb  # kg C per point

    r_lst = stats.correlation(stock, lst[pts[:, 0], pts[:, 1]])
    # UHI is a linear rescale of LST within one year, so both r values match here
    r_uhi = stats.correlation(stock, uhi[pts[:, 0], pts[:, 1]])
    rows.append({"year": year, "mean LST C": lst.mean(), "UHI max": uhi.max(),
                 "UHI min": uhi.min(), "mean stock kg C": stock.mean(),
                 "r stock-LST": r_lst["r"], "r stock-UHI": r_uhi["r"], "N": r_lst["n"]})

table = pd.DataFrame(rows).set_index("year").round(3)
print(table.to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.6))
    for ax, (year, uhi) in zip(axes, uhi_maps.items(), strict=True):
        im = ax.imshow(uhi, cmap="viridis", vmin=-2.5, vmax=3.5)
        ax.set_title(f"UHI {year}")
        ax.axis("off")
    fig.colorbar(im, ax=axes)
    fig.savefig("sample_output.png", dpi=120, bbox_inches="tight")
