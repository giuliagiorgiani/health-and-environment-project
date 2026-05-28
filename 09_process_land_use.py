import geopandas as gpd
import pandas as pd

# load DUSAF land use
dusaf = gpd.read_file(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\land_use\dusaf6.shp"
)

# load ATS boundaries
ats = gpd.read_file(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ATS.shp"
)

print(dusaf.head())

print(dusaf.columns)

print(dusaf.crs)

# load lookup table
lut = pd.read_excel(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\land_use\dusaf6_lut.xls"
)

print(lut.head())

print(lut.columns)

# make same datatype for merge
dusaf["LIV_1"] = dusaf["LIV_1"].astype(int)

# merge labels
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

# make sure CRS matches
print(ats.crs)

ats = ats.to_crs(dusaf.crs)

print(ats.crs)

# dissolve by land-use category
dusaf_simple = (
    dusaf.dissolve(
        by="LIVELLO_1_DESCRIZIONE"
    )
    .reset_index()
)

print(dusaf_simple.head())

print(dusaf_simple.shape)

# overlay with ATS
dusaf_ats = gpd.overlay(
    dusaf_simple,
    ats,
    how="intersection"
)

print(dusaf_ats.head())

print(dusaf_ats.shape)

# calculate area
dusaf_ats["area_m2"] = (
    dusaf_ats.geometry.area
)

print(
    dusaf_ats[
        [
            "LIVELLO_1_DESCRIZIONE",
            "CODICE_ATS",
            "area_m2"
        ]
    ].head()
)

# summarize area by ATS and land use
landuse_summary = (
    dusaf_ats.groupby(
        [
            "CODICE_ATS",
            "DESCRIZION",
            "LIVELLO_1_DESCRIZIONE"
        ]
    )["area_m2"]
    .sum()
    .reset_index()
)

print(landuse_summary.head())

print(landuse_summary.shape)

# total ATS area
ats_total = (
    landuse_summary.groupby(
        "CODICE_ATS"
    )["area_m2"]
    .sum()
    .reset_index(name="total_area")
)

# merge totals
landuse_summary = landuse_summary.merge(
    ats_total,
    on="CODICE_ATS",
    how="left"
)

# compute percentage
landuse_summary["percentage"] = (
    landuse_summary["area_m2"]
    / landuse_summary["total_area"]
) * 100

print(
    landuse_summary[
        [
            "CODICE_ATS",
            "LIVELLO_1_DESCRIZIONE",
            "percentage"
        ]
    ].head()
)

# save output
landuse_summary.to_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_landuse_summary.csv",
    index=False
)

print("ATS land use dataset saved")