# Agricultural drought in the Barind Tract, Bangladesh

> Kafy, A.-A., Bakshi, A., Saha, M., Al Faisal, A., Almulhim, A.I., Rahaman, Z.A., Mohammad, P. (2023). Assessment and prediction of index based agricultural drought vulnerability using machine learning algorithms. *Science of the Total Environment*, 867, 161394. [https://doi.org/10.1016/j.scitotenv.2023.161394](https://doi.org/10.1016/j.scitotenv.2023.161394)

## In one paragraph

The study covers the Barind Tract (BT) in northwest Bangladesh. This area has 25 upazilas in Rajshahi, Naogaon and Chapai-Nawabganj districts, and its total area is 8371 km². The paper uses Landsat 5 TM and Landsat 8 OLI/TIRS scenes from March and April (pre-monsoon) for 1996, 2001, 2006, 2011, 2016 and 2021. It maps NDVI, MNDWI and LST. It also maps surface water from the Global Surface Water Explorer, rainfall from CHIRPS and soil moisture from GLDAS-NOAH. From NDVI and LST it builds the VCI and TCI, and then combines them into the VHI. Each index is put into five drought classes. A CA-ANN model in the QGIS MOLUSCE plugin then predicts the VHI drought map for 2026 and 2031. The model was checked against the 2016 and 2021 maps with kappa, chi-square and AUC. The model scored 0.938 and 0.960 AUC. Under VHI, extreme drought grew from 184.00 km² in 1996 to 571.18 km² in 2021. The paper predicts that severe and extreme drought will reach 15% and 13% of the area in 2026, and 18% and 24% in 2031.

## Key numbers

- Maximum LST rose from 31.75 °C in 1996 to 36.49 °C in 2021. Minimum LST rose from 18.66 °C to 20.89 °C (Section 3.2, Fig. 9).
- The area at 31 °C or more grew from 111.09 km² in 1996 to 1023.49 km² in 2021 (Table 11).
- Permanent and temporary surface water fell from 1055.85 km² in 1996 to 777.94 km² in 2021 (Table 10).
- VHI extreme drought area grew from 184.00 km² in 1996 to 571.18 km² in 2021. The no-drought area fell from 1738.21 km² to 1175.27 km² (Table 14).
- TCI extreme drought area grew from 105.16 km² in 1996 to 1267.67 km² in 2021 (Table 13).
- CA-ANN validation gave an overall kappa of 0.83 for 2016 and 0.84 for 2021. Percent correctness was 85.05 and 86.72 (Table 16).
- AUC was 0.938 for 2016 and 0.960 for 2021 (Fig. 16).
- Predicted severe and extreme drought: 15% and 13% in 2026, and 18% and 24% in 2031 (Section 3.5, Fig. 17).

## Method → code

| Step | Paper | Toolkit function |
|---|---|---|
| Image selection | Landsat 5 TM and 8 OLI/TIRS Collection 1 Level-1 scenes, path/row 138/43, cloud cover under 5%, March and April | `data.search_scenes`. The paper used single C1 scenes. The toolkit uses C2 L2 (`data.load_composite`). |
| Vegetation | NDVI (Eq. 1) in five classes | `indices.ndvi`, `lulc.class_areas` |
| Open water | MNDWI from Green and SWIR (Eq. 2) | `indices.mndwi` |
| Surface water (PTSW) | Global Surface Water Explorer in Google Earth Engine | not included. This is a GEE dataset (JRC GSW), not a Landsat index. |
| Rainfall | CHIRPS annual precipitation in GEE | not included. This is an outside climate dataset. |
| Soil moisture | GLDAS-NOAH at 0-10, 10-40 and 40-100 cm | not included. This is an outside model dataset. |
| Emissivity | NDVI lookup table (Table 2) | `thermal.emissivity_from_ndvi`. The paper's table breaks differ from the default (see Notes). |
| LST | DN to radiance to brightness temperature to LST (Eqs. 3 to 8), built in ArcGIS Pro Model Builder | `thermal.lst_from_bt`. The Model Builder chain is desktop only. |
| LST zones | Area in five LST ranges (Table 11) | `thermal.range_areas` |
| VCI | Eq. 9 | `drought.vci` |
| TCI | Eq. 10 | `drought.tci` |
| VHI | α·VCI + (1−α)·TCI (Eq. 8, second use of that number) | `drought.vhi` |
| Drought classes | Five classes from Table 7. Vegetation mask is NDVI > 0.2. | `drought.classify_vhi`, `lulc.class_areas` |
| Directional reading | NW, SW, NE and SE parts of the map | `zones.directional_sectors`, `zones.share_by_zone` |
| Correlation | NDVI, MNDWI, rainfall, LST, VCI, TCI, VHI (Fig. 14) | `stats.correlation` |
| VHI vs surface water | Cross profile (Fig. 15) | `stats.cross_profile` |
| Prediction | CA-ANN in the QGIS MOLUSCE plugin, for 2026 and 2031 | `caann.transition_matrix`, `caann.CAANN`. MOLUSCE itself is a desktop plugin. |
| Validation | Kappa set (Table 16), Pearson chi-square (Table 15), ROC AUC (Fig. 16) | `caann.kappa`, `caann.chi_square_validation`, `stats.roc_auc` |

## Figures and tables in the paper

| Item | What it shows | Toolkit function |
|---|---|---|
| [Fig. 1](https://doi.org/10.1016/j.scitotenv.2023.161394) | Study area in Bangladesh and the Barind region | map / layout |
| [Fig. 2](https://doi.org/10.1016/j.scitotenv.2023.161394) | Method flowchart | map / layout |
| [Fig. 3](https://doi.org/10.1016/j.scitotenv.2023.161394) | ANN layout: eight inputs, one hidden layer, VHI output | `caann.CAANN` |
| [Fig. 4](https://doi.org/10.1016/j.scitotenv.2023.161394) | NDVI vegetation classes, 1996 to 2021 | `indices.ndvi` |
| [Fig. 5](https://doi.org/10.1016/j.scitotenv.2023.161394) | MNDWI open water, 1996 to 2021 | `indices.mndwi` |
| [Fig. 6](https://doi.org/10.1016/j.scitotenv.2023.161394) | Permanent and temporary surface water, 1996 to 2021 | not included (GSWE) |
| [Fig. 7](https://doi.org/10.1016/j.scitotenv.2023.161394) | Annual CHIRPS rainfall, 1996 to 2021 | not included (CHIRPS) |
| [Fig. 8](https://doi.org/10.1016/j.scitotenv.2023.161394) | GLDAS soil moisture at three depths | not included (GLDAS) |
| [Fig. 9](https://doi.org/10.1016/j.scitotenv.2023.161394) | LST zones, 1996 to 2021 | `thermal.lst_from_bt` |
| [Fig. 10](https://doi.org/10.1016/j.scitotenv.2023.161394) | VCI drought maps | `drought.vci` |
| [Fig. 11](https://doi.org/10.1016/j.scitotenv.2023.161394) | TCI drought maps | `drought.tci` |
| [Fig. 12](https://doi.org/10.1016/j.scitotenv.2023.161394) | VHI drought maps | `drought.vhi`, `drought.classify_vhi` |
| [Fig. 13](https://doi.org/10.1016/j.scitotenv.2023.161394) | Drought class shares by VCI, TCI and VHI over time | `lulc.class_areas` |
| [Fig. 14](https://doi.org/10.1016/j.scitotenv.2023.161394) | Correlation plot of drought indices and drivers | `stats.correlation` |
| [Fig. 15](https://doi.org/10.1016/j.scitotenv.2023.161394) | Cross profile of VHI against surface water | `stats.cross_profile` |
| [Fig. 16](https://doi.org/10.1016/j.scitotenv.2023.161394) | ROC curves for 2016 and 2021 predictions | `stats.roc_auc` |
| [Fig. 17](https://doi.org/10.1016/j.scitotenv.2023.161394) | Predicted VHI drought maps, 2026 and 2031 | `caann.CAANN` |
| [Fig. 18](https://doi.org/10.1016/j.scitotenv.2023.161394) | VHI drought class change, 1996 to 2031 | `lulc.class_areas` |
| [Table 1](https://doi.org/10.1016/j.scitotenv.2023.161394) | Landsat scenes used | `data.search_scenes` |
| [Table 2](https://doi.org/10.1016/j.scitotenv.2023.161394) | Emissivity values by NDVI range | `thermal.emissivity_from_ndvi` |
| [Table 3](https://doi.org/10.1016/j.scitotenv.2023.161394) | NDVI minimum, maximum, mean and SD per year | `indices.ndvi` |
| [Table 4](https://doi.org/10.1016/j.scitotenv.2023.161394) | NDVI class breaks | `indices.ndvi` |
| [Table 5](https://doi.org/10.1016/j.scitotenv.2023.161394) | TCI minimum, maximum, mean and SD per year | `drought.tci` |
| [Table 6](https://doi.org/10.1016/j.scitotenv.2023.161394) | VCI minimum, maximum, mean and SD per year | `drought.vci` |
| [Table 7](https://doi.org/10.1016/j.scitotenv.2023.161394) | Drought class breaks for VCI, TCI and VHI | `drought.classify_vhi` |
| [Table 8](https://doi.org/10.1016/j.scitotenv.2023.161394) | NDVI classes matched to TCI and VCI drought classes | `drought.classify_vhi` |
| [Table 9](https://doi.org/10.1016/j.scitotenv.2023.161394) | Area per NDVI category per year | `lulc.class_areas` |
| [Table 10](https://doi.org/10.1016/j.scitotenv.2023.161394) | Surface water area and change per period | not included (GSWE) |
| [Table 11](https://doi.org/10.1016/j.scitotenv.2023.161394) | Area per LST range per year | `thermal.range_areas` |
| [Table 12](https://doi.org/10.1016/j.scitotenv.2023.161394) | Drought class areas from VCI | `lulc.class_areas` |
| [Table 13](https://doi.org/10.1016/j.scitotenv.2023.161394) | Drought class areas from TCI | `lulc.class_areas` |
| [Table 14](https://doi.org/10.1016/j.scitotenv.2023.161394) | Drought class areas from VHI | `lulc.class_areas` |
| [Table 15](https://doi.org/10.1016/j.scitotenv.2023.161394) | Estimated vs predicted VHI areas, chi-square deviation | `caann.chi_square_validation` |
| [Table 16](https://doi.org/10.1016/j.scitotenv.2023.161394) | CA-ANN kappa validation, 2016 and 2021 | `caann.kappa` |

## Published tables as data

- `tables/table1_landsat_scenes.csv`: the six Landsat scenes (date, scene ID, sensor, cloud, path/row).
- `tables/table3_ndvi_stats.csv`: NDVI lowest, highest, mean and SD per year.
- `tables/table5_tci_stats.csv`: TCI lowest, highest, mean and SD per year.
- `tables/table6_vci_stats.csv`: VCI lowest, highest, mean and SD per year.
- `tables/table9_ndvi_category_area_km2.csv`: area in km² per NDVI category per year.
- `tables/table10_ptsw_area_km2.csv`: surface water area in km² per year.
- `tables/table10_ptsw_change.csv`: surface water change per period, as printed.
- `tables/table11_lst_range_area_km2.csv`: area in km² per LST range (°C) per year.
- `tables/table12_vci_drought_area_km2.csv`: VCI drought class areas in km².
- `tables/table13_tci_drought_area_km2.csv`: TCI drought class areas in km².
- `tables/table14_vhi_drought_area_km2.csv`: VHI drought class areas in km².
- `tables/table15_vhi_chi_square_deviation.csv`: estimated vs predicted VHI areas in km² and deviation in %.
- `tables/table16_caann_validation.csv`: percent correctness, overall kappa, K-no, K-location, K-standard and K-location-strata.

## Notes

- LST is in °C. All areas are in km². Every area table sums to 8371.03 km², give or take 0.02 for rounding.
- Drought class breaks (Table 7): TCI <15, 15-<25, 25-<35, 35-<45, ≥45. VCI <10, 10-<20, 20-<30, 30-<40, ≥40. VHI 0-10, 10-20, 20-30, 30-40, ≥40. The classes run Extreme, Severe, Moderate, Mild, No. TCI uses different breaks from VCI and VHI.
- Pixels with NDVI < 0.2 are set to No Data before drought mapping. This removes water, bare land and built-up areas.
- The paper does not give a value for the VHI weight α.
- Table 2 prints the emissivity breaks as "0002E185" and "0002E727". These are most likely −0.185 and 0.727, the values in the first and last rows.
- The paper prints the TM constants as K1 = 1260.56 K and K2 = 607.66. The usual Landsat 5 values are K1 = 607.76 and K2 = 1260.56. Check this before you reuse them.
- The second row of Table 10 is labeled "Change in % of PTSW". The values are really km² differences (for example, 1055.85 − 777.94 = 277.91). The CSV keeps them as printed.
- In Table 1, the 2006 date (2006/04/09) does not match the scene ID day (170, which is June 19). The CSV copies both as printed.
- Table 9 uses the names No, Less, Moderate, Sparse and Dense vegetation. Table 4 uses No vegetation, Poor, Normal, Good and Excellent.
- The 2026 and 2031 percentages come from the text and Fig. 17. The paper gives no area table for the predicted years.
- The ANN settings (neighborhood, iterations, learning rate) are not reported. Fig. 3 shows 8 inputs, one hidden layer with 8 nodes, and one output.

Figures are not reproduced here. See the paper at the DOI above.
