import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import Point
from sklearn.neighbors import NearestNeighbors

# =====================================================
# LOAD TRUE VORONOI POLYGONS
# =====================================================

temp_voronoi = gpd.read_file(
    "temperature_voronoi.shp"
)

print(temp_voronoi.head())

print(temp_voronoi.columns)

print(temp_voronoi.crs)

print(temp_voronoi.shape)

print(
    "Unique polygons:",
    temp_voronoi["IdSensore"].nunique()
)

# =====================================================
# REMOVE EMPTY / DUPLICATE POLYGONS
# =====================================================

temp_voronoi = temp_voronoi.dropna(
    subset=["IdSensore"]
)

temp_voronoi = temp_voronoi.drop_duplicates(
    subset=["IdSensore"]
)

print("After cleaning:")

print(temp_voronoi.shape)

print(
    "Unique polygons:",
    temp_voronoi["IdSensore"].nunique()
)

# =====================================================
# PROJECT TO METRIC CRS
# =====================================================

temp_voronoi = temp_voronoi.to_crs(
    "EPSG:32632"
)

# =====================================================
# CREATE CENTROIDS
# =====================================================

temp_voronoi["centroid"] = (
    temp_voronoi.geometry.centroid
)

temp_centroids = temp_voronoi.copy()

temp_centroids = temp_centroids.set_geometry(
    "centroid"
)

print(temp_centroids.head())

# =====================================================
# LOAD PM10 STATIONS
# =====================================================

pm10 = pd.read_json(
    "GetStazioniFisse_airqualitystations_PM10.json"
)

print(pm10.head())

print(pm10.columns)

print(pm10.shape)

# =====================================================
# CREATE PM10 GEODATAFRAME
# =====================================================

pm10_geometry = [
    Point(xy)
    for xy in zip(
        pm10["longitudine"],
        pm10["latitudine"]
    )
]

pm10_gdf = gpd.GeoDataFrame(
    pm10,
    geometry=pm10_geometry,
    crs="EPSG:4326"
)

# =====================================================
# PROJECT PM10 TO METRIC CRS
# =====================================================

pm10_gdf = pm10_gdf.to_crs(
    "EPSG:32632"
)

print(pm10_gdf.head())

print(pm10_gdf.shape)

# =====================================================
# LOAD O3 STATIONS
# =====================================================

o3 = pd.read_json(
    "GetStazioniFisse_airqualitystations_O3.json"
)
print(o3.head())

print(o3.columns)

print(o3.shape)

# =====================================================
# CREATE O3 GEODATAFRAME
# =====================================================

o3_geometry = [
    Point(xy)
    for xy in zip(
        o3["longitudine"],
        o3["latitudine"]
    )
]

o3_gdf = gpd.GeoDataFrame(
    o3,
    geometry=o3_geometry,
    crs="EPSG:4326"
)

# =====================================================
# PROJECT O3 TO METRIC CRS
# =====================================================

o3_gdf = o3_gdf.to_crs(
    "EPSG:32632"
)

print(o3_gdf.head())

print(o3_gdf.shape)

# =====================================================
# CREATE POLYGON COORDINATES
# =====================================================

polygon_coords = np.array(
    [
        (
            geom.x,
            geom.y
        )
        for geom in temp_centroids.geometry
    ]
)

# =====================================================
# PM10 STATION COORDINATES
# =====================================================

pm10_coords = np.array(
    [
        (
            geom.x,
            geom.y
        )
        for geom in pm10_gdf.geometry
    ]
)

# =====================================================
# FIND 3 NEAREST PM10 STATIONS
# =====================================================

pm10_nn = NearestNeighbors(
    n_neighbors=3
)

pm10_nn.fit(pm10_coords)

pm10_distances, pm10_indices = (
    pm10_nn.kneighbors(polygon_coords)
)

# =====================================================
# BUILD PM10 WEIGHTS TABLE
# =====================================================

pm10_rows = []

for i, polygon_id in enumerate(temp_centroids["IdSensore"]):

    for j in range(3):

        station_index = pm10_indices[i][j]

        station_id = (
            pm10_gdf.iloc[station_index]["idSensore"]
        )

        distance = pm10_distances[i][j]

        pm10_rows.append(
            {
                "IdSensore": polygon_id,
                "pm10_station": station_id,
                "distance_pm10": distance
            }
        )

pm10_matches = pd.DataFrame(pm10_rows)

# =====================================================
# CALCULATE PM10 WEIGHTS
# =====================================================

pm10_matches["weight_pm10"] = (
    1 / pm10_matches["distance_pm10"]
)

pm10_matches["weight_pm10"] = (
    pm10_matches["weight_pm10"]
    /
    pm10_matches.groupby("IdSensore")["weight_pm10"]
    .transform("sum")
)

print(pm10_matches.head(10))

print(pm10_matches.shape)

# =====================================================
# O3 STATION COORDINATES
# =====================================================

o3_coords = np.array(
    [
        (
            geom.x,
            geom.y
        )
        for geom in o3_gdf.geometry
    ]
)

# =====================================================
# FIND 3 NEAREST O3 STATIONS
# =====================================================

o3_nn = NearestNeighbors(
    n_neighbors=3
)

o3_nn.fit(o3_coords)

o3_distances, o3_indices = (
    o3_nn.kneighbors(polygon_coords)
)

# =====================================================
# BUILD O3 WEIGHTS TABLE
# =====================================================

o3_rows = []

for i, polygon_id in enumerate(temp_centroids["IdSensore"]):

    for j in range(3):

        station_index = o3_indices[i][j]

        station_id = (
            o3_gdf.iloc[station_index]["idSensore"]
        )

        distance = o3_distances[i][j]

        o3_rows.append(
            {
                "IdSensore": polygon_id,
                "o3_station": station_id,
                "distance_o3": distance
            }
        )

o3_matches = pd.DataFrame(o3_rows)

# =====================================================
# CALCULATE O3 WEIGHTS
# =====================================================

o3_matches["weight_o3"] = (
    1 / o3_matches["distance_o3"]
)

o3_matches["weight_o3"] = (
    o3_matches["weight_o3"]
    /
    o3_matches.groupby("IdSensore")["weight_o3"]
    .transform("sum")
)

print(o3_matches.head(10))

print(o3_matches.shape)

# =====================================================
# FINAL STATION CHECKS
# =====================================================

print(
    "Total PM10 stations available:",
    pm10_gdf["idSensore"].nunique()
)

print(
    "PM10 stations assigned:",
    pm10_matches["pm10_station"].nunique()
)

print(
    "Total O3 stations available:",
    o3_gdf["idSensore"].nunique()
)

print(
    "O3 stations assigned:",
    o3_matches["o3_station"].nunique()
)

print(
    "Unique polygons:",
    temp_voronoi["IdSensore"].nunique()
)

print(
    "PM10 weight rows:",
    pm10_matches.shape
)

print(
    "O3 weight rows:",
    o3_matches.shape
)

# =====================================================
# REMOVE CENTROID GEOMETRY
# =====================================================

temp_voronoi = temp_voronoi.drop(
    columns="centroid"
)

temp_voronoi = temp_voronoi.set_geometry(
    "geometry"
)

# =====================================================
# SAVE OUTPUTS
# =====================================================

pm10_matches.to_csv(
    r"...\polygon_pm10_weights.csv",
    index=False
)

o3_matches.to_csv(
    "polygon_o3_weights.csv",
    index=False
)

temp_voronoi.to_file(
    "master_environment_polygons.shp"
)

temp_voronoi.to_csv(
    "master_environment_polygons.csv",
    index=False
)

print("Master environmental polygons saved")

print("PM10 weights table saved")

print("O3 weights table saved")
