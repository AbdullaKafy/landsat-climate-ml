"""Download Landsat Collection 2 Level-2 data for a study area.

Data come from the Microsoft Planetary Computer STAC catalog. No account is
needed. Each season is a median composite of clear pixels from all scenes with
less than `max_cloud` percent cloud cover in the date window.
"""

from __future__ import annotations

import numpy as np
import xarray as xr

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
CRS = "EPSG:32646"  # UTM zone 46N, covers Cumilla
RES = 30

# Season windows (month-day). Winter is the dry season (December to February),
# summer is the hot pre-monsoon season (March to May).
SEASONS = {
    "winter": ("{y0}-12-01", "{y}-02-28"),
    "summer": ("{y}-03-01", "{y}-05-31"),
}

REFLECTANCE = ["blue", "green", "red", "nir08", "swir16", "swir22"]


def aoi_box(lat: float, lon: float, area_km2: float):
    """Square study area (as a shapely polygon in WGS84) with a given area."""
    from shapely.geometry import box

    half = np.sqrt(area_km2) / 2.0
    dlat = half / 110.574
    dlon = half / (111.320 * np.cos(np.deg2rad(lat)))
    return box(lon - dlon, lat - dlat, lon + dlon, lat + dlat)


def _catalog():
    import planetary_computer
    import pystac_client

    return pystac_client.Client.open(STAC_URL, modifier=planetary_computer.sign_inplace)


def search_scenes(geom, year: int, season: str, max_cloud: float = 20.0, platforms=None):
    """Return STAC items for one year and season."""
    a, b = SEASONS[season]
    window = f"{a.format(y0=year - 1, y=year)}/{b.format(y0=year - 1, y=year)}"
    query = {"eo:cloud_cover": {"lt": max_cloud}}
    if platforms:
        query["platform"] = {"in": list(platforms)}
    items = _catalog().search(
        collections=["landsat-c2-l2"], intersects=geom, datetime=window, query=query
    ).item_collection()
    return list(items)


def _clear_mask(qa: xr.DataArray) -> xr.DataArray:
    """True where the QA_PIXEL band says clear: no fill, cloud, shadow, snow, cirrus."""
    qa = qa.astype("uint16")
    bad = 0
    for bit in (0, 1, 2, 3, 4, 5):  # fill, dilated cloud, cirrus, cloud, shadow, snow
        bad |= 1 << bit
    return (qa & bad) == 0


def load_composite(items, geom) -> xr.Dataset:
    """Median composite of reflectance (0 to 1) and surface temperature (°C)."""
    from odc.stac import load

    thermal = "lwir11" if items[0].properties["platform"] == "landsat-8" else "lwir"
    ds = load(
        items,
        bands=REFLECTANCE + [thermal, "qa_pixel"],
        geopolygon=geom,
        crs=CRS,
        resolution=RES,
        groupby="solar_day",
        chunks={},
    )
    clear = _clear_mask(ds["qa_pixel"])
    out = {}
    for b in REFLECTANCE:
        v = ds[b].where(ds[b] > 0) * 0.0000275 - 0.2  # Collection 2 scale and offset
        out[b] = v.where(clear).median("time")
    st = ds[thermal].where(ds[thermal] > 0) * 0.00341802 + 149.0 - 273.15  # Kelvin to °C
    out["lst"] = st.where(clear).median("time")
    comp = xr.Dataset(out).compute()
    comp.attrs["n_scenes"] = len(items)
    comp.attrs["scenes"] = ", ".join(sorted(i.id for i in items))
    return comp


def load_dem(geom) -> xr.DataArray:
    """Copernicus GLO-30 elevation (m) on the same 30 m UTM grid as the composites."""
    from odc.stac import load

    items = list(_catalog().search(collections=["cop-dem-glo-30"], intersects=geom).items())
    dem = load(items, bands=["data"], geopolygon=geom, crs=CRS, resolution=RES,
               resampling="bilinear", chunks={})["data"].max("time")
    return dem.astype("float32").compute()


def load_worldcover(geom) -> xr.DataArray:
    """ESA WorldCover 2020 classes on the same 30 m grid (used only as a check)."""
    from odc.stac import load

    items = list(
        _catalog()
        .search(collections=["esa-worldcover"], intersects=geom, datetime="2020")
        .items()
    )
    wc = load(items, bands=["map"], geopolygon=geom, crs=CRS, resolution=RES,
              resampling="mode", chunks={})["map"].max("time")
    return wc.compute()
