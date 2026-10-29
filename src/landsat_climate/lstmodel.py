"""Predict seasonal land surface temperature (LST) from land cover.

An artificial neural network (multilayer perceptron) learns how LST depends on
a pixel's land cover, the land cover around it and elevation. Trained on one
year, it can then estimate LST for a simulated future land cover map. The
model holds the climate of the training year fixed: it shows the effect of
land cover change alone, not of regional warming.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from landsat_climate.caann import CLASSES, neighbor_fractions
from landsat_climate.lulc import spatial_blocks


def lst_features(lulc: np.ndarray, dem: np.ndarray) -> np.ndarray:
    """Class (one-hot), class shares in 5x5 and 15x15 windows, elevation."""
    onehot = np.stack([(lulc == c) for c in CLASSES], axis=-1).astype("float32")
    return np.concatenate(
        [onehot, neighbor_fractions(lulc, 5), neighbor_fractions(lulc, 15),
         np.nan_to_num(dem)[..., None].astype("float32")],
        axis=-1,
    )


def _model(seed: int):
    return make_pipeline(
        StandardScaler(),
        MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, early_stopping=True,
                     random_state=seed),
    )


def fit_lst_model(lulc, dem, lst, seed: int = 0, n_splits: int = 5):
    """Fit the ANN and score it with spatial block cross-validation.

    Returns the model fit on all pixels and a dict with mean R2 and RMSE (°C).
    """
    X = lst_features(lulc, dem)
    m = (lulc > 0) & np.isfinite(lst)
    Xm, ym = X[m], lst[m]
    groups = spatial_blocks(lulc.shape)[m]
    r2s, rmses = [], []
    for tr, te in GroupKFold(n_splits=n_splits).split(Xm, ym, groups):
        mdl = _model(seed).fit(Xm[tr], ym[tr])
        p = mdl.predict(Xm[te])
        r2s.append(r2_score(ym[te], p))
        rmses.append(float(np.sqrt(mean_squared_error(ym[te], p))))
    model = _model(seed).fit(Xm, ym)
    return model, {"r2": float(np.mean(r2s)), "rmse": float(np.mean(rmses))}


def predict_lst(model, lulc, dem) -> np.ndarray:
    X = lst_features(lulc, dem)
    out = np.full(lulc.shape, np.nan, dtype="float32")
    m = lulc > 0
    out[m] = model.predict(X[m])
    return out
