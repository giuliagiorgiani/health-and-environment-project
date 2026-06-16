import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
# =====================================================
# SPATIAL VISUALIZATION OF ENVIRONMENTAL AND HEALTH
# VARIABLES
# =====================================================
#
# Purpose:
# Create choropleth maps of average environmental,
# demographic, and respiratory health indicators.
#
# Inputs:
# - polygon_temp_ats.shp
# - ATS.shp
# - model_dataset_with_8223.csv
#
# Outputs:
# - Respiratory_Rate_Map.png
# - Respiratory_Cases_Map.png
# - PM10_Map.png
# - O3_Map.png
# - Temperature_Map.png
# - Female_Map.png
# - Elderly_Map.png
# - Child_Map.png
#
# Method:
# - Average values by polygon
# - Create quintile-based classes
# - Overlay ATS boundaries
#
# =====================================================
# =====================================================

# LOAD DATA

# =====================================================

gdf = gpd.read_file("polygon_temp_ats.shp")
ats = gpd.read_file("ATS.shp")

df = pd.read_csv("model_dataset.csv")

print("Voronoi CRS:", gdf.crs)
print("ATS CRS:", ats.crs)

# =====================================================

# AVERAGE VALUES BY POLYGON

# =====================================================

avg_data = (
df.groupby("IdSensore")
[
[
"SindromiResp_Tot",
"population",
"pm10_mean",
"o3_mean",
"weekly_mean",
"female_pct",
"elderly_pct",
"child_pct"
]
]
.mean()
.reset_index()
)
avg_data["female_pct"] *= 100
avg_data["elderly_pct"] *= 100
avg_data["child_pct"] *= 100
# Respiratory rate per 1000 population

avg_data["resp_rate"] = (
avg_data["SindromiResp_Tot"]
/ avg_data["population"]
* 1000
)

# =====================================================

# JOIN

# =====================================================

gdf["IdSensore"] = pd.to_numeric(
gdf["IdSensore"],
errors="coerce"
)

avg_data["IdSensore"] = pd.to_numeric(
avg_data["IdSensore"],
errors="coerce"
)

map_data = gdf.merge(
avg_data,
on="IdSensore",
how="left"
)

print(
"Matched polygons:",
map_data["resp_rate"].notna().sum()
)

def draw_map(variable, title, cmap, output_file):

    fig, ax = plt.subplots(
        figsize=(11, 11),
        facecolor="white"
    )

    # ==========================================
    # QUANTILE CLASSES WITH CLEAN LABELS
    # ==========================================

    temp = map_data.copy()

    _, bins = pd.qcut(
        temp[variable],
        q=5,
        retbins=True,
        duplicates="drop"
    )

    labels = []

    for i in range(len(bins) - 1):

        if "pct" in variable:

            lower = round(bins[i], 1)
            upper = round(bins[i + 1], 1)

            labels.append(f"{lower}%–{upper}%")

        else:

            lower = int(round(bins[i]))
            upper = int(round(bins[i + 1]))

            labels.append(f"{lower}–{upper}")
    temp["Class"] = pd.cut(
        temp[variable],
        bins=bins,
        labels=labels,
        include_lowest=True,
        ordered=False
    )
    temp.plot(
        column="Class",
        categorical=True,
        cmap=cmap,
        legend=True,
        linewidth=0.03,
        edgecolor="white",
        ax=ax
    )

    ats.boundary.plot(
        ax=ax,
        color="black",
        linewidth=1.2,
        zorder=10
    )

    ax.set_title(
        title,
        fontsize=20,
        fontweight="bold",
        pad=20
    )

    ax.set_axis_off()

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=600,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()

# =====================================================

# RESPIRATORY RATE

# =====================================================

draw_map(
    "resp_rate",
    "Average Respiratory Syndrome Rate per 1,000 Population",
    "Reds",
    "Respiratory_Rate_Map.png"
)

draw_map(
    "SindromiResp_Tot",
    "Average Respiratory Syndrome Cases",
    "Reds",
    "Respiratory_Cases_Map.png"
)
# =====================================================

# PM10

# =====================================================

draw_map(
    "pm10_mean",
    "Average PM10 Concentration (µg/m³)",
    "Oranges",
    "PM10_Map.png"
)

# =====================================================

# OZONE

# =====================================================

draw_map(
    "o3_mean",
    "Average Ozone Concentration (µg/m³)",
    "Purples",
    "O3_Map.png"
)

# =====================================================

# TEMPERATURE

# =====================================================

draw_map(
    "weekly_mean",
    "Average Temperature  (°C)",
    "YlOrRd",
    "Temperature_Map.png"
)

# =====================================================

# FEMALE SHARE

# =====================================================

draw_map(
    "female_pct",
    "Average Female Population Share",
    "Blues",
    "Female_Map.png"
)

# =====================================================

# ELDERLY SHARE

# =====================================================

draw_map(
    "elderly_pct",
    "Average Elderly Population Share",
    "Greens",
    "Elderly_Map.png"
)

# =====================================================

# CHILD SHARE

# =====================================================

draw_map(
    "child_pct",
    "Average Child Population Share",
    "BuGn",
    "Child_Map.png"
)

print("All maps saved.")
