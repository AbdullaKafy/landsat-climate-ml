# Forest cover change and carbon storage in the Chittagong Hill Tracts

> Kafy, A.-A., Saha, M., Fattah, M.A., Rahman, M.T., Duti, B.M., Rahaman, Z.A., Bakshi, A., Kalaivani, S., Rahaman, S.N., Sattar, G.S. (2023). Integrating forest cover change and carbon storage dynamics: Leveraging Google Earth Engine and InVEST model to inform conservation in hilly regions. *Ecological Indicators*, 152, 110374. https://doi.org/10.1016/j.ecolind.2023.110374

## In one paragraph

The study covers the Chittagong Hill Tracts (CHT) region of Bangladesh, about 15,516 km², across five districts: Chittagong, Cox's Bazar, Bandarban, Rangamati and Khagrachari. It uses six April Landsat scenes from 1996 to 2021 (TM for 1996 to 2011, OLI for 2016 and 2021). Land cover was mapped in Google Earth Engine with a maximum likelihood classifier into five classes. Changes were found with the Land Change Modeler. Carbon storage was mapped with the InVEST carbon model, using four carbon pools per class (above-ground, below-ground, soil, dead organic matter). A multiple linear regression tested elevation, NDVI, EVI and rainfall as drivers. Vegetation fell by 2862.86 km² (21%), and built-up area grew by 466.27 km² (388%). Carbon storage fell from 495.93 × 10⁶ Mg in 1996 to 479.63 × 10⁶ Mg in 2021. Chittagong lost the most carbon (7.99 × 10⁶ Mg).

## Key numbers

- Kappa was 90.18, 91.85, 92.63, 93.66, 93.57 and 93.32 for 1996 to 2021 (Section 2.4).
- Vegetation fell by 2862.86 km² (21%); built-up area rose by 466.27 km² (388%); agricultural land rose by 2520.87 km² (66%) (Section 3.1, Fig. 4).
- Total carbon storage was 495.93 × 10⁶ Mg in 1996 and 479.63 × 10⁶ Mg in 2021 (Section 5).
- The abstract reports a total loss of 21.65 × 10⁶ Mg of carbon storage (Abstract).
- Carbon loss by district, 1996 to 2021: Chittagong 7.99, Cox's Bazar 5.36, Bandarban 3.86, Rangamati 3.53, Khagrachari 0.92 × 10⁶ Mg (Fig. 9).
- Vegetation held 79% (393.81 × 10⁶ Mg) of carbon storage in 1996 and 65% (311.72 × 10⁶ Mg) in 2021 (Fig. 10).
- Carbon density per class (Mg/km²), above + below + soil + dead: vegetation 410 + 5640 + 22,600 + 22; crop land 4650 + 8070 + 10,840 + 100 (Table 3).

## Method → code

| Step | Paper | Toolkit function |
|---|---|---|
| Get imagery | Six April Landsat scenes, path/row 136/44, < 5% cloud; corrected in ERDAS Imagine | `data.search_scenes`, `data.load_composite` (toolkit uses C2 L2 median composites; the paper used single C1 Level-1 scenes) |
| Land cover map | Maximum likelihood supervised classification in GEE, five classes | `lulc.train_classifier` (Random Forest; paper used maximum likelihood) |
| Accuracy | More than 500 points per year, overall, user, producer accuracy, kappa | `lulc.accuracy` |
| Class areas | Area per class and district | `lulc.class_areas` |
| Change detection | Land Change Modeler (LCM) | `lulc.change_matrix`, `lulc.gain_loss` |
| Carbon storage | InVEST carbon model, four pools per class (Table 3) | `carbon.stock_map` |
| Carbon change | S = C(T2) − C(T1), per pixel | `carbon.stock_change` |
| Carbon by district | Gain and loss per district | `carbon.stock_change` with `zones.share_by_zone` |
| Vegetation indices | NDVI and EVI in GEE | `indices.ndvi`, `indices.evi` |
| Drivers | Multiple linear regression: rainfall, NDVI, EVI, elevation vs carbon | not included: the toolkit has pairwise `stats.correlation` only |

## Figures and tables in the paper

| Item | What it shows | Toolkit function |
|---|---|---|
| [Fig. 1](https://doi.org/10.1016/j.ecolind.2023.110374) | Location of the CHT study area | map / layout |
| [Fig. 2](https://doi.org/10.1016/j.ecolind.2023.110374) | Method flowchart | map / layout |
| [Fig. 3](https://doi.org/10.1016/j.ecolind.2023.110374) | Land cover maps of CHT, six years | `lulc.train_classifier` |
| [Fig. 4](https://doi.org/10.1016/j.ecolind.2023.110374) | Land cover areas over time | `lulc.class_areas` |
| [Fig. 5](https://doi.org/10.1016/j.ecolind.2023.110374) | Maps of land cover conversions | `lulc.change_matrix` |
| [Fig. 6](https://doi.org/10.1016/j.ecolind.2023.110374) | Land cover transitions by district | `lulc.gain_loss` |
| [Fig. 7](https://doi.org/10.1016/j.ecolind.2023.110374) | Carbon storage maps, six years | `carbon.stock_map` |
| [Fig. 8](https://doi.org/10.1016/j.ecolind.2023.110374) | Carbon storage change maps, 1996 to 2021 | `carbon.stock_change` |
| [Fig. 9](https://doi.org/10.1016/j.ecolind.2023.110374) | Carbon storage change by district | `carbon.stock_change` |
| [Fig. 10](https://doi.org/10.1016/j.ecolind.2023.110374) | Carbon storage share by land cover class | `carbon.stock_map` |
| [Table 1](https://doi.org/10.1016/j.ecolind.2023.110374) | Landsat scenes used | `data.search_scenes` |
| [Table 2](https://doi.org/10.1016/j.ecolind.2023.110374) | Land cover class definitions | `lulc.train_classifier` |
| [Table 3](https://doi.org/10.1016/j.ecolind.2023.110374) | Carbon density pools per land cover class | `carbon.stock_map` |

## Published tables as data

- `tables/table1_landsat_scenes.csv`: dates, scene IDs, sensor, cloud cover, path/row.
- `tables/table3_carbon_density_mg_per_km2.csv`: above-ground, below-ground, soil and dead organic carbon (Mg/km²) per class, with the source reference.

Table 2 (class definitions) has no numbers and is not saved. Tables S1 to S3 and Figs. S1 to S4 are in the online supplement, not in the article PDF.

## Notes

- Carbon pools are printed in Mg/km². To use Mg/ha, divide by 100 (for example vegetation soil carbon 22,600 Mg/km² = 226 Mg/ha).
- InVEST total per cell: C = A × (Ca + Cb + Cs + Cd). Sum of pools per class (Mg/km²): water 12,023; vegetation 28,672; built-up 16,277; crop 23,660; bare 26,244.
- The paper reports the carbon density map range as 9.39 to 22.40 Mg/km² (Fig. 7). This range is much lower than the Table 3 pool sums; the paper does not explain the difference.
- Carbon totals are written as "× 10⁶ Mg/year" in the results, but they are stock totals. 495.93 − 479.63 = 16.30 × 10⁶ Mg, which matches "decreased by 16.3 × 10⁶" in Section 3.2 but not the 21.65 × 10⁶ Mg in the abstract.
- Vegetation loss is 2862.85 km² in the abstract and 2862.86 km² in Section 3.1.
- Land cover classes: water body, vegetation land, built-up area, crop land, bare land.

This article is open access under CC BY 4.0.
