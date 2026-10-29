# Vegetation loss, surface heat and carbon in Cumilla

> Kafy, A.-A., Faisal, A.-A., Al Rakib, A., Fattah, M.A., Rahaman, Z.A., Sattar, G.S. (2022). Impact of vegetation cover loss on surface temperature and carbon emission in a fastest-growing city, Cumilla, Bangladesh. *Building and Environment*, 208, 108573. https://doi.org/10.1016/j.buildenv.2021.108573

## In one paragraph

The study looks at Cumilla City Corporation in Bangladesh from 1994 to 2019. It uses six April Landsat scenes (TM for 1994 to 2009, OLI for 2014 and 2019). The images were classified into four classes (water, urban, vegetation, bare land) with a support vector machine (SVM). NDVI was split into six vegetation health classes. LST was found with the single-channel method. Carbon stock was estimated with a tree allometric equation (Biomass Carbon Stock Assessment) and laid over the land cover and LST maps. Results were reported for four zones: residential, commercial, industrial and educational. Urban area grew from 13.11 km² to 26.31 km² and vegetation fell from 18.91 km² to 14.95 km². The share of "very good" vegetation fell from 43.35% to 14.53%. The highest LST rose from 27.61 °C (1994) to 39.28 °C (2019). The paper reports an LST rise of 11.2 °C (1.86 °C/year) since 1994 and a strong positive link between carbon emission and LST.

## Key numbers

- Urban area grew from 13.11 km² (1994) to 26.31 km² (2019); vegetation fell from 18.91 km² to 14.95 km² (Table 4).
- Water bodies fell from 3.63 km² to 0.60 km²; bare land from 9.61 km² to 3.39 km² (Table 4).
- "Very good" vegetation (NDVI > 0.75) fell from 43.35% of the area in 1994 to 14.53% in 2019; "no vegetation" rose from 2.23% to 19.87% (Table 5).
- In the residential zone, very good vegetation fell from 8.22% to 0.22% (Table 5).
- Maximum LST rose from 27.61 °C in 1994 to 39.28 °C in 2019, both in the industrial zone (Table 6).
- In 2019, 51.36% of the area was in the 29 to < 33 °C range; in 1994, 0.00% was (Table 6).
- LST rose by 11.2 °C (1.86 °C/year) since 1994 (Section 3.5).
- Overall accuracy was 97% to 98% for all six years; printed kappa was 86.65 to 88.33 (Table 3).

## Method → code

| Step | Paper | Toolkit function |
|---|---|---|
| Get imagery | Six April Landsat scenes from USGS, path/row 137/44 | `data.search_scenes`, `data.load_composite` (toolkit uses C2 L2 median composites; the paper used single Level-1 scenes) |
| Land cover map | SVM supervised classification in ENVI 5.3, four classes | `lulc.train_classifier` (Random Forest; paper used SVM) |
| Accuracy | 300 points per year (1800 total), confusion matrix, kappa | `lulc.accuracy` |
| Class areas | Area in km² per class per year | `lulc.class_areas` |
| Class change | ArcGIS "combine" tool | `lulc.change_matrix`, `lulc.gain_loss` |
| Vegetation index | NDVI in ArcGIS Model Builder | `indices.ndvi` (the six class breaks in Table 2 are applied by the user) |
| Emissivity | ε = 0.004 PV + 0.986, PV linear | `thermal.emissivity_from_ndvi` |
| LST | DN to radiance to brightness temperature to LST, single channel | `thermal.lst_from_bt` |
| LST ranges by zone | % area in five LST ranges per zone | `thermal.range_areas` |
| Vegetation and LST by zone | Results for RZ, CZ, IZ, EZ (zone boundaries from the city office) | `zones.share_by_zone` (with the zone polygons as input) |
| LST by NDVI class | LST in each vegetation class (Fig. 7) | `thermal.stats_by_class` |
| Carbon stock | Allometric AGB from field DBH and tree height, carbon = 0.5 × biomass | not included: needs field tree data; the toolkit uses per-class carbon pools (`carbon.stock_map`) instead |
| Carbon vs LST | Sensitivity analysis (Fig. 8) | `stats.correlation` |

## Figures and tables in the paper

| Item | What it shows | Toolkit function |
|---|---|---|
| [Fig. 1](https://doi.org/10.1016/j.buildenv.2021.108573) | Study area and the four city zones | map / layout |
| [Fig. 2](https://doi.org/10.1016/j.buildenv.2021.108573) | Carbon stock concentration maps, 1994 to 2019 | not included (field allometry) |
| [Fig. 3](https://doi.org/10.1016/j.buildenv.2021.108573) | Data collection and method flowchart | map / layout |
| [Fig. 4](https://doi.org/10.1016/j.buildenv.2021.108573) | Land cover maps of Cumilla for six years | `lulc.train_classifier` |
| [Fig. 5](https://doi.org/10.1016/j.buildenv.2021.108573) | NDVI vegetation health class maps | `indices.ndvi` |
| [Fig. 6](https://doi.org/10.1016/j.buildenv.2021.108573) | LST maps for six years | `thermal.lst_from_bt` |
| [Fig. 7](https://doi.org/10.1016/j.buildenv.2021.108573) | LST in each NDVI vegetation class | `thermal.stats_by_class` |
| [Fig. 8](https://doi.org/10.1016/j.buildenv.2021.108573) | Carbon emission versus LST over time | `stats.correlation` |
| [Table 1](https://doi.org/10.1016/j.buildenv.2021.108573) | Landsat scenes used | `data.search_scenes` |
| [Table 2](https://doi.org/10.1016/j.buildenv.2021.108573) | NDVI class breaks and vegetation types | `indices.ndvi` |
| [Table 3](https://doi.org/10.1016/j.buildenv.2021.108573) | Confusion matrices and accuracy per year | `lulc.accuracy` |
| [Table 4](https://doi.org/10.1016/j.buildenv.2021.108573) | Land cover area per year and change | `lulc.class_areas` |
| [Table 5](https://doi.org/10.1016/j.buildenv.2021.108573) | Vegetation health class shares by zone, NDVI range | `zones.share_by_zone` |
| [Table 6](https://doi.org/10.1016/j.buildenv.2021.108573) | LST range shares by zone, LST max and min | `thermal.range_areas` |

## Published tables as data

- `tables/table1_landsat_scenes.csv`: scene dates, sensor, path/row, resolution, cloud cover.
- `tables/table2_ndvi_classes.csv`: NDVI class breaks and types, copied as printed.
- `tables/table3_confusion_matrix.csv`: confusion matrix per year, with totals, user and producer accuracy (%).
- `tables/table3_accuracy_summary.csv`: overall accuracy (%) and kappa (× 100) per year.
- `tables/table4_lulc_area_km2.csv`: area per class per year in km², and change 1994 to 2019 in %.
- `tables/table5_vegetation_class_pct_by_zone.csv`: % of total area in each NDVI class per zone, plus NDVI max and min.
- `tables/table6_lst_range_pct_by_zone.csv`: % of total area in each LST range (°C) per zone, plus LST max and min (°C).

## Notes

- LST is in °C. Areas are in km². Tables 5 and 6 give % of the whole city area, so each year's "Total" row sums to about 100.
- LST ranges: < 21, 21 to < 25, 25 to < 29, 29 to < 33, ≥ 33 °C.
- NDVI classes (Table 2): Very Good > 0.75, Good 0.45 to 0.75, Normal 0.25 to 0.45, Poor 0.15 to 0.25. The printed "Very Poor" range is "−0.12 to −0.15" and water is labeled "Poor ≤ 0.1". These are copied as printed; they do not form a clean set of breaks.
- The LST equation uses DN-based radiance (Lmin/Lmax), not Collection 2 surface temperature. ρ is printed as "1.438 × 10² mK"; the usual value is 1.438 × 10⁻² mK. PV is linear here (not squared).
- Table 3: the 2009 producer accuracy for water is printed as 69.84, but the matrix gives 44/44 = 100. Kappa recomputed from the printed matrices is about 95 to 97, higher than the printed 86.65 to 88.33. The CSVs keep the printed values.
- Table 4 "Change in %" (e.g., urban 29.17) does not match the text, which says urban +26.96%, bare land −18.18%, water −6.68%, vegetation −2.10%. The CSV keeps the table values.
- The conclusion gives an average LST rise of 2.24 °C/year; Section 3.5 gives 1.86 °C/year.
- Carbon was not mapped from per-class pools. It came from field tree data (DBH and height from the city office), so no carbon-by-class table exists.

Figures are not reproduced here. See the paper at the DOI above.
