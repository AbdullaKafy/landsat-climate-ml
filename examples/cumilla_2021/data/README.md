# Data

All files here were made by `python download.py` from free, public sources.
They are small (about 10 MB) and are kept in the repository so the notebook runs
without a download.

| File | What it holds | Source and license |
|---|---|---|
| `composites.nc` | Median seasonal composites for 1999, 2009 and 2019 (winter and summer): six reflectance bands (0 to 1) and surface temperature `lst` (°C). 30 m grid, UTM 46N (EPSG:32646), 247 x 247 pixels. | Landsat Collection 2 Level-2 (Landsat 5 TM and Landsat 8 OLI/TIRS), USGS, public domain. Accessed through the Microsoft Planetary Computer. |
| `scenes.csv` | Every Landsat scene used, with date and cloud cover. | Same as above. |
| `dem.nc` | Elevation (m) on the same grid. | Copernicus GLO-30 DEM, © DLR e.V. 2010 to 2014 and © Airbus Defence and Space GmbH 2014 to 2018, provided under COPERNICUS by the European Union and ESA. |
| `worldcover2020.nc` | ESA WorldCover 2020 classes on the same grid (mode resampling from 10 m). Used as training labels and as a check. | © ESA WorldCover project 2020, contains modified Copernicus Sentinel data (2020), CC BY 4.0. |
| `aoi.geojson` | The square study area (53.04 km²). | Center point from OpenStreetMap (node 268417180), © OpenStreetMap contributors, ODbL. |

## Seasons

* Winter: 1 December of the previous year to 28 February.
* Summer (pre-monsoon): 1 March to 31 May.

Scenes with 20% or more cloud cover are skipped. Pixels flagged as fill, cloud,
dilated cloud, cirrus, cloud shadow or snow in `QA_PIXEL` are masked before the median.

| Year | Winter scenes | Summer scenes | Summer dates |
|---|---|---|---|
| 1999 | 8 | 4 | 5 Mar to 15 Apr |
| 2009 | 8 | 4 | 1 Apr to 12 May |
| 2019 | 8 | 3 | 28 Mar to 15 May |

The 1999 summer composite has only March and early April scenes, so it is cooler
than 2009 and 2019 partly because of timing, not only land cover.
