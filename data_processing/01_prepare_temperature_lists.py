import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
import numpy as np

from shapely.geometry import Point
from shapely.ops import voronoi_diagram
from rasterio.mask import mask

# =====================================================
# LOAD TEMPERATURE STATIONS
# =====================================================

temperature = pd.read_csv(
    "temperature_stations_list.csv"
)

print(temperature.columns)

print(temperature.head())

# =====================================================
# CLEAN COORDINATES
# =====================================================

temperature["UTM Est"] = pd.to_numeric(
    temperature["UTM Est"],
    errors="coerce"
)

temperature["UTM Nord"] = pd.to_numeric(
    temperature["UTM Nord"],
    errors="coerce"
)

temperature = temperature.dropna(
    subset=[
        "UTM Est",
        "UTM Nord"
    ]
)

# =====================================================
# CREATE GEODATAFRAME
# =====================================================

geometry = [
    Point(xy)
    for xy in zip(
        temperature["UTM Est"],
        temperature["UTM Nord"]
    )
]

temperature_gdf = gpd.GeoDataFrame(
    temperature,
    geometry=geometry,
    crs="EPSG:32632"
)

print(temperature_gdf.head())

print(temperature_gdf.crs)

# =====================================================
# LOAD LOMBARDIA BOUNDARY
# =====================================================

lombardia = gpd.read_file(
    "lombardia.shp"
)

print(lombardia.crs)

# =====================================================
# PLOT STATIONS
# =====================================================

ax = lombardia.plot(
    figsize=(8, 8),
    color="white",
    edgecolor="black"
)

temperature_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)

plt.show()

# =====================================================
# CREATE VORONOI
# =====================================================

temperature_gdf = temperature_gdf.dropna(
    subset=["geometry"]
)

temperature_gdf = temperature_gdf.drop_duplicates(
    subset=["geometry"]
)

points = temperature_gdf.unary_union

voronoi = voronoi_diagram(points)

print(voronoi)

# =====================================================
# CONVERT TO GEODATAFRAME
# =====================================================

voronoi_gdf = gpd.GeoDataFrame(
    geometry=list(voronoi.geoms),
    crs=temperature_gdf.crs
)

# =====================================================
# CLIP TO LOMBARDIA
# =====================================================

voronoi_lombardia = gpd.overlay(
    voronoi_gdf,
    lombardia,
    how="intersection"
)

# =====================================================
# PLOT VORONOI
# =====================================================

ax = voronoi_lombardia.plot(
    figsize=(8, 8),
    edgecolor="black",
    facecolor="none"
)

temperature_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)

plt.show()

# =====================================================
# ASSIGN TEMPERATURE STATIONS
# =====================================================

temperature_points = temperature_gdf[
    [
        "IdSensore",
        "geometry"
    ]
]

voronoi_temperature = gpd.sjoin(
    voronoi_lombardia,
    temperature_points,
    how="left",
    predicate="contains"
)

print(voronoi_temperature.head())

print(
    "Unique Voronoi polygons:",
    voronoi_temperature["IdSensore"].nunique()
)

# =====================================================
# SAVE TRUE ENVIRONMENT POLYGONS
# =====================================================

voronoi_temperature.to_file(
    "temperature_voronoi.shp"
)

print("Pure Voronoi polygons saved")

# =====================================================
# LOAD ATS
# =====================================================

ats = gpd.read_file(
    "ATS.shp"
)

print(ats.crs)

# =====================================================
# CREATE ATS INTERSECTION
# ONLY FOR WEIGHTS
# =====================================================

voronoi_ats = gpd.overlay(
    voronoi_temperature,
    ats,
    how="intersection"
)

# =====================================================
# PLOT ATS OVERLAY
# =====================================================

ax = voronoi_ats.plot(
    figsize=(8, 8),
    edgecolor="black",
    facecolor="none"
)

ats.boundary.plot(
    ax=ax,
    color="red"
)

plt.show()

# =====================================================
# LOAD POPULATION RASTER
# =====================================================

pop = rasterio.open(
    "ita_pop_2022_CN_100m_R2025A_v1.tif"
)

print(pop.crs)

print(pop.bounds)

# =====================================================
# MATCH CRS
# =====================================================

voronoi_ats = voronoi_ats.to_crs(
    pop.crs
)

# =====================================================
# CALCULATE POPULATION
# =====================================================

population_list = []

for geom in voronoi_ats.geometry:

    out_image, out_transform = mask(
        pop,
        [geom],
        crop=True
    )

    out_image = out_image.astype("float")

    out_image[out_image < 0] = np.nan

    population = np.nansum(out_image)

    population_list.append(population)

voronoi_ats["population"] = population_list

print(
    voronoi_ats[
        [
            "IdSensore",
            "population"
        ]
    ].head()
)

# =====================================================
# CALCULATE ATS WEIGHTS
# =====================================================

ats_population = (
    voronoi_ats.groupby(
        "CODICE_ATS"
    )["population"]
    .transform("sum")
)

voronoi_ats["weight"] = (
    voronoi_ats["population"]
    / ats_population
)

print(
    voronoi_ats[
        [
            "CODICE_ATS",
            "DESCRIZION",
            "IdSensore",
            "population",
            "weight"
        ]
    ].head()
)

# =====================================================
# CREATE CLEAN WEIGHTS TABLE
# =====================================================

weights_table = voronoi_ats[
    [
        "IdSensore",
        "CODICE_ATS",
        "DESCRIZION",
        "population",
        "weight"
    ]
].copy()

print(weights_table.head())

print(weights_table.shape)

# =====================================================
# SAVE WEIGHTS TABLE
# =====================================================

weights_table.to_csv(
    "temperature_ats_weights.csv",
    index=False
)
print("ATS weights table saved")

print(
    voronoi_temperature.shape
)

print(
    voronoi_temperature["IdSensore"].nunique()
)



# =====================================================
# AGE STRUCTURE
# =====================================================

print(voronoi_temperature.columns)

age_polygons = voronoi_temperature[
    [
        "IdSensore",
        "geometry"
    ]
].copy()

print(age_polygons.head())
print(age_polygons.shape)


# =====================================================
# TOTAL 70+ POPULATION
# =====================================================
folder = "ita_agesex_structures_2022_CN_1km_R2025A_UA_v1"

test_raster = rasterio.open(
    fr"{folder}\ita_t_70_2022_CN_1km_R2025A_UA_v1.tif"
)

print(age_polygons.crs)
print(test_raster.crs)

age_polygons = age_polygons.to_crs(
    test_raster.crs
)
folder = "ita_agesex_structures_2022_CN_1km_R2025A_UA_v1"
elderly_total = np.zeros(len(age_polygons))

for age in ["70", "75", "80", "85", "90"]:

    raster = rasterio.open(
        fr"{folder}\ita_t_{age}_2022_CN_1km_R2025A_UA_v1.tif"
    )

    values = []

    for geom in age_polygons.geometry:

        out_image, out_transform = mask(
            raster,
            [geom],
            crop=True
        )

        out_image = out_image.astype("float")
        out_image[out_image < 0] = np.nan

        values.append(
            np.nansum(out_image)
        )

    elderly_total += np.array(values)

age_polygons["elderly_total_70plus"] = elderly_total

print(
    age_polygons[
        [
            "IdSensore",
            "elderly_total_70plus"
        ]
    ].head()
)

print(
    age_polygons["elderly_total_70plus"].describe()
)

# =====================================================
# FUNCTION TO EXTRACT POPULATION
# =====================================================

def extract_population(polygons, raster_files):

    total = np.zeros(len(polygons))

    for raster_file in raster_files:

        raster = rasterio.open(raster_file)

        values = []

        for geom in polygons.geometry:

            out_image, out_transform = mask(
                raster,
                [geom],
                crop=True
            )

            out_image = out_image.astype("float")

            out_image[out_image < 0] = np.nan

            values.append(
                np.nansum(out_image)
            )

        total += np.array(values)

    return total


# =====================================================
# TOTAL MALE / FEMALE POPULATION (ALL AGES)
# =====================================================

all_male_files = [
    fr"{folder}\ita_m_00_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_01_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_05_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_10_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_15_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_20_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_25_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_30_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_35_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_40_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_45_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_50_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_55_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_60_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_65_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_70_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_75_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_80_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_85_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_90_2022_CN_1km_R2025A_UA_v1.tif",
]

all_female_files = [
    fr"{folder}\ita_f_00_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_01_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_05_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_10_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_15_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_20_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_25_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_30_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_35_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_40_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_45_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_50_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_55_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_60_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_65_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_70_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_75_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_80_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_85_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_90_2022_CN_1km_R2025A_UA_v1.tif",
]

age_polygons["male_total"] = extract_population(
    age_polygons,
    all_male_files
)

age_polygons["female_total"] = extract_population(
    age_polygons,
    all_female_files
)

age_polygons["population_total"] = (
    age_polygons["male_total"]
    + age_polygons["female_total"]
)


folder = "ita_agesex_structures_2022_CN_1km_R2025A_UA_v1"
# 0-9 years
child_total_files = [
    fr"{folder}\ita_t_00_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_01_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_05_2022_CN_1km_R2025A_UA_v1.tif"
]

child_male_files = [
    fr"{folder}\ita_m_00_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_01_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_05_2022_CN_1km_R2025A_UA_v1.tif"
]

child_female_files = [
    fr"{folder}\ita_f_00_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_01_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_05_2022_CN_1km_R2025A_UA_v1.tif"
]

# 70+ years
elderly_total_files = [
    fr"{folder}\ita_t_70_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_75_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_80_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_85_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_90_2022_CN_1km_R2025A_UA_v1.tif"
]

elderly_male_files = [
    fr"{folder}\ita_m_70_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_75_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_80_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_85_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_m_90_2022_CN_1km_R2025A_UA_v1.tif"
]

elderly_female_files = [
    fr"{folder}\ita_f_70_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_75_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_80_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_85_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_f_90_2022_CN_1km_R2025A_UA_v1.tif"
]

age_polygons["child_total_0_9"] = extract_population(age_polygons, child_total_files)
age_polygons["child_male_0_9"] = extract_population(age_polygons, child_male_files)
age_polygons["child_female_0_9"] = extract_population(age_polygons, child_female_files)

age_polygons["elderly_total_70plus"] = extract_population(age_polygons, elderly_total_files)
age_polygons["elderly_male_70plus"] = extract_population(age_polygons, elderly_male_files)
age_polygons["elderly_female_70plus"] = extract_population(age_polygons, elderly_female_files)

age_table = age_polygons[
    [
        "IdSensore",

        "population_total",
        "male_total",
        "female_total",

        "child_total_0_9",
        "child_male_0_9",
        "child_female_0_9",

        "elderly_total_70plus",
        "elderly_male_70plus",
        "elderly_female_70plus"
    ]
]
print(age_table.head())

print(age_table.describe())
print(age_table.isna().sum())
age_table = age_table.dropna(subset=["IdSensore"])

age_table.to_csv(
    "temperature_age_structure.csv",
    index=False
)

print("Age structure table saved")


print(
    temperature_gdf[temperature_gdf["IdSensore"].isna()][
        ["Nome", "Comune", "Provincia"]
    ]
)
print("Rows:", len(age_table))
print("Unique stations:", age_table["IdSensore"].nunique())

total_files = [
    fr"{folder}\ita_t_00_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_01_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_05_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_10_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_15_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_20_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_25_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_30_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_35_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_40_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_45_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_50_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_55_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_60_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_65_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_70_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_75_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_80_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_85_2022_CN_1km_R2025A_UA_v1.tif",
    fr"{folder}\ita_t_90_2022_CN_1km_R2025A_UA_v1.tif",
]
age_polygons["total_from_t"] = extract_population(
    age_polygons,
    total_files
)

print(
    (
        age_polygons["population_total"]
        - age_polygons["total_from_t"]
    ).describe()
)


print(
    voronoi_ats.groupby("IdSensore")["population"]
    .sum()
    .describe()
)
print(voronoi_ats.groupby("IdSensore")["population"].sum().describe())
