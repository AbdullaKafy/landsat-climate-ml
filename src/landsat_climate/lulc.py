"""Land use / land cover (LULC) classification across years and sensors.

A Random Forest is trained on the 2019 composites, with labels from ESA
WorldCover 2020, then applied to 1999 and 2009.

Landsat 5 (1999, 2009) and Landsat 8 (2019) measure slightly different
reflectance for the same surface. To make one model work for all years, each
feature is standardized within its own year (median 0, interquartile range 1)
before training and prediction. This "relative normalization" assumes the
overall spread of surfaces in the study area is similar between years. It
removes sensor offsets but can also hide real area-wide change, so the class
shares for 1999 and 2009 should be read as estimates.
"""

from __future__ import annotations

import numpy as np
import xarray as xr
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import cohen_kappa_score, confusion_matrix

from landsat_climate.indices import mndwi, ndbi, ndvi

CLASSES = {1: "Water", 2: "Built-up", 3: "Vegetation", 4: "Cropland and bare"}
COLORS = {1: "#3b7dd8", 2: "#c2533a", 3: "#2f6b3a", 4: "#d8c38a"}
BANDS = ("blue", "green", "red", "nir08", "swir16", "swir22")

# ESA WorldCover 2020 code -> class used here
WORLDCOVER_MAP = {80: 1, 50: 2, 10: 3, 20: 3, 30: 3, 90: 3, 95: 3, 40: 4, 60: 4}


def worldcover_labels(wc: np.ndarray) -> np.ndarray:
    out = np.zeros(wc.shape, dtype="uint8")
    for code, cls in WORLDCOVER_MAP.items():
        out[wc == code] = cls
    return out


def features(comp: xr.Dataset, year: int) -> np.ndarray:
    """Bands and indices for winter and summer, standardized within the year."""
    cols = []
    for season in ("winter", "summer"):
        d = comp.sel(year=year, season=season)
        v = {b: d[b].values for b in BANDS}
        cols += [v[b] for b in BANDS]
        cols += [ndvi(v["nir08"], v["red"]), ndbi(v["swir16"], v["nir08"]),
                 mndwi(v["green"], v["swir16"])]
    X = np.stack(cols, axis=-1).astype("float32")
    med = np.nanmedian(X, axis=(0, 1))
    iqr = np.nanpercentile(X, 75, axis=(0, 1)) - np.nanpercentile(X, 25, axis=(0, 1))
    return (X - med) / np.where(iqr > 0, iqr, 1)


def spatial_blocks(shape, block: int = 40) -> np.ndarray:
    h, w = shape
    return (np.arange(h)[:, None] // block) * 10_000 + (np.arange(w)[None, :] // block)


def train_classifier(X: np.ndarray, labels: np.ndarray, holdout: float = 0.25, seed: int = 0):
    """Fit a Random Forest and report accuracy on held-out spatial blocks.

    Returns the model refit on all labeled pixels, plus a dict with overall
    accuracy, kappa and the confusion matrix from the spatial holdout.
    """
    m = labels > 0
    blk = spatial_blocks(labels.shape)
    ub = np.unique(blk)
    rng = np.random.default_rng(seed)
    test = np.isin(blk, rng.choice(ub, int(len(ub) * holdout), replace=False))

    def make():
        return RandomForestClassifier(n_estimators=300, min_samples_leaf=3, n_jobs=-1,
                                      random_state=seed, class_weight="balanced_subsample")

    rf = make().fit(X[m & ~test], labels[m & ~test])
    pred = rf.predict(X[m & test])
    truth = labels[m & test]
    report = {
        "overall_accuracy": float(np.mean(pred == truth)),
        "kappa": float(cohen_kappa_score(truth, pred)),
        "confusion": confusion_matrix(truth, pred, labels=list(CLASSES)),
        "n_test": int(len(truth)),
    }
    return make().fit(X[m], labels[m]), report


def classify(model, X: np.ndarray) -> np.ndarray:
    h, w, k = X.shape
    return model.predict(X.reshape(-1, k)).reshape(h, w).astype("uint8")


def class_shares(lulc: np.ndarray) -> dict:
    """Percent of valid pixels in each class."""
    v = lulc[lulc > 0]
    return {CLASSES[c]: 100 * float(np.mean(v == c)) for c in CLASSES}


def class_areas(lulc: np.ndarray, pixel_area_m2: float = 900.0, names: dict = CLASSES) -> dict:
    """Area (km²) of each class."""
    return {n: float(np.sum(lulc == c)) * pixel_area_m2 / 1e6 for c, n in names.items()}


def accuracy(truth: np.ndarray, pred: np.ndarray, names: dict = CLASSES) -> dict:
    """Overall accuracy, kappa, and producer's and user's accuracy per class.

    Producer's accuracy = correct / reference total (omission side).
    User's accuracy = correct / mapped total (commission side).
    """
    truth = np.asarray(truth).ravel()
    pred = np.asarray(pred).ravel()
    codes = list(names)
    cm = confusion_matrix(truth, pred, labels=codes)
    diag = np.diag(cm).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        prod = diag / cm.sum(axis=1)
        user = diag / cm.sum(axis=0)
    return {
        "overall_accuracy": float(diag.sum() / cm.sum()),
        "kappa": float(cohen_kappa_score(truth, pred, labels=codes)),
        "producer": dict(zip(names.values(), prod.round(4).tolist(), strict=True)),
        "user": dict(zip(names.values(), user.round(4).tolist(), strict=True)),
        "confusion": cm,
    }


def change_matrix(before: np.ndarray, after: np.ndarray, pixel_area_m2: float = 900.0,
                  names: dict = CLASSES):
    """From-to change matrix in km² (rows: before, columns: after)."""
    import pandas as pd

    codes = list(names)
    m = np.zeros((len(codes), len(codes)))
    for i, a in enumerate(codes):
        for j, b in enumerate(codes):
            m[i, j] = np.sum((before == a) & (after == b)) * pixel_area_m2 / 1e6
    return pd.DataFrame(m, index=list(names.values()), columns=list(names.values()))


def gain_loss(before: np.ndarray, after: np.ndarray, pixel_area_m2: float = 900.0,
              names: dict = CLASSES):
    """Gain, loss and net change (km²) for each class between two maps."""
    import pandas as pd

    cm = change_matrix(before, after, pixel_area_m2, names)
    stay = np.diag(cm.values)
    gain = cm.sum(axis=0).values - stay
    loss = cm.sum(axis=1).values - stay
    return pd.DataFrame({"gain_km2": gain, "loss_km2": -loss, "net_km2": gain - loss},
                        index=cm.index)


def expansion_indices(area_t1_km2: float, area_t2_km2: float, years: float,
                      total_area_km2: float) -> dict:
    """Urban expansion speed (km² per year) and intensity (% of total area per year)."""
    d = area_t2_km2 - area_t1_km2
    return {"speed_km2_per_year": d / years,
            "intensity_pct_per_year": 100 * d / (total_area_km2 * years)}
