# Surface heat and carbon storage in coastal Cox's Bazar, 1996 to 2041

> Abdulla Al Kafy, Nataraj Narayan Dey, Milan Saha, Hamad Ahmed Altuwaijri, Md. Abdul Fattah, Zullyadini A. Rahaman, S. Kalaivani, Arpita Bakshi, Sk Nafiz Rahaman (2024). Leveraging machine learning algorithms in dynamic modeling of urban expansion, surface heat islands, and carbon storage for sustainable environmental management in coastal ecosystems. *Journal of Environmental Management*, 370, 122427. [https://doi.org/10.1016/j.jenvman.2024.122427](https://doi.org/10.1016/j.jenvman.2024.122427)

## In one paragraph

The study covers Cox's Bazar, a coastal area in southeast Bangladesh, from 1996 to 2021, with projections to 2031 and 2041. It uses April Landsat 5 TM and Landsat 8 OLI/TIRS Level 2 scenes at 5-year steps. MODIS MOD11A1 gives nighttime LST. A CNN maps seven land cover classes, with an average accuracy of 88%. Daytime LST comes from the thermal band, with emissivity taken from the NDVI vegetation proportion. The InVEST model turns land cover into carbon stock using four carbon pools per class. LST is compared with NDBI, NDVI, NDWI and elevation using regression. Cross-section profiles and directional mapping show how LST and carbon stock vary in space. A CA-ANN model in QGIS MOLUSCE projects LST. Daytime maximum LST rose from 35.26 °C (1996) to 40.8 °C (2021). Mean daytime LST rose from 27.72 to 31.78 °C. The area with no carbon stock grew by 355.78%. By 2041, 22.51% of the area may have LST above 32 °C.

## Key numbers

- Daytime maximum LST rose from 35.26 °C (1996) to 40.8 °C (2021). The minimum rose from 20.17 °C to 22.76 °C. (Fig. 5)
- Mean daytime LST rose from 27.72 °C to 31.78 °C, which the results text calls +4.07 °C. The abstract and conclusion give +3.57 °C. (Fig. 5)
- Mean nighttime LST (MODIS) went from 24.04 °C (2001) to 24.49 °C (2021). (Fig. 6)
- The no-carbon-stock zone grew by 355.78% from 1996 to 2021. The high zone fell by 14.15% and the very high zone by 47.78%. (Fig. 12)
- The LST and NDBI regression had R² from 0.809 to 0.893. The LST and elevation regression had R² from 0.804 to 0.880. (Figs. 8 and 9)
- The CA-ANN validation gave overall kappa 0.83 (2016) and 0.86 (2021), with 91.90% and 92.05% correctness. (Table 5)
- The ROC AUC for the predicted LST was 0.89 (2016) and 0.91 (2021). (Fig. 15)
- By 2041, LST above 32 °C may cover 22.51% of the area, and LST below 24 °C 1.68%. In 1996, 12.87% of the area was below 24 °C. (Fig. 16)

## Method → code

| Step | Paper | Toolkit function |
|---|---|---|
| Get imagery | April Landsat 5 TM and 8 OLI/TIRS C2 L2 scenes, cloud under 10%, 1996 to 2021 at 5-year steps; MODIS MOD11A1 for night LST; SRTM DEM | `data.search_scenes`, `data.load_composite` (MODIS and DEM not included; the paper used single scenes, not composites) |
| Classify land cover | CNN on image patches, 7 classes, 250 random ground truth points per year | `lulc.train_classifier` (Random Forest; the paper used a CNN) |
| Accuracy | Average overall accuracy of 88% | `lulc.accuracy` |
| Spectral indices | NDVI, NDBI, NDWI (Table 4) | `indices.ndvi`, `indices.ndbi`, `indices.ndwi` |
| Emissivity | Pv = ((NDVI − NDVImin)/(NDVImax − NDVImin))², LSE = 0.004 Pv + 0.986 | `thermal.emissivity_from_ndvi` |
| Daytime LST | Radiance, then BT in °C, then emissivity-corrected LST; mean of bands 10 and 11; ArcGIS Pro Model Builder toolbox (Fig. 3) | `thermal.lst_from_bt` (the Model Builder toolbox is desktop only) |
| LST zones | Six daytime LST ranges: <24, 24-<26, 26-<28, 28-<30, 30-<32, ≥32 °C | `thermal.range_areas` |
| LST check against MODIS | 100 random points; mean r 0.92, MAE 1.8 °C | `stats.correlation` |
| Directional pattern | Directional mapping of daytime LST (Fig. 7) | `zones.directional_sectors`, `zones.share_by_zone` |
| Carbon stock | InVEST carbon model with four pools per class (Table 2), then six concentration classes (Table 3) | `carbon.stock_map`, `carbon.stock_change` |
| LST and carbon profiles | Profile lines across LST and carbon rasters (ArcGIS Pro Profile Graph) | `stats.cross_profile` |
| LST vs indices and DEM | About 980 valid stratified points per year; linear, log and polynomial fits; Pearson r; 5-fold cross-validation; GWR | `stats.correlation` (GWR and k-fold not included) |
| LST prediction | CA-ANN (MLP) in QGIS MOLUSCE; 5-fold cross-validation over time steps; 2031 and 2041 | `caann.CAANN` |
| Prediction validation | Kappa set, % correctness (Table 5), sensitivity analysis, ROC AUC | `caann.kappa`, `stats.roc_auc` |

## Figures and tables in the paper

| Item | What it shows | Toolkit function |
|---|---|---|
| [Fig. 1](https://doi.org/10.1016/j.jenvman.2024.122427) | Location of Cox's Bazar in Bangladesh | map / layout |
| [Fig. 2](https://doi.org/10.1016/j.jenvman.2024.122427) | Method flowchart | map / layout |
| [Fig. 3](https://doi.org/10.1016/j.jenvman.2024.122427) | ArcGIS Model Builder LST toolbox | map / layout (logic in `thermal.lst_from_bt`) |
| [Fig. 4](https://doi.org/10.1016/j.jenvman.2024.122427) | MOLUSCE LST prediction workflow | map / layout (model is `caann.CAANN`) |
| [Fig. 5](https://doi.org/10.1016/j.jenvman.2024.122427) | Daytime LST zone maps, 1996 to 2021 | `thermal.lst_from_bt`, `thermal.range_areas` |
| [Fig. 6](https://doi.org/10.1016/j.jenvman.2024.122427) | Nighttime LST maps, 2001 to 2021 | not included (MODIS night LST) |
| [Fig. 7](https://doi.org/10.1016/j.jenvman.2024.122427) | Directional mapping of daytime LST | `zones.directional_sectors`, `zones.share_by_zone` |
| [Fig. 8](https://doi.org/10.1016/j.jenvman.2024.122427) | LST against NDBI, per year | `stats.correlation` |
| [Fig. 9](https://doi.org/10.1016/j.jenvman.2024.122427) | LST against elevation, per year | `stats.correlation` |
| [Fig. 10](https://doi.org/10.1016/j.jenvman.2024.122427) | LST against NDVI, per year | `stats.correlation` |
| [Fig. 11](https://doi.org/10.1016/j.jenvman.2024.122427) | LST against NDWI, per year | `stats.correlation` |
| [Fig. 12](https://doi.org/10.1016/j.jenvman.2024.122427) | Carbon stock class maps, 1996 to 2021 | `carbon.stock_map` |
| [Fig. 13](https://doi.org/10.1016/j.jenvman.2024.122427) | LST and carbon stock along profile lines | `stats.cross_profile` |
| [Fig. 14](https://doi.org/10.1016/j.jenvman.2024.122427) | Sensitivity check, predicted vs estimated LST | `stats.correlation` |
| [Fig. 15](https://doi.org/10.1016/j.jenvman.2024.122427) | ROC curves for 2016 and 2021 LST predictions | `stats.roc_auc` |
| [Fig. 16](https://doi.org/10.1016/j.jenvman.2024.122427) | Predicted daytime LST for 2031 and 2041 | `lstmodel.predict_lst`, `thermal.range_areas` |
| [Fig. 17](https://doi.org/10.1016/j.jenvman.2024.122427) | Change in LST range shares, 1996 to 2041 | `thermal.range_areas` |
| [Table 1](https://doi.org/10.1016/j.jenvman.2024.122427) | Landsat and MODIS scenes used | `data.search_scenes` |
| [Table 2](https://doi.org/10.1016/j.jenvman.2024.122427) | Carbon density per pool and class | `carbon.stock_map` |
| [Table 3](https://doi.org/10.1016/j.jenvman.2024.122427) | Carbon stock concentration class thresholds | `carbon.stock_map` |
| [Table 4](https://doi.org/10.1016/j.jenvman.2024.122427) | Index formulas and Landsat bands | `indices.ndbi`, `indices.ndvi`, `indices.ndwi` |
| [Table 5](https://doi.org/10.1016/j.jenvman.2024.122427) | Kappa validation of predicted LST | `caann.kappa` |

## Published tables as data

- `tables/table1_landsat_scenes.csv`: six Landsat scenes (date, scene ID, sensor, cloud, path/row) and five MODIS MOD11A1 dates.
- `tables/table2_carbon_density_mg_km2.csv`: above-ground, below-ground, soil and dead carbon per class in Mg/km², with the source paper.
- `tables/table3_carbon_stock_classes_mg_km2.csv`: lower and upper bounds (Mg/km²) of the six carbon stock classes.
- `tables/table5_lst_prediction_validation.csv`: model validation kappa, % correctness, Kappa histo, Kappa loc and Kappa overall for 2016 and 2021.

## Notes

- LST is in °C. Carbon density is in Mg/km² as printed (divide by 100 for Mg/ha). Brightness temperature is converted with −273.15.
- Each Table 3 class break equals the summed four-pool density of one class in Table 2: 22360 (Grassland), 23660 (Crop Land), 26244 (Bare Land), 28672 (Vegetation) and 48015 (Evergreen Forest). The lowest bound, 5900, is not explained.
- Outliers above the mean + 3 SD of LST were removed each year (about 0.1% of pixels).
- The paper reports R² as negative (−0.795 to −0.842) for vegetation indices in the abstract and conclusion. The results text gives R² of 0.0483 to 0.191 for LST and NDVI (Fig. 10) and 0.0002 to 0.1421 for LST and NDWI (Fig. 11).
- Some numbers in the paper do not agree with each other. Mean daytime warming is +3.57 °C in the abstract and +4.07 °C in the results. Night LST is −0.05 °C in the abstract and discussion but +0.46 °C in the results. The discussion swaps the high (14.15%) and very high (47.78%) losses. Table 1 lists a 2010 scene, while the text and figures use 2011. The Table 4 NDVI formula is printed as (NIR − R)/(NIR − R), which is a typo for (NIR − R)/(NIR + R). Section 2.6 says three profile lines, but the Fig. 13 maps show four (A-B, C-D, E-F, G-H).
- The text says the CA-ANN model reached Kappa above 0.80, overall accuracy above 85% and AUC above 0.89. The full metrics are in Table 5.

Figures are not reproduced here. See the paper at the DOI above.
