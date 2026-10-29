# Urban growth and its environmental effects across Saudi Arabia

> Almulhim, A.I., Kafy, A.A., Ferdous, M.N., Fattah, Md.A., Morshed, S.R. (2024). Harnessing urban analytics and machine learning for sustainable urban development: A multidimensional framework for modeling environmental impacts of urbanization in Saudi Arabia. *Journal of Environmental Management*, 357, 120705. [https://doi.org/10.1016/j.jenvman.2024.120705](https://doi.org/10.1016/j.jenvman.2024.120705)

## In one paragraph

The study covers the whole Kingdom of Saudi Arabia (KSA), an area of 2,149,690 km², from 1987 to 2022. It uses summer Landsat 5 and Landsat 8 surface reflectance images at 5-year steps. All data were processed in Google Earth Engine. Urban areas come from an object-based deep learning classification. The paper describes urban growth with expanding speed and intensity indices and a gravity center. It then maps environmental parameters: EVI, NDBI, MNDWI, NDISI and UTFVI from Landsat, soil moisture from GLDAS-2, and PM2.5, CH4, CO, SO2 and NO2 from NASA GEOS-CF. Nighttime light comes from DMSP-OLS. Each parameter is linked to urban expansion with a simple regression (EP = β0 + β1·UE + ε), and PCA ranks which ones are most affected. Built-up land grew from 0.067% to 0.14% of the country. Mean soil moisture fell from 15.76% to 14.02%. Mean PM2.5 rose from 44.25 to 73.36 μg/m³. PCA gave the highest PC1 loadings to PM2.5 (0.94), UTFVI (0.92) and NO2 (0.88).

## Key numbers

- Built-up area was 1440.29 km² in 1987, which is 0.067% of the country (Section 3.1, Fig. 2).
- Built-up share reached 0.14% in 2022 (Fig. 2).
- The highest MNDWI value fell from 0.6085 in 1987 to 0.2240 in 2022 (Section 3.2.1, Fig. 5).
- Mean soil moisture fell from 15.76% in 2002 to 14.02% in 2022 (Section 3.3, Fig. 7).
- Mean PM2.5 rose from 44.25 μg/m³ to 73.36 μg/m³. The 2022 maximum was 126.45 μg/m³ (Section 3.6, Fig. 9).
- Mean SO2 rose from 4.54×10⁻⁴ to 5.07×10⁻⁴ mol/m³ (Section 3.6, Fig. 12).
- The urban expansion relationship with NDBI rose from 0.776 in 1987 to 0.880 in 2022 (Table 2).
- PC1 loadings: PM2.5 0.94, UTFVI 0.92, NO2 0.88, EVI 0.87, soil moisture 0.82 (Table 4).

## Method → code

| Step | Paper | Toolkit function |
|---|---|---|
| Images | Cloud-free summer Landsat 5 and 8 surface reflectance, 30 m, 1987 to 2022, in Google Earth Engine | `data.search_scenes`, `data.load_composite` |
| Land cover | Object-based classification: minimum spanning tree segmentation, then a stacked (denoising) autoencoder. Four classes: urban, water, vegetation, bare land. | `lulc.train_classifier`. The toolkit uses Random Forest. The paper used a deep-learning OBIC. |
| Urban area | Built-up area per year | `lulc.class_areas` |
| Accuracy | ROC AUC on the urban map, over 90% | `stats.roc_auc` |
| Urban speed and intensity | Mue = ΔU/Δt and Iue = ΔU/ULA per directional zone (Eqs. 1 to 2) | `lulc.expansion_indices` per zone from `zones.directional_sectors` |
| Gravity center | Area-weighted center, travel distance L and angle α (Eqs. 3 to 6) | `zones.gravity_center` (distance and angle between years are simple geometry). |
| Vegetation | EVI (Eq. 7) | `indices.evi` |
| Built-up | NDBI (Eq. 8), five manual classes | `indices.ndbi` |
| Water | MNDWI (Eq. 9) | `indices.mndwi` |
| Impervious surface | NDISI written as (SWIR2 − NIR)/(SWIR2 + NIR) (Eq. 10) | not included. This form is NDBI with SWIR2. `indices.ndbi` is the nearest match. |
| Soil moisture | GLDAS-2, 2002 to 2022 | not included. This is an outside model dataset. |
| LST | Landsat surface temperature product | `thermal.lst_from_bt` (the toolkit derives LST itself) |
| Thermal comfort | UTFVI (Eq. 11) | `thermal.utfvi`, `thermal.classify_utfvi`. The paper's formula differs from the default (see Notes). |
| Air pollutants | PM2.5, CH4, CO, SO2, NO2 from NASA GEOS-CF 1-hour data | not included. This is a model dataset, not a Landsat product. |
| Night light | DMSP-OLS Nighttime Lights Time Series Version 4 | not included. This is an outside dataset. |
| Regression | EP = β0 + β1·UE + ε for each parameter, in ArcGIS Pro (Table 1) | `stats.correlation` |
| PCA | Mean-centered covariance PCA, loadings ranked | `stats.pca_loadings` |

## Figures and tables in the paper

| Item | What it shows | Toolkit function |
|---|---|---|
| [Fig. 1](https://doi.org/10.1016/j.jenvman.2024.120705) | Saudi Arabia and its provinces | map / layout |
| [Fig. 2](https://doi.org/10.1016/j.jenvman.2024.120705) | Urban expansion direction and share, 1987 to 2022 | `lulc.class_areas`, `zones.directional_sectors` |
| [Fig. 3](https://doi.org/10.1016/j.jenvman.2024.120705) | Vegetation health (EVI), 1987 to 2022 | `indices.evi` |
| [Fig. 4](https://doi.org/10.1016/j.jenvman.2024.120705) | Built-up density (NDBI), 1987 to 2022 | `indices.ndbi` |
| [Fig. 5](https://doi.org/10.1016/j.jenvman.2024.120705) | Water bodies (MNDWI), 1987 to 2022 | `indices.mndwi` |
| [Fig. 6](https://doi.org/10.1016/j.jenvman.2024.120705) | Imperviousness (NDISI), 1987 to 2022 | not included (NDISI) |
| [Fig. 7](https://doi.org/10.1016/j.jenvman.2024.120705) | GLDAS soil moisture, 2002 to 2022 | not included (GLDAS) |
| [Fig. 8](https://doi.org/10.1016/j.jenvman.2024.120705) | Thermal comfort (UTFVI), 1987 to 2022 | `thermal.utfvi` |
| [Fig. 9](https://doi.org/10.1016/j.jenvman.2024.120705) | PM2.5 concentration maps | not included (GEOS-CF) |
| [Fig. 10](https://doi.org/10.1016/j.jenvman.2024.120705) | CH4 concentration maps | not included (GEOS-CF) |
| [Fig. 11](https://doi.org/10.1016/j.jenvman.2024.120705) | CO concentration maps | not included (GEOS-CF) |
| [Fig. 12](https://doi.org/10.1016/j.jenvman.2024.120705) | SO2 concentration maps | not included (GEOS-CF) |
| [Fig. 13](https://doi.org/10.1016/j.jenvman.2024.120705) | NO2 concentration maps | not included (GEOS-CF) |
| [Fig. 14](https://doi.org/10.1016/j.jenvman.2024.120705) | DMSP nighttime light, 1992 to 2022 | not included (DMSP-OLS) |
| [Table 1](https://doi.org/10.1016/j.jenvman.2024.120705) | Regression equations, one per parameter | `stats.correlation` |
| [Table 2](https://doi.org/10.1016/j.jenvman.2024.120705) | Urban expansion vs land parameters by year | `stats.correlation` |
| [Table 3](https://doi.org/10.1016/j.jenvman.2024.120705) | Urban expansion vs thermal, air and light parameters | `stats.correlation` |
| [Table 4](https://doi.org/10.1016/j.jenvman.2024.120705) | PCA loadings, PC1 and PC2 | `stats.pca_loadings` |

## Published tables as data

- `tables/table2_urban_expansion_vs_land_eps.csv`: urban expansion relationship values for NDBI, NDISI, soil moisture, EVI and MNDWI per year.
- `tables/table3_urban_expansion_vs_thermal_air_eps.csv`: urban expansion relationship values for UTFVI, PM2.5, SO2, NO2, CH4, CO and NLP per year.
- `tables/table4_pca_loadings.csv`: PC1 and PC2 loadings for 10 parameters.

## Notes

- All data were processed in Google Earth Engine. The regression was run in ArcGIS Pro.
- The air pollutant data are NASA GEOS-CF (Goddard Earth Observing System Composition Forecast, 1-hour). They are not Sentinel-5P.
- The text says the pollutant maps are for 2018 and 2022, and Tables 2 and 3 use 2018. But the Fig. 9 to 13 captions say 2019 to 2022, and the Fig. 9 panels are labeled 2019 and 2022.
- Fig. 14 gives the night light data as DMSP, from the Earth Observation Group, Payne Institute for Public Policy, at 30 arc-seconds (about 1 km), in EPSG:4326.
- Tables 2 and 3 are called "relationship assessment" and correlation in the text. The paper does not say if the values are r, R² or β1. Empty cells mean that the paper prints "-" (no data that year).
- The paper writes UTFVI = (LSTmax − LSTmin)/(LSTmax + LSTmin). This is not the usual per-pixel form, (Ts − Tmean)/Ts. Its UTFVI values ran from −1.20 to 0.946.
- The paper writes NDISI as (SWIR2 − NIR)/(SWIR2 + NIR). Its text, however, describes NDISI with SWIR and MIR.
- The PCA text gives UTFVI PC1 as 0.94, but Table 4 gives 0.92. The CSV follows Table 4.
- The PCA text lists 12 variables (including LST and NLP), but Table 4 shows 10.
- The built-up increments in Section 3.1 (257.97, 451.44 and 859.88 km²) and the stated total rise of 28,655.37 km² do not add up. The figures are reported as printed. The 0.067% and 0.14% shares agree with Fig. 2.
- The abstract gives night light as 0.166 to 9.670. The text and Fig. 14 give 0.1625 to 9670.04.
- The paper lists no Landsat scenes. No scene table is included.

Figures are not reproduced here. See the paper at the DOI above.
