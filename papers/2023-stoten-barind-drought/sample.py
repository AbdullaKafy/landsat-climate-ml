"""VHI drought maps and a CA-ANN drought forecast, as in Figs. 12 and 17 of the Barind paper.

What it shows: VCI and TCI are computed from a stack of yearly NDVI and LST maps,
combined into VHI, and put into five drought classes (Table 7, Fig. 12). Then a
CA-ANN model learns the 2016 to 2021 change and predicts the next step (Fig. 17).
The toolkit CA-ANN works with four classes, so Extreme and Severe are merged here.

Synthetic data: numbers will not match the paper.
Run: python papers/2023-stoten-barind-drought/sample.py [--plot]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from landsat_climate import caann, drought

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
args = parser.parse_args()

rng = np.random.default_rng(7)
years = [1996, 2001, 2006, 2011, 2016, 2021]
shape = (80, 80)
dem = np.add.outer(np.linspace(10, 45, shape[0]), np.zeros(shape[1]))  # meters
trend = np.arange(len(years))[:, None, None]
west = np.linspace(1, 0, shape[1])[None, None, :]  # the west side dries out faster
patch = rng.normal(0, 0.05, shape)  # fixed local pattern, plus small noise each year
ndvi = 0.55 - 0.03 * trend * west + patch + rng.normal(0, 0.02, (len(years), *shape))
lst = 27 + 0.6 * trend * west - 10 * patch + rng.normal(0, 0.5, (len(years), *shape))
ndvi[ndvi < 0.2] = np.nan  # paper: NDVI < 0.2 set to No Data

vci, tci, vhi = drought.from_stack(ndvi, lst)  # min and max over all years per pixel
rows = {}
for i, y in enumerate(years):
    cls = pd.Series(drought.classify_vhi(vhi[i]).ravel()).dropna()
    rows[y] = (100 * cls.value_counts(normalize=True)).reindex(drought.VHI_CLASSES).fillna(0)
print("Share of area in each VHI drought class (%)")
print(pd.DataFrame(rows).T.round(1).to_string())

# Codes for CA-ANN: 1 Extreme or Severe, 2 Moderate, 3 Mild, 4 No drought.
codes = np.select([vhi < 20, vhi < 30, vhi < 40, vhi >= 40], [1, 2, 3, 4], 0).astype("uint8")
d2016, d2021 = codes[4], codes[5]
matrix = caann.transition_matrix(d2016, d2021)
model = caann.CAANN(neighborhood=3, hidden=(8,), seed=0).fit(d2016, d2021, dem)
d2026 = model.step(d2021, dem, matrix, protect_water=False)
share = {c: [100 * np.mean(m[m > 0] == c) for m in (d2021, d2026)] for c in (1, 2, 3, 4)}
labels = ["Extreme+Severe", "Moderate", "Mild", "No drought"]
print("\nCA-ANN forecast, share of area (%)")
print(pd.DataFrame(share, index=["2021", "2026"]).set_axis(labels, axis=1).round(1).to_string())

if args.plot:
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    for ax, m, t in zip(axes, (d2021, d2026), ("2021 (from VHI)", "2026 (CA-ANN)"), strict=True):
        ax.imshow(np.where(m > 0, m, np.nan), cmap="RdYlGn", vmin=1, vmax=4)
        ax.set_title(t)
        ax.set_axis_off()
    fig.savefig("sample_output.png", dpi=120, bbox_inches="tight")
    print("Saved sample_output.png")
