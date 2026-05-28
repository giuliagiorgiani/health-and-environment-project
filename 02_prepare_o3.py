import pandas as pd

o3 = pd.read_json("GetStazioniFisse_airqualitystations_O3.json")

print(o3.head())
print(o3.columns)

import geopandas as gpd
from shapely.geometry import Point

geometry = [
    Point(xy) for xy in zip(o3["longitudine"], o3["latitudine"])
]

o3_gdf = gpd.GeoDataFrame(
    o3,
    geometry=geometry,
    crs="EPSG:4326"
)
lombardia = gpd.read_file(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\lombardia.shp"
)

lombardia = lombardia.to_crs(o3_gdf.crs)

import matplotlib.pyplot as plt

ax = lombardia.plot(
    figsize=(8,8),
    color="white",
    edgecolor="black"
)

o3_gdf.plot(
    ax=ax,
    color="red",
    markersize=10
)

plt.show()

from shapely.ops import voronoi_diagram

points = o3_gdf.unary_union

voronoi = voronoi_diagram(points)

voronoi_gdf = gpd.GeoDataFrame(
    geometry=list(voronoi.geoms),
    crs=o3_gdf.crs
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

o3_gdf.plot(
    ax=ax,
    color="red",
    markersize=10
)

plt.show()

o3_points = o3_gdf[["idSensore", "geometry"]]

voronoi_o3 = gpd.sjoin(
    voronoi_lombardia,
    o3_points,
    how="left",
    predicate="contains"
)

ats = gpd.read_file(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ATS.shp"
)

ats = ats.to_crs(o3_gdf.crs)

voronoi_ats = gpd.overlay(
    voronoi_o3,
    ats,
    how="intersection"
)
import rasterio
from rasterio.mask import mask
import numpy as np

pop = rasterio.open(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ita_pop_2022_CN_100m_R2025A_v1.tif"
)
voronoi_ats = voronoi_ats.to_crs(pop.crs)

lombardia_pop = lombardia.to_crs(pop.crs)

pop_clip, pop_transform = mask(
    pop,
    lombardia_pop.geometry,
    crop=True
)

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
            "idSensore",
            "population",
            "weight"
        ]
    ].head()
)

voronoi_ats.to_csv(
    "o3_weights.csv",
    index=False
)

voronoi_ats.to_file(
    "o3_voronoi_ats.shp"
)