import pandas as pd
import geopandas as gpd

weather = pd.read_csv("Weather_stations_list.csv")

print(weather.columns)
print(weather.head())

from shapely.geometry import Point
geometry = [
    Point(xy) for xy in zip(weather["UTM Est"], weather["UTM Nord"])
]

weather_gdf = gpd.GeoDataFrame(
    weather,
    geometry=geometry,
    crs="EPSG:32632"
)

print(weather_gdf.head())
print(weather_gdf.crs)

lombardia = gpd.read_file(r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\lombardia.shp")
print(lombardia.crs)

ax = lombardia.plot(figsize=(8,8), color="white", edgecolor="black")

weather_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)
import matplotlib.pyplot as plt
plt.show()

from shapely.ops import voronoi_diagram
points = weather_gdf.unary_union
voronoi = voronoi_diagram(points)
print(voronoi)
voronoi_gdf = gpd.GeoDataFrame(
    geometry=list(voronoi.geoms),
    crs=weather_gdf.crs
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

weather_gdf.plot(
    ax=ax,
    color="red",
    markersize=5
)

plt.show()

weather_points = weather_gdf[["IdSensore", "geometry"]]
voronoi_weather = gpd.sjoin(
    voronoi_lombardia,
    weather_points,
    how="left",
    predicate="contains"
)
print(voronoi_weather.head())

ats = gpd.read_file( r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ATS.shp" )
print(ats.crs)

voronoi_ats = gpd.overlay(
    voronoi_weather,
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

print(voronoi_ats.columns

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
    "weather_weights.csv",
    index=False
)
voronoi_ats.to_file(
    "weather_voronoi_ats.shp"
)