"""Step 1: download seasonal Landsat composites, elevation and WorldCover.

Run from this folder:  python download.py
Output (in ./data): composites.nc, dem.nc, worldcover2020.nc, aoi.geojson, scenes.csv
"""

import json
from pathlib import Path

import pandas as pd
import xarray as xr
from shapely.geometry import mapping

from landsat_climate.data import aoi_box, load_composite, load_dem, load_worldcover, search_scenes

# Study area: square of 53.04 km2 (official area of Cumilla City Corporation)
# centered on the city node in OpenStreetMap (node 268417180).
CENTER = (23.4609839, 91.1812216)
AREA_KM2 = 53.04
YEARS = {1999: ["landsat-5"], 2009: ["landsat-5"], 2019: ["landsat-8"]}  # sensors used in the paper

out = Path("data")
out.mkdir(exist_ok=True)
geom = aoi_box(*CENTER, AREA_KM2)
(out / "aoi.geojson").write_text(
    json.dumps({"type": "Feature", "properties": {"name": "Cumilla study box"},
                "geometry": mapping(geom)})
)

layers, scenes = [], []
have = (out / "composites.nc").exists()
for year, platforms in ({} if have else YEARS).items():
    for season in ("winter", "summer"):
        items = search_scenes(geom, year, season, platforms=platforms)
        comp = load_composite(items, geom).expand_dims(year=[year], season=[season])
        layers.append(comp)
        scenes += [{"year": year, "season": season, "scene": i.id,
                    "date": i.datetime.date().isoformat(),
                    "cloud": i.properties["eo:cloud_cover"]} for i in items]
        print(year, season, len(items), "scenes")

if not have:
    ds = xr.combine_by_coords(layers, combine_attrs="drop")
    ds.to_netcdf(out / "composites.nc")
    pd.DataFrame(scenes).sort_values(["year", "season", "date"]).to_csv(
        out / "scenes.csv", index=False
    )
load_dem(geom).to_netcdf(out / "dem.nc")
load_worldcover(geom).to_netcdf(out / "worldcover2020.nc")
print("saved", dict(xr.open_dataset(out / "composites.nc").sizes))
