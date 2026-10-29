"""Predict future land cover with a CA model and read it by direction.

Relates to Fig. 10 (predicted 2025 and 2035 maps read with 16 direction rays) and
Tables 2 and 3 (kappa and chi-square checks). A Markov matrix sets how much of each
class there will be; a cellular automata model with a neural network (CA-ANN)
decides where. The model is checked on a known map before it is run forward.

Synthetic data: numbers will not match the paper.
"""

import argparse

import numpy as np
import pandas as pd

from landsat_climate import caann, zones

# Classes: 1 water, 2 built-up, 3 forest, 4 agriculture
rng = np.random.default_rng(42)
n = 120
rr, cc = np.indices((n, n))
dist = np.hypot(rr - 60, cc - 60)
dem = 2.0 * np.maximum(0, cc - 70) + rng.normal(0, 3, (n, n))  # hills in the east
score = -dist + rng.normal(0, 8, (n, n))  # where built-up appears first


def make_map(built_share):  # built-up grows out from the center; forest on hills; a lake
    lulc = np.full((n, n), 4, dtype="uint8")
    lulc[dem > 60] = 3
    lulc[score > np.quantile(score, 1 - built_share)] = 2
    lulc[np.hypot(rr - 95, cc - 30) < 8] = 1
    return lulc


maps = {2010: make_map(0.20), 2015: make_map(0.27), 2020: make_map(0.34)}

# Fit on 2010 to 2015, simulate 2020, compare with the "actual" 2020 map
model = caann.CAANN(neighborhood=5, seed=0).fit(maps[2010], maps[2015], dem)
m_fit = caann.transition_matrix(maps[2010], maps[2015])
sim2020 = model.step(maps[2015], dem, m_fit)
agree, kappa = caann.kappa(maps[2020], sim2020)
chi = caann.chi_square_validation(maps[2020], sim2020)
print(f"Check 2020: agreement {agree:.3f}, kappa {kappa:.3f}, chi-square {chi['chi_square']:.3f}")

# Run forward from 2020 in 5-year steps to 2025 and 2035
model = caann.CAANN(neighborhood=5, seed=0).fit(maps[2015], maps[2020], dem)
m_next = caann.transition_matrix(maps[2015], maps[2020])
pred = {2025: model.step(maps[2020], dem, m_next)}
pred[2030] = model.step(pred[2025], dem, m_next)
pred[2035] = model.step(pred[2030], dem, m_next)

# Built-up share in each of 16 direction rays
sectors = zones.directional_sectors((n, n), (60, 60), n=16)
every = {**maps, **pred}
rows = {y: zones.share_by_zone(every[y], sectors, 2) for y in (2020, 2025, 2035)}
table = pd.DataFrame(rows).round(1)
table.index = "N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW".split()
print("\nBuilt-up share (%) by direction sector")
print(table.to_string())

parser = argparse.ArgumentParser()
parser.add_argument("--plot", action="store_true", help="save sample_output.png")
if parser.parse_args().plot:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    for ax, y in zip(axes, (2020, 2025, 2035), strict=True):
        ax.imshow(every[y], cmap="tab10", vmin=1, vmax=4)
        ax.set_title(str(y))
        ax.axis("off")
    fig.savefig("sample_output.png", dpi=120, bbox_inches="tight")
