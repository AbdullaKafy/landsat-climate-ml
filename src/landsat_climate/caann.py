"""Cellular automata with an artificial neural network (CA-ANN).

Two parts, as in common CA-ANN land change models:
1. Quantity: a Markov chain from the last observed period says how many pixels
   each class should have at the next step.
2. Location: a neural network gives each pixel a suitability score for each
   class, using its current class, its neighbors and elevation. Pixels are
   assigned to classes from the highest score down until each class reaches
   its quantity.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CLASSES = (1, 2, 3, 4)


def neighbor_fractions(lulc: np.ndarray, size: int = 5) -> np.ndarray:
    """Share of each class in a size x size window around every pixel."""
    valid = (lulc > 0).astype("float32")
    vfrac = uniform_filter(valid, size=size, mode="nearest")
    out = []
    for c in CLASSES:
        f = uniform_filter((lulc == c).astype("float32"), size=size, mode="nearest")
        with np.errstate(invalid="ignore", divide="ignore"):
            out.append(np.where(vfrac > 0, f / vfrac, 0.0))
    return np.stack(out, axis=-1)


def features(lulc: np.ndarray, dem: np.ndarray, size: int = 5) -> np.ndarray:
    """Per-pixel features: current class (one-hot), neighbor shares, elevation."""
    onehot = np.stack([(lulc == c) for c in CLASSES], axis=-1).astype("float32")
    nb = neighbor_fractions(lulc, size)
    return np.concatenate([onehot, nb, dem[..., None].astype("float32")], axis=-1)


def transition_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Row-normalized Markov matrix: P[i, j] = share of class i at t1 that is class j at t2."""
    m = (a > 0) & (b > 0)
    k = len(CLASSES)
    counts = np.zeros((k, k))
    for i, ci in enumerate(CLASSES):
        for j, cj in enumerate(CLASSES):
            counts[i, j] = np.sum((a[m] == ci) & (b[m] == cj))
    rows = counts.sum(axis=1, keepdims=True)
    return np.divide(counts, rows, out=np.eye(k), where=rows > 0)


class CAANN:
    """Fit on one change period, then simulate later dates."""

    def __init__(self, neighborhood: int = 5, hidden=(32, 16), seed: int = 0):
        self.size = neighborhood
        self.model = make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=hidden, max_iter=400, early_stopping=True,
                          random_state=seed),
        )
        self.seed = seed

    def fit(self, lulc_t0, lulc_t1, dem, max_samples: int = 40_000):
        m = (lulc_t0 > 0) & (lulc_t1 > 0) & np.isfinite(dem)
        X = features(lulc_t0, np.nan_to_num(dem), self.size)[m]
        y = lulc_t1[m]
        rng = np.random.default_rng(self.seed)
        idx = rng.choice(len(y), size=min(max_samples, len(y)), replace=False)
        self.model.fit(X[idx], y[idx])
        return self

    def step(self, lulc, dem, matrix, protect_water: bool = True):
        """One step forward in time with class totals set by `matrix`."""
        m = lulc > 0
        X = features(lulc, np.nan_to_num(dem), self.size)[m]
        proba = self.model.predict_proba(X)  # columns follow self.model.classes_
        cols = list(self.model.classes_)
        cur = lulc[m]
        counts = np.array([np.sum(cur == c) for c in CLASSES], dtype=float)
        target = np.round(counts @ matrix).astype(int)
        target[-1] += len(cur) - target.sum()  # keep the total pixel count

        n = len(cur)
        score = np.zeros((n, len(CLASSES)))
        for j, c in enumerate(CLASSES):
            if c in cols:
                score[:, j] = proba[:, cols.index(c)]
        assigned = np.zeros(n, dtype="uint8")
        quota = target.copy()
        if protect_water:  # open water stays water
            w = cur == 1
            assigned[w] = 1
            quota[0] -= w.sum()
        order = np.argsort(-score, axis=None)
        pix, cls = np.unravel_index(order, score.shape)
        for p, j in zip(pix, cls, strict=True):
            if assigned[p] == 0 and quota[j] > 0:
                assigned[p] = CLASSES[j]
                quota[j] -= 1
        left = assigned == 0  # any pixel left keeps its class
        assigned[left] = cur[left]
        out = np.zeros_like(lulc)
        out[m] = assigned
        return out


def kappa(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Overall agreement and Cohen's kappa between two class maps."""
    m = (a > 0) & (b > 0)
    a, b = a[m], b[m]
    po = float(np.mean(a == b))
    pe = sum(float(np.mean(a == c)) * float(np.mean(b == c)) for c in CLASSES)
    return po, (po - pe) / (1 - pe)


def chi_square_validation(actual: np.ndarray, simulated: np.ndarray,
                          pixel_area_m2: float = 900.0) -> dict:
    """Compare class areas of an actual and a simulated map with Pearson's chi-square.

    Returns per-class O, E, (O - E)^2 / E in km², the chi-square statistic and
    its p-value (degrees of freedom = number of classes - 1).
    """
    from scipy.stats import chi2

    o = np.array([np.sum(actual == c) for c in CLASSES], dtype=float) * pixel_area_m2 / 1e6
    e = np.array([np.sum(simulated == c) for c in CLASSES], dtype=float) * pixel_area_m2 / 1e6
    with np.errstate(divide="ignore", invalid="ignore"):
        parts = np.where(e > 0, (o - e) ** 2 / e, 0.0)
    stat = float(parts.sum())
    return {"observed_km2": o, "expected_km2": e, "parts": parts, "chi_square": stat,
            "p_value": float(chi2.sf(stat, df=len(CLASSES) - 1))}
