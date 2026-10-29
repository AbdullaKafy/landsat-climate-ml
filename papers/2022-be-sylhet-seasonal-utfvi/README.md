# Land cover change and seasonal UTFVI in Sylhet, Bangladesh

> Abdulla - Al Kafy, Milan Saha, Abdullah-Al- Faisal, Zullyadini A. Rahaman, Muhammad Tauhidur Rahman, Desheng Liu, Md. Abdul Fattah, Abdullah Al Rakib, Ahmad E. AlDousari, Sk Nafiz Rahaman, Md Zakaria Hasan, Md Ahasanul Karim Ahasan (2022). Predicting the impacts of land use/land cover changes on seasonal urban thermal characteristics using machine learning algorithms. *Building and Environment*, 217, 109066. https://doi.org/10.1016/j.buildenv.2022.109066

## In one paragraph

The study area is Sylhet City Corporation (SCC), Bangladesh, about 26.5 km². The authors used 12 Landsat scenes (Landsat 4-5 TM and Landsat 8 OLI), one summer and one winter scene every five years from 1995 to 2020. They mapped four land cover classes with SVM. They computed the seasonal urban thermal field variance index (UTFVI) in six classes. They mapped change by 16 directions around the city center. A CA-ANN model (MOLUSCE plugin) predicted land cover for 2025 and 2030. An ANN in MATLAB, on a 500 m grid, predicted seasonal UTFVI for 2025 and 2030. Built-up land grew from 14.52 % of the city in 1995 to 52.66 % in 2020. It is predicted to reach 58.93 % in 2030. Vegetation fell from 57.62 % to 40.27 %. From 1995 to 2030, the summer strong, stronger and strongest UTFVI areas are predicted to grow by about 20.42, 26.762 and 3.53 km².

## Key numbers

- Built-up land: 14.52 % (1995), 52.66 % (2020), 56.62 % (2025) and 58.93 % (2030) of the city (Table 8).
- Vegetation: 57.62 % (1995), 40.27 % (2020) and 35.32 % (2030) (Table 8).
- Change 1995 to 2030: built-up +44.41, vegetation -22.30, bare land -20.79, water -1.32 percentage points (Table 8).
- SVM overall accuracy 88.11 % to 93 %, kappa 83.8 % to 90.67 % across the six years (Table 4).
- CA model check for 2020: chi-square 0.049, well below the critical value 7.815 at 3 degrees of freedom (Table 5).
- CA model overall kappa: 0.9507 (2015) and 0.94528 (2020) (Table 6).
- ANN UTFVI check for 2020: RMSE 0.56 and R 0.88 (summer), RMSE 0.624 and R 0.87 (winter) (Table 7).
- Summer, 1995 to 2030: strong, stronger and strongest UTFVI areas grow by about 20.42, 26.762 and 3.53 km² (Fig. 17).

## Method → code

| Step | Paper | Toolkit function |
|---|---|---|
| Get scenes | 12 single Landsat scenes, path/row 136/43, cloud < 10 % | `data.search_scenes`, `data.load_composite` (toolkit uses Collection 2 Level 2 median composites, not single scenes) |
| Land cover map | SVM in ENVI 5.3, RBF kernel, 4 classes | `lulc.train_classifier` (Random Forest; the paper used SVM) |
| Accuracy | User, producer, overall accuracy and kappa | `lulc.accuracy` |
| Class share and gain/loss | % per class per year; gain and loss 1995 to 2020 | `lulc.class_areas`, `lulc.gain_loss` |
| LST | Seasonal LST was extracted, but the paper does not give the LST steps | `thermal.lst_from_bt` |
| UTFVI | (Ts - Tm) / Tm, six classes (Table 2) | `thermal.utfvi(lst, denominator="tmean")`, `thermal.classify_utfvi` |
| UTFVI by land cover | ArcGIS Tabulate Area between UTFVI and land cover rasters | `lulc.change_matrix` (cross-tab of two class rasters) |
| Directional change | Rings at 200 m intervals around the urban center, cut into 16 equal sectors | `zones.directional_sectors`, `zones.concentric_rings`, `zones.share_by_zone` |
| Future land cover | CA with ANN transition potential in MOLUSCE (QGIS); drivers: commercial space, distance to roads, slope, elevation, schools, water | `caann.transition_matrix`, `caann.CAANN` |
| Land cover model check | Chi-square between actual and predicted 2020; kappa in MOLUSCE for 2015 and 2020 | `caann.chi_square_validation`, `caann.kappa` |
| Index inputs | NDBI, NDVI, NDBSI, NDWI as ANN inputs | `indices.ndbi`, `indices.ndvi`, `indices.bsi`, `indices.ndwi` (BSI is close to, but not the same as, NDBSI) |
| Future UTFVI | ANN (MLP) in MATLAB on a 500 m grid; compared with ResNet, GoogLeNet, VGGNet, AlexNet | `lstmodel.fit_lst_model`, `lstmodel.predict_lst` (scikit-learn MLP on the pixel grid; the paper used MATLAB on a 500 m grid) |
| Model fit | RMSE and R between predicted and actual 2020 UTFVI | `stats.correlation` |

## Figures and tables in the paper

| Item | What it shows | Toolkit function |
|---|---|---|
| [Fig. 1](https://doi.org/10.1016/j.buildenv.2022.109066) | Flow chart of the method | map / layout |
| [Fig. 2](https://doi.org/10.1016/j.buildenv.2022.109066) | Study area location | map / layout |
| [Fig. 3](https://doi.org/10.1016/j.buildenv.2022.109066) | ANN process for seasonal UTFVI prediction | map / layout |
| [Fig. 4](https://doi.org/10.1016/j.buildenv.2022.109066) | Land cover maps, 1995 to 2020 | `lulc.train_classifier` |
| [Fig. 5](https://doi.org/10.1016/j.buildenv.2022.109066) | Land cover class change, 1995 to 2020 | `lulc.class_areas` |
| [Fig. 6](https://doi.org/10.1016/j.buildenv.2022.109066) | Gain and loss per land cover class | `lulc.gain_loss` |
| [Fig. 7](https://doi.org/10.1016/j.buildenv.2022.109066) | Land cover by direction, six years | `zones.share_by_zone` |
| [Fig. 8](https://doi.org/10.1016/j.buildenv.2022.109066) | Summer UTFVI maps, six years | `thermal.classify_utfvi` |
| [Fig. 9](https://doi.org/10.1016/j.buildenv.2022.109066) | Winter UTFVI maps, six years | `thermal.classify_utfvi` |
| [Fig. 10](https://doi.org/10.1016/j.buildenv.2022.109066) | Percent of city in each seasonal UTFVI class | `thermal.classify_utfvi` |
| [Fig. 11](https://doi.org/10.1016/j.buildenv.2022.109066) | Summer UTFVI by direction | `zones.share_by_zone` |
| [Fig. 12](https://doi.org/10.1016/j.buildenv.2022.109066) | Winter UTFVI by direction | `zones.share_by_zone` |
| [Fig. 13](https://doi.org/10.1016/j.buildenv.2022.109066) | Summer UTFVI share by land cover class | `lulc.change_matrix` |
| [Fig. 14](https://doi.org/10.1016/j.buildenv.2022.109066) | Winter UTFVI share by land cover class | `lulc.change_matrix` |
| [Fig. 15](https://doi.org/10.1016/j.buildenv.2022.109066) | Predicted land cover, 2025 and 2030 | `caann.CAANN` |
| [Fig. 16](https://doi.org/10.1016/j.buildenv.2022.109066) | Predicted summer UTFVI, 2025 and 2030 | `lstmodel.predict_lst` |
| [Fig. 17](https://doi.org/10.1016/j.buildenv.2022.109066) | Spider chart of summer UTFVI area change | `thermal.classify_utfvi` |
| [Fig. 18](https://doi.org/10.1016/j.buildenv.2022.109066) | Predicted winter UTFVI, 2025 and 2030 | `lstmodel.predict_lst` |
| [Fig. 19](https://doi.org/10.1016/j.buildenv.2022.109066) | Spider chart of winter UTFVI area change | `thermal.classify_utfvi` |
| [Table 1](https://doi.org/10.1016/j.buildenv.2022.109066) | Landsat scenes used | `data.search_scenes` |
| [Table 2](https://doi.org/10.1016/j.buildenv.2022.109066) | UTFVI class thresholds | `thermal.classify_utfvi` |
| [Table 3](https://doi.org/10.1016/j.buildenv.2022.109066) | Five prediction algorithms compared | `stats.correlation` |
| [Table 4](https://doi.org/10.1016/j.buildenv.2022.109066) | Land cover map accuracy | `lulc.accuracy` |
| [Table 5](https://doi.org/10.1016/j.buildenv.2022.109066) | CA model chi-square check, 2020 | `caann.chi_square_validation` |
| [Table 6](https://doi.org/10.1016/j.buildenv.2022.109066) | CA model kappa check, 2015 and 2020 | `caann.kappa` |
| [Table 7](https://doi.org/10.1016/j.buildenv.2022.109066) | ANN UTFVI check (RMSE, R), 2020 | `stats.correlation` |
| [Table 8](https://doi.org/10.1016/j.buildenv.2022.109066) | Past and predicted land cover share | `lulc.class_areas` |

## Published tables as data

- `tables/table1_landsat_scenes.csv`: date, scene ID and sensor of the 12 scenes.
- `tables/table3_algorithm_comparison.csv`: fitted line, MSE and R for five algorithms.
- `tables/table4_lulc_accuracy.csv`: user and producer accuracy per class, overall accuracy and kappa (%).
- `tables/table5_ca_chi_square_2020.csv`: actual vs predicted 2020 class share and chi-square terms.
- `tables/table6_ca_kappa_validation.csv`: MOLUSCE % correctness and kappa values for 2015 and 2020.
- `tables/table7_ann_utfvi_validation_2020.csv`: hidden layers, RMSE and R for UTFVI.
- `tables/table8_lulc_pct.csv`: % of city per class for 1995 to 2030 and change rows.

Table 2 (UTFVI class breaks) is not a CSV. Its values are in `paper.json` under `method_details`.

## Notes

- Land cover results are in % of the city area (Table 8). The city area is about 26.5 km².
- UTFVI here is (Ts - Tm) / Tm (Eq. 3). The 2021 Cumilla paper divided by Ts.
- UTFVI classes: None < 0, Weak 0 to 0.005, Middle 0.005 to 0.010, Strong 0.010 to 0.015, Stronger 0.015 to 0.020, Strongest > 0.020 (Table 2).
- The paper has no table of UTFVI area by class. UTFVI areas appear only in figures and in the text.
- Table 3: the column labeled "MSE" holds values near 0.85 to 0.90, and the "R" column holds 0.51 to 0.69. We copied them as printed.
- The paper does not describe how LST was computed.
- Directional analysis: the methods describe 200 m rings and 16 sectors. The results text says "16 concentrated circles ... at each 5-km random equal interval".
- The abstract says "2025 and 2035". The methods and tables use 2025 and 2030.

Figures are not reproduced here. See the paper at the DOI above.
