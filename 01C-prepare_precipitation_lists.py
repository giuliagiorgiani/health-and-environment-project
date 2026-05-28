import pandas as pd
import geopandas as gpd

precipitation = pd.read_csv("precipitation_stations_list.csv")

print(precipitation.columns)
print(precipitation.head())

from shapely.geometry import Point
precipitation["UTM Est"] = pd.to_numeric(
    precipitation["UTM Est"],
    errors="coerce"
)

precipitation["UTM Nord"] = pd.to_numeric(
    precipitation["UTM Nord"],
    errors="coerce"
)

precipitation = precipitation.dropna(
    subset=["UTM Est", "UTM Nord"]
)

geometry = [
    Point(xy) for xy in zip(
        precipitation["UTM Est"],
        precipitation["UTM Nord"]
    )
]

precipitation_gdf = gpd.GeoDataFrame(
    precipitation,
    geometry=geometry,
    crs="EPSG:32632"
)

print(precipitation_gdf.head())
print(precipitation_gdf.crs)

lombardia = gpd.read_file(r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\lombardia.shp")
print(lombardia.crs)

ax = lombardia.plot(figsize=(8,8), color="white", edgecolor="black")

precipitation_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)
import matplotlib.pyplot as plt
plt.show()

from shapely.ops import voronoi_diagram
precipitation_gdf = precipitation_gdf.dropna(
    subset=["geometry"]
)

precipitation_gdf = precipitation_gdf.drop_duplicates(
    subset=["geometry"]
)
points = precipitation_gdf.unary_union
voronoi = voronoi_diagram(points)
print(voronoi)
voronoi_gdf = gpd.GeoDataFrame(
    geometry=list(voronoi.geoms),
    crs=precipitation_gdf.crs
)
voronoi_lombardia = gpd.overlay(
    voronoi_gdf,
    lombardia,
    how="intersection"
)

ax = voronoi_lombardia.plot(
    figsize=(8,8),
    edgecolor="black",
    facecolor="none"
)

precipitation_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)

plt.show()

precipitation_points = precipitation_gdf[["IdSensore", "geometry"]]
voronoi_precipitation = gpd.sjoin(
    voronoi_lombardia,
    precipitation_points,
    how="left",
    predicate="contains"
)
print(voronoi_precipitation.head())

ats = gpd.read_file( r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ATS.shp" )
print(ats.crs)

voronoi_ats = gpd.overlay(
    voronoi_precipitation,
    ats,
    how="intersection"
)
ax = voronoi_ats.plot(
    figsize=(8,8),
    edgecolor="black",
    facecolor="none"
)

ats.boundary.plot(ax=ax, color="red")

plt.show()

import rasterio

pop = rasterio.open(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ita_pop_2022_CN_100m_R2025A_v1.tif"
)

print(pop.crs)
print(pop.bounds)
voronoi_ats = voronoi_ats.to_crs(pop.crs)

from rasterio.mask import mask
lombardia = lombardia.to_crs(pop.crs)

from rasterio.mask import mask
import numpy as np

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
print(voronoi_ats[["IdSensore", "population"]].head())

print(voronoi_ats.columns)

ats_population = voronoi_ats.groupby(
    "CODICE_ATS"
)["population"].transform("sum")

voronoi_ats["weight"] = (
    voronoi_ats["population"] / ats_population
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

voronoi_ats.to_csv(
    "precipitation_weights.csv",
    index=False
)
voronoi_ats.to_file(
    "precipitation_voronoi_ats.shp"
)