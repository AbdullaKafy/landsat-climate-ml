"""Tests for thermal, lulc tables, carbon, drought, zones and stats."""

import numpy as np

from landsat_climate import carbon, drought, stats, thermal, zones
from landsat_climate.caann import chi_square_validation
from landsat_climate.indices import bsi, evi, mndwi, savi
from landsat_climate.lulc import accuracy, change_matrix, class_areas, gain_loss


def test_indices_signs():
    assert mndwi(0.3, 0.1) > 0
    assert savi(0.5, 0.1) > 0
    assert bsi(0.05, 0.3, 0.2, 0.4) > 0
    assert evi(0.5, 0.1, 0.05) > 0


def test_lst_from_bt_close_to_bt():
    e = thermal.emissivity_from_ndvi(np.array([0.6]))
    assert np.isclose(e[0], 0.99)
    lst = thermal.lst_from_bt(np.array([300.0]), e)
    assert 27 < lst[0] < 29  # emissivity < 1 raises LST slightly above BT (26.85 °C)


def test_uhi_standardized():
    u = thermal.uhi(np.array([20.0, 25.0, 30.0]))
    assert np.isclose(np.mean(u), 0) and np.isclose(np.std(u), 1)


def test_range_areas_total():
    t = np.array([[19.0, 22.0], [27.0, 40.0]])
    a = thermal.range_areas(t, (20, 25, 30))
    assert np.isclose(sum(a.values()), 4 * 900 / 1e6)
    assert a["<20"] > 0 and a[">30"] > 0


def test_lulc_tables():
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[1, 2], [2, 4]])
    assert np.isclose(sum(class_areas(a).values()), 4 * 0.0009)
    cm = change_matrix(a, b)
    assert np.isclose(cm.loc["Vegetation", "Built-up"], 0.0009)
    gl = gain_loss(a, b)
    assert np.isclose(gl.loc["Built-up", "net_km2"], 0.0009)
    acc = accuracy(a, b)
    assert acc["overall_accuracy"] == 0.75 and acc["producer"]["Vegetation"] == 0


def test_chi_square_perfect():
    a = np.array([[1, 2], [3, 4]])
    r = chi_square_validation(a, a)
    assert r["chi_square"] == 0 and r["p_value"] == 1


def test_carbon_change():
    pools = {3: {"above": 100, "soil": 50}, 2: {"soil": 10}}
    before = np.array([[3, 3]])
    after = np.array([[3, 2]])
    r = carbon.stock_change(before, after, pools)
    assert np.isclose(r["stock_before_mg"], 2 * 150 * 0.09)
    assert np.isclose(r["emission_mg"], 140 * 0.09)


def test_drought_indices():
    n = np.array([[[0.2]], [[0.6]], [[0.4]]])
    t = np.array([[[30.0]], [[20.0]], [[25.0]]])
    v, c, h = drought.from_stack(n, t)
    assert np.allclose(v.ravel(), [0, 100, 50]) and np.allclose(c.ravel(), [0, 100, 50])
    assert list(drought.classify_vhi([5, 15, 25, 35, 60])) == list(drought.VHI_CLASSES)


def test_zones():
    s = zones.directional_sectors((11, 11), (5, 5))
    assert s[0, 5] == 0 and s[5, 10] == 2 and s[10, 5] == 4 and s[5, 0] == 6
    r = zones.concentric_rings((11, 11), (5, 5), ring_m=60)
    assert r[5, 5] == 0 and r[5, 10] == 2
    share = zones.share_by_zone(np.full((11, 11), 2), s, 2)
    assert all(v == 100 for v in share.values())


def test_stats():
    x = np.arange(10.0)
    assert np.isclose(stats.correlation(x, 2 * x + 1)["slope"], 2)
    assert stats.roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1
    prof = stats.cross_profile(np.eye(5), (0, 0), (4, 4))
    assert prof[0] == 1 and prof[-1] == 1


def test_more_helpers():
    e = thermal.emissivity_ndvi_thresholds(np.array([-0.5, 0.0, 0.5, 0.9]))
    assert np.allclose(e[[0, 1, 3]], [0.995, 0.970, 0.990]) and 0.97 < e[2] < 0.99
    assert stats.rmse([1, 2, 3], [1, 2, 5]) == np.sqrt(4 / 3)
    t = stats.crosstab(np.array(["a", "a", "b"]), np.array(["x", "y", "y"]))
    assert np.allclose(t.sum(axis=1), 100)


def test_expansion_and_gravity():
    from landsat_climate.lulc import expansion_indices

    e = expansion_indices(10, 20, 5, 100)
    assert e["speed_km2_per_year"] == 2 and e["intensity_pct_per_year"] == 2
    m = np.zeros((5, 5), bool)
    m[1, 1] = m[3, 3] = True
    assert zones.gravity_center(m) == (2.0, 2.0)
    assert thermal.utfvi(np.array([10.0, 30.0]), denominator="tmean").sum() == 0


def test_pca():
    import pandas as pd

    rng = np.random.default_rng(0)
    a = rng.normal(size=200)
    df = pd.DataFrame(
        {"a": a, "b": 2 * a + rng.normal(scale=0.01, size=200), "c": rng.normal(size=200)}
    )
    load, var = stats.pca_loadings(df)
    assert var[0] > 0.6 and abs(load.loc["b", "PC1"]) > abs(load.loc["c", "PC1"])
