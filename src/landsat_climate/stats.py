"""Small statistics helpers used across the papers."""

from __future__ import annotations

import numpy as np


def correlation(x, y) -> dict:
    """Pearson r, R² and the least-squares line (slope, intercept), ignoring NaN."""
    from scipy.stats import pearsonr

    x = np.asarray(x, dtype="float64").ravel()
    y = np.asarray(y, dtype="float64").ravel()
    m = np.isfinite(x) & np.isfinite(y)
    r, p = pearsonr(x[m], y[m])
    slope, intercept = np.polyfit(x[m], y[m], 1)
    return {"r": float(r), "r2": float(r * r), "p": float(p), "slope": float(slope),
            "intercept": float(intercept), "n": int(m.sum())}


def roc_auc(y_true, score) -> float:
    """Area under the ROC curve for a binary target."""
    from sklearn.metrics import roc_auc_score

    return float(roc_auc_score(np.asarray(y_true).ravel(), np.asarray(score).ravel()))


def cross_profile(raster: np.ndarray, start_rc, end_rc, n: int | None = None) -> np.ndarray:
    """Values sampled along a straight line (nearest pixel), for profile plots."""
    (r0, c0), (r1, c1) = start_rc, end_rc
    n = n or int(np.hypot(r1 - r0, c1 - c0)) + 1
    rr = np.rint(np.linspace(r0, r1, n)).astype(int)
    cc = np.rint(np.linspace(c0, c1, n)).astype(int)
    return np.asarray(raster)[rr, cc]


def rmse(observed, predicted) -> float:
    """Root mean square error, ignoring NaN."""
    o = np.asarray(observed, dtype="float64").ravel()
    p = np.asarray(predicted, dtype="float64").ravel()
    m = np.isfinite(o) & np.isfinite(p)
    return float(np.sqrt(np.mean((o[m] - p[m]) ** 2)))


def crosstab(a, b, percent: str | None = "row"):
    """Cross-table of two class maps, e.g. UTFVI class within each land cover class.

    percent: "row" (each row sums to 100), "all", or None for pixel counts.
    """
    import pandas as pd

    a = np.asarray(a).ravel()
    b = np.asarray(b).ravel()
    m = pd.notna(a) & pd.notna(b)
    t = pd.crosstab(a[m], b[m])
    if percent == "row":
        t = 100 * t.div(t.sum(axis=1), axis=0)
    elif percent == "all":
        t = 100 * t / t.values.sum()
    return t


def pca_loadings(table, n_components: int = 2):
    """PCA on mean-centered columns. Loadings = eigenvector x sqrt(eigenvalue).

    `table` is a pandas DataFrame with one column per variable. Returns the
    loadings (variables x components) and the share of variance explained.
    """
    import pandas as pd
    from sklearn.decomposition import PCA

    x = table - table.mean()
    p = PCA(n_components=n_components).fit(x.values)
    load = p.components_.T * np.sqrt(p.explained_variance_)
    cols = [f"PC{i + 1}" for i in range(n_components)]
    return pd.DataFrame(load, index=table.columns, columns=cols), p.explained_variance_ratio_
