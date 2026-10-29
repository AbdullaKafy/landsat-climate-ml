"""landsat_climate: land cover, surface heat, carbon and drought from Landsat.

Reusable code behind a series of published studies by Abdulla Al Kafy and
co-authors. Modules:

data      Landsat Collection 2 Level-2 composites, DEM and WorldCover (STAC)
indices   NDVI, NDBI, NDWI, MNDWI, SAVI, EVI, BSI
thermal   LST (single-channel), UHI, UTFVI and their classes
lulc      Random Forest land cover, accuracy, change matrix, gain and loss
caann     Markov + neural network cellular automata (CA-ANN) land change
lstmodel  Neural network that predicts LST from land cover
carbon    Carbon stock and change from land cover (InVEST style)
drought   VCI, TCI, VHI and drought classes
zones     Directional sectors and rings around a city center
stats     Correlation, ROC AUC and cross profiles
"""

__version__ = "0.2.0"
