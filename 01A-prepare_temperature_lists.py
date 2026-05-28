import pandas as pd
import geopandas as gpd

temperature = pd.read_csv("temperature_stations_list.csv")

print(temperature.columns)
print(temperature.head())

from shapely.geometry import Point
temperature["UTM Est"] = pd.to_numeric(
    temperature["UTM Est"],
    errors="coerce"
)

temperature["UTM Nord"] = pd.to_numeric(
    temperature["UTM Nord"],
    errors="coerce"
)

temperature = temperature.dropna(
    subset=["UTM Est", "UTM Nord"]
)

geometry = [
    Point(xy) for xy in zip(
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

lombardia = gpd.read_file(r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\lombardia.shp")
print(lombardia.crs)

ax = lombardia.plot(figsize=(8,8), color="white", edgecolor="black")

temperature_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)
import matplotlib.pyplot as plt
plt.show()

from shapely.ops import voronoi_diagram
temperature_gdf = temperature_gdf.dropna(
    subset=["geometry"]
)

temperature_gdf = temperature_gdf.drop_duplicates(
    subset=["geometry"]
)
points = temperature_gdf.unary_union
voronoi = voronoi_diagram(points)
print(voronoi)
voronoi_gdf = gpd.GeoDataFrame(
    geometry=list(voronoi.geoms),
    crs=temperature_gdf.crs
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

temperature_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)

plt.show()

temperature_points = temperature_gdf[["IdSensore", "geometry"]]
voronoi_temperature = gpd.sjoin(
    voronoi_lombardia,
    temperature_points,
    how="left",
    predicate="contains"
)
print(voronoi_temperature.head())

ats = gpd.read_file( r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ATS.shp" )
print(ats.crs)

voronoi_ats = gpd.overlay(
    voronoi_temperature,
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
    "temperature_weights.csv",
    index=False
)
voronoi_ats.to_file(
    "temperature_voronoi_ats.shp"
)