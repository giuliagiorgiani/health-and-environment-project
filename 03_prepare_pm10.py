import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

pm10 = pd.read_json(
    "GetStazioniFisse_airqualitystations_PM10.json"
)

print(pm10.head())
print(pm10.columns)
geometry = [
    Point(xy) for xy in zip(
        pm10["longitudine"],
        pm10["latitudine"]
    )
]

pm10_gdf = gpd.GeoDataFrame(
    pm10,
    geometry=geometry,
    crs="EPSG:4326"
)
lombardia = gpd.read_file(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\lombardia.shp"
)

ats = gpd.read_file(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\ATS.shp"
)

lombardia = lombardia.to_crs(pm10_gdf.crs)
ats = ats.to_crs(pm10_gdf.crs)

from shapely.ops import voronoi_diagram

points = pm10_gdf.unary_union

voronoi = voronoi_diagram(points)

voronoi_gdf = gpd.GeoDataFrame(
    geometry=list(voronoi.geoms),
    crs=pm10_gdf.crs
)

voronoi_lombardia = gpd.overlay(
    voronoi_gdf,
    lombardia,
    how="intersection"
)

pm10_points = pm10_gdf[
    ["idSensore", "geometry"]
]

voronoi_pm10 = gpd.sjoin(
    voronoi_lombardia,
    pm10_points,
    how="left",
    predicate="contains"
)

voronoi_ats = gpd.overlay(
    voronoi_pm10,
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
    "pm10_weights.csv",
    index=False
)

voronoi_ats.to_file(
    "pm10_voronoi_ats.shp"
)