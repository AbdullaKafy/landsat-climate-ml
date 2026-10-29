# Seasonal heat and UTFVI prediction in Cumilla, Bangladesh

> Abdulla - Al Kafy, Abdullah-Al-Faisal, Md. Shahinoor Rahman, Muhaiminul Islam, Abdullah Al Rakib, Md. Arshadul Islam, Md. Hasib Hasan Khan, Md. Soumik Sikdar, Md. Hasnan Sakin Sarker, Jannatul Mawa, Golam Shabbir Sattar (2021). Prediction of seasonal urban thermal field variance index using machine learning algorithms in Cumilla, Bangladesh. *Sustainable Cities and Society*, 64, 102542. https://doi.org/10.1016/j.scs.2020.102542

## In one paragraph

The study area is Cumilla City Corporation (CCC), Bangladesh, about 46 km². The authors used Landsat 4-5 TM and Landsat 8 OLI scenes for 1999, 2009 and 2019, one summer and one winter scene per year. They mapped four land cover classes with SVM. They computed seasonal LST, a normalized UHI and the urban thermal field variance index (UTFVI) with six classes. A CA-ANN model (MOLUSCE plugin) predicted land cover for 2029 and 2039. A three-layer ANN, built in MATLAB on a 500 m grid, predicted seasonal LST and UTFVI. Urban area grew from 20.45 km² (1999) to 26.31 km² (2019). Vegetation fell from 19.69 km² to 12.95 km². The model predicts 31.30 km² of urban area by 2039. In summer 2039, 37.06 % of the city is predicted to be at or above 33 °C.

## Key numbers

- Urban area rose from 20.45 km² in 1999 to 26.31 km² in 2019; vegetation fell from 19.69 km² to 12.95 km² (Table 2).
- Summer area at or above 33 °C: 0.20 km² in 1999 and 3.04 km² in 2019 (Table 3).
- Summer "strongest" UTFVI area (> 0.020): 0.33 km² in 1999 and 2.53 km² in 2019 (Table 7).
- CA model validation for 2019: overall kappa 0.86 and 89.41 % correctness (Table 8).
- Predicted urban area: 29.87 km² in 2029 and 31.30 km² in 2039 (Table 9).
- ANN LST validation for summer 2019: RMSE 0.53 and R 0.87 (Table 10).
- Predicted summer area at or above 33 °C: 32.77 % in 2029 and 37.06 % in 2039 (Table 11).
- Predicted summer "strongest" UTFVI area: 31.07 km² in 2029 and 35.92 km² in 2039 (Table 13).

## Method → code

| Step | Paper | Toolkit function |
|---|---|---|
| Get scenes | One summer and one winter Landsat scene per year from USGS EarthExplorer, cloud < 10 % | `data.search_scenes`, `data.load_composite` (toolkit uses Collection 2 Level 2 median composites, not single scenes) |
| Land cover map | SVM, RBF kernel, 4 classes, about 45 training samples per class | `lulc.train_classifier` (Random Forest; the paper used SVM) |
| Accuracy | Overall, user, producer accuracy and kappa from 200 ground points and 150 Google Earth points | `lulc.accuracy` |
| Class areas and change | km² per class per year and net change | `lulc.class_areas`, `lulc.gain_loss` |
| NDVI | (Band 5 - Band 4) / (Band 5 + Band 4) for Landsat 8 | `indices.ndvi` |
| Emissivity | PV from NDVI min/max, LSE = 0.004 PV + 0.986 | `thermal.emissivity_from_ndvi` |
| LST | TM: DN to radiance to Kelvin to °C. OLI: radiance, BT, NDVI emissivity; mean of Band 10 and Band 11 | `thermal.lst_from_bt` (toolkit works from Level 2 data, not raw DN) |
| LST range areas | km² and % in five ranges (< 21 to ≥ 33 °C) | `thermal.range_areas` |
| LST by land cover | Cross-tab of LST range and land cover class | `thermal.range_areas` run per class mask; `thermal.stats_by_class` gives class means |
| UHI | (Ts - Tm) / SD | `thermal.uhi` |
| UTFVI | (Ts - Tm) / Ts, six classes | `thermal.utfvi`, `thermal.classify_utfvi` |
| UTFVI by land cover | Share of each UTFVI class per land cover class | `lulc.change_matrix` (cross-tab of two class rasters) |
| Future land cover | CA with ANN transition potential in MOLUSCE (QGIS); drivers: elevation, slope, distance to roads, commercial space, schools, water | `caann.transition_matrix`, `caann.CAANN` |
| Land cover model check | Kappa in MOLUSCE and IDRISI Selva for 2019 | `caann.kappa` |
| Built-up and bare soil inputs | NDBI and NDBSI as ANN inputs | `indices.ndbi`, `indices.bsi` (BSI is close to, but not the same as, NDBSI) |
| Future LST and UTFVI | Three-layer ANN in MATLAB on a 500 m grid; compared with ResNet, GoogLeNet, VGGNet, AlexNet | `lstmodel.fit_lst_model`, `lstmodel.predict_lst` (scikit-learn MLP on the pixel grid; the paper used MATLAB on a 500 m grid) |
| Model fit | RMSE and R between predicted and measured 2019 values | `stats.correlation` |

## Figures and tables in the paper

| Item | What it shows | Toolkit function |
|---|---|---|
| [Fig. 1](https://doi.org/10.1016/j.scs.2020.102542) | Study area location in Bangladesh and Cumilla | map / layout |
| [Fig. 2](https://doi.org/10.1016/j.scs.2020.102542) | Five algorithms: estimated vs measured LST, 2019 | `stats.correlation` |
| [Fig. 3](https://doi.org/10.1016/j.scs.2020.102542) | ANN architecture for seasonal LST | map / layout |
| [Fig. 4](https://doi.org/10.1016/j.scs.2020.102542) | ANN architecture for seasonal UTFVI | map / layout |
| [Fig. 5](https://doi.org/10.1016/j.scs.2020.102542) | SVM land cover maps, 1999 to 2019 | `lulc.train_classifier` |
| [Fig. 6](https://doi.org/10.1016/j.scs.2020.102542) | Summer LST maps | `thermal.lst_from_bt` |
| [Fig. 7](https://doi.org/10.1016/j.scs.2020.102542) | Winter LST maps | `thermal.lst_from_bt` |
| [Fig. 8](https://doi.org/10.1016/j.scs.2020.102542) | Summer UTFVI maps | `thermal.classify_utfvi` |
| [Fig. 9](https://doi.org/10.1016/j.scs.2020.102542) | Winter UTFVI maps | `thermal.classify_utfvi` |
| [Fig. 10](https://doi.org/10.1016/j.scs.2020.102542) | Summer UTFVI share by land cover class | `lulc.change_matrix` |
| [Fig. 11](https://doi.org/10.1016/j.scs.2020.102542) | Winter UTFVI share by land cover class | `lulc.change_matrix` |
| [Fig. 12](https://doi.org/10.1016/j.scs.2020.102542) | Predicted land cover, 2029 and 2039 | `caann.CAANN` |
| [Fig. 13](https://doi.org/10.1016/j.scs.2020.102542) | Predicted summer and winter LST | `lstmodel.predict_lst` |
| [Fig. 14](https://doi.org/10.1016/j.scs.2020.102542) | Predicted summer and winter UTFVI | `lstmodel.predict_lst` |
| [Table 1](https://doi.org/10.1016/j.scs.2020.102542) | Landsat scenes used | `data.search_scenes` |
| [Table 2](https://doi.org/10.1016/j.scs.2020.102542) | Land cover area per class, 1999 to 2019 | `lulc.class_areas` |
| [Table 3](https://doi.org/10.1016/j.scs.2020.102542) | Summer LST area by temperature range | `thermal.range_areas` |
| [Table 4](https://doi.org/10.1016/j.scs.2020.102542) | Winter LST area by temperature range | `thermal.range_areas` |
| [Table 5](https://doi.org/10.1016/j.scs.2020.102542) | Summer LST ranges within each land cover class | `thermal.range_areas` |
| [Table 6](https://doi.org/10.1016/j.scs.2020.102542) | Winter LST ranges within each land cover class | `thermal.range_areas` |
| [Table 7](https://doi.org/10.1016/j.scs.2020.102542) | Seasonal UTFVI area by class | `thermal.classify_utfvi` |
| [Table 8](https://doi.org/10.1016/j.scs.2020.102542) | CA model kappa validation, 2019 | `caann.kappa` |
| [Table 9](https://doi.org/10.1016/j.scs.2020.102542) | Predicted land cover area, 2029 and 2039 | `caann.CAANN`, `lulc.class_areas` |
| [Table 10](https://doi.org/10.1016/j.scs.2020.102542) | ANN LST validation (RMSE, R), 2019 | `stats.correlation` |
| [Table 11](https://doi.org/10.1016/j.scs.2020.102542) | Predicted LST area by range | `thermal.range_areas` |
| [Table 12](https://doi.org/10.1016/j.scs.2020.102542) | ANN UTFVI validation (RMSE, R), 2019 | `stats.correlation` |
| [Table 13](https://doi.org/10.1016/j.scs.2020.102542) | Predicted UTFVI area and change by class | `thermal.classify_utfvi` |

## Published tables as data

- `tables/table1_landsat_scenes.csv`: date, sensor and path/row of the six scenes.
- `tables/table2_lulc_area_km2.csv`: area per land cover class in 1999, 2009, 2019 and net change (%).
- `tables/table3_summer_lst_range_area.csv`: summer area (km², %) in five LST ranges.
- `tables/table4_winter_lst_range_area.csv`: winter area (km², %) in five LST ranges.
- `tables/table5_summer_lst_by_lulc.csv`: summer LST range area for each land cover class.
- `tables/table6_winter_lst_by_lulc.csv`: winter LST range area for each land cover class.
- `tables/table7_utfvi_area_km2.csv`: summer and winter area in six UTFVI classes.
- `tables/table8_ca_validation_2019.csv`: kappa values from IDRISI Selva and MOLUSCE.
- `tables/table9_predicted_lulc_area_km2.csv`: predicted class area for 2029 and 2039 and net change.
- `tables/table10_ann_lst_validation_2019.csv`: hidden layers, RMSE and R for LST.
- `tables/table11_predicted_lst_range_area.csv`: predicted summer and winter LST range area.
- `tables/table12_ann_utfvi_validation_2019.csv`: hidden layers, RMSE and R for UTFVI.
- `tables/table13_predicted_utfvi_area_km2.csv`: predicted UTFVI area (km²) and change (%) from 2019.

## Notes

- LST is in °C. Areas are in km². Total area is about 45.25 km².
- LST range breaks: < 21, 21 to < 25, 25 to < 29, 29 to < 33, ≥ 33 °C.
- UTFVI here is (Ts - Tm) / Ts (Eq. 14). The 2022 Sylhet paper divides by Tm instead. `thermal.utfvi` divides by Ts by default; pass `denominator="tmean"` for the other form.
- UTFVI classes: None < 0, Weak 0 to 0.005, Middle 0.005 to 0.010, Strong 0.010 to 0.015, Stronger 0.015 to 0.020, Strongest > 0.020.
- The TM constants are printed as K1 = 1260.56 K and K2 = 607.66. The usual Landsat 5 values are the other way round (K1 = 607.76, K2 = 1260.56). We copied what the paper prints.
- Table 2: the last column header reads "Net Changes (%) 1999-2009", but the text calls it the 20-year (1999 to 2019) net change.
- Some printed values do not agree with each other. We copied them as printed. The text gives 5.29 km² at ≥ 33 °C in summer 2019; Table 3 gives 3.04 km² (5.29 %). In Table 7 the summer rows add to 46.59 km² (1999) and 43.65 km² (2019), not about 45.25 km². In Table 11 (winter 2039), the % values for 25 to < 29 °C and 29 to < 33 °C do not match their km² values. In Tables 5 and 6, the class totals do not always match Table 2.
- Table 6 prints one value with three decimals (2.422). We kept it.
- Classification overall accuracy (text, not a table): 86.04 %, 84.82 % and 87.23 % for 1999, 2009 and 2019.

Figures are not reproduced here. See the paper at the DOI above.
