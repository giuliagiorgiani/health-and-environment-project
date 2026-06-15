import geopandas as gpd
import pandas as pd
# =====================================================
# LAND USE CHARACTERIZATION OF TEMPERATURE POLYGONS
# =====================================================
#
# Input:
#   temperature_voronoi.shp
#   dusaf6.shp
#   dusaf6_lut.xls
#
# Output:
#   polygon_landuse_summary.csv
#
# Processing steps:
#   1. Load temperature Voronoi polygons
#   2. Load DUSAF land-use data
#   3. Merge land-use lookup table
#   4. Dissolve detailed classes into Level-1 classes
#   5. Intersect land use with Voronoi polygons
#   6. Calculate land-use area within each polygon
#   7. Calculate percentage land-use composition
#
# Output variables:
#   IdSensore
#   LIVELLO_1_DESCRIZIONE
#   area_m2
#   percentage
#
# =====================================================
# =====================================================
# LOAD TRUE VORONOI POLYGONS
# =====================================================

master = gpd.read_file(
    "temperature_voronoi.shp"
)

print(master.head())

print(master.columns)

print(master.crs)

print(master.shape)

print(
    master["IdSensore"].nunique()
)

# =====================================================
# LOAD DUSAF LAND USE
# =====================================================

dusaf = gpd.read_file(
    "land_use/REGIONE_LOMBARDIA/dusaf6.shp"
)
print(dusaf.head())

print(dusaf.columns)

print(dusaf.crs)

# =====================================================
# LOAD LOOKUP TABLE
# =====================================================

lut = pd.read_excel(
    "land_use/dusaf6_lut.xls"
)

print(lut.head())

print(lut.columns)

# =====================================================
# PREPARE LAND USE LABELS
# =====================================================

dusaf["LIV_1"] = dusaf["LIV_1"].astype(int)

dusaf = dusaf.merge(
    lut,
    left_on="LIV_1",
    right_on="LIVELLO_1",
    how="left"
)

print(
    dusaf[
        [
            "LIVELLO_1",
            "LIVELLO_1_DESCRIZIONE"
        ]
    ].head()
)

# =====================================================
# MATCH CRS
# =====================================================

master = master.to_crs(
    dusaf.crs
)

print(master.crs)

# =====================================================
# SIMPLIFY LAND USE
# =====================================================

dusaf_simple = (
    dusaf.dissolve(
        by="LIVELLO_1_DESCRIZIONE"
    )
    .reset_index()
)

print(dusaf_simple.head())

print(dusaf_simple.shape)

# =====================================================
# OVERLAY LAND USE WITH POLYGONS
# =====================================================

dusaf_master = gpd.overlay(
    dusaf_simple,
    master,
    how="intersection"
)

print(dusaf_master.head())

print(dusaf_master.shape)

# =====================================================
# CALCULATE AREA
# =====================================================

dusaf_master["area_m2"] = (
    dusaf_master.geometry.area
)

print(
    dusaf_master[
        [
            "IdSensore",
            "LIVELLO_1_DESCRIZIONE",
            "area_m2"
        ]
    ].head()
)

# =====================================================
# SUMMARIZE AREA BY POLYGON + LAND USE
# =====================================================

landuse_summary = (
    dusaf_master.groupby(
        [
            "IdSensore",
            "LIVELLO_1_DESCRIZIONE"
        ]
    )["area_m2"]
    .sum()
    .reset_index()
)

print(landuse_summary.head())

print(landuse_summary.shape)

# =====================================================
# TOTAL AREA OF EACH POLYGON
# =====================================================

polygon_total = (
    landuse_summary.groupby(
        "IdSensore"
    )["area_m2"]
    .sum()
    .reset_index(name="total_area")
)

# =====================================================
# MERGE TOTAL AREA
# =====================================================

landuse_summary = landuse_summary.merge(
    polygon_total,
    on="IdSensore",
    how="left"
)

# =====================================================
# CALCULATE PERCENTAGE
# =====================================================

landuse_summary["percentage"] = (
    landuse_summary["area_m2"]
    / landuse_summary["total_area"]
) * 100

print(
    landuse_summary[
        [
            "IdSensore",
            "LIVELLO_1_DESCRIZIONE",
            "percentage"
        ]
    ].head()
)

# =====================================================
# FINAL CHECKS
# =====================================================

print(
    "Unique polygons:",
    landuse_summary["IdSensore"].nunique()
)

print(
    "Total rows:",
    landuse_summary.shape[0]
)

# =====================================================
# SAVE OUTPUT
# =====================================================

landuse_summary.to_csv(
    "polygon_landuse_summary.csv",
    index=False
)
print("Polygon land use dataset saved")