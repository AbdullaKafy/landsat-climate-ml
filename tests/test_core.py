"""Offline tests on small synthetic arrays (no downloads needed)."""

import numpy as np

from landsat_climate.caann import CAANN, kappa, neighbor_fractions, transition_matrix
from landsat_climate.indices import ndvi
from landsat_climate.lulc import class_shares, spatial_blocks, worldcover_labels
from landsat_climate.thermal import UTFVI_CLASSES, classify_utfvi, utfvi


def test_ndvi_range():
    assert np.isclose(ndvi(0.5, 0.1), 0.4 / 0.6)
    assert np.isclose(ndvi(0.2, 0.2), 0.0)


def test_utfvi_mean_is_near_zero():
    lst = np.array([[30.0, 32.0], [34.0, 36.0]])
    u = utfvi(lst)
    assert abs(np.mean(u)) < 1e-3
    assert u[1, 1] > 0 > u[0, 0]


def test_utfvi_classes():
    out = classify_utfvi([-0.01, 0.003, 0.007, 0.012, 0.017, 0.03, np.nan])
    assert list(out[:6]) == list(UTFVI_CLASSES)
    assert out[6] is None


def test_worldcover_mapping():
    wc = np.array([[80, 50], [10, 40]])
    assert worldcover_labels(wc).tolist() == [[1, 2], [3, 4]]


def test_class_shares_sum_to_100():
    lulc = np.array([[1, 2], [3, 4]])
    assert np.isclose(sum(class_shares(lulc).values()), 100)


def test_spatial_blocks():
    b = spatial_blocks((80, 80), block=40)
    assert len(np.unique(b)) == 4


def test_neighbor_fractions_sum_to_one():
    rng = np.random.default_rng(0)
    lulc = rng.integers(1, 5, size=(20, 20))
    f = neighbor_fractions(lulc, 5)
    assert np.allclose(f.sum(axis=-1), 1)


def test_transition_matrix_rows():
    a = np.array([[1, 2], [3, 4]])
    p = transition_matrix(a, a)
    assert np.allclose(p, np.eye(4))
    assert np.allclose(p.sum(axis=1), 1)


def test_kappa_perfect():
    a = np.array([[1, 2], [3, 4]])
    po, k = kappa(a, a)
    assert po == 1 and np.isclose(k, 1)


def test_caann_step_meets_quotas():
    rng = np.random.default_rng(1)
    t0 = rng.integers(1, 5, size=(40, 40)).astype("uint8")
    t1 = t0.copy()
    t1[(t0 == 4) & (rng.random(t0.shape) < 0.3)] = 2  # some cropland becomes built-up
    dem = rng.random(t0.shape).astype("float32")
    p = transition_matrix(t0, t1)
    model = CAANN(hidden=(8,)).fit(t0, t1, dem)
    nxt = model.step(t1, dem, p)
    counts = np.array([np.sum(t1 == c) for c in (1, 2, 3, 4)], dtype=float)
    target = np.round(counts @ p).astype(int)
    target[-1] += t1.size - target.sum()
    got = np.array([np.sum(nxt == c) for c in (1, 2, 3, 4)])
    assert np.array_equal(got, target)
    assert np.all(nxt[t1 == 1] == 1)  # water protected
