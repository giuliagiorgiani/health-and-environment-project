import geopandas as gpd
import pandas as pd
# =====================================================
# FINAL ENVIRONMENTAL PANEL CREATION
# =====================================================
#
# Purpose:
# Create the final polygon-year-week environmental
# exposure panel for 2022–2026.
#
# Inputs:
# - master_environment_polygons.shp
# - polygon_pm10_weights.csv
# - polygon_o3_weights.csv
# - weekly_temperature_station_YYYY.csv
# - weekly_pm10_station_YYYY.csv
# - weekly_o3_station_YYYY.csv
# - polygon_landuse_summary.csv
#
# Outputs:
# - FINAL_COMPLETE_master_environment_panel_2022_2026.csv
#
# Method:
# - Merge temperature exposures directly
# - Apply inverse-distance PM10 weights
# - Apply inverse-distance O3 weights
# - Merge static land-use characteristics
#
# =====================================================
# =====================================================
# LOAD MASTER POLYGONS
# =====================================================

master = gpd.read_file(
    "master_environment_polygons.shp"
)

print(master.head())

print(master.columns)

print(master.shape)

# =====================================================
# LOAD PM10 WEIGHTS
# =====================================================

pm10_weights = pd.read_csv(
    "polygon_pm10_weights.csv"
)

print(pm10_weights.head())

print(pm10_weights.columns)

print(pm10_weights.shape)

# =====================================================
# LOAD O3 WEIGHTS
# =====================================================

o3_weights = pd.read_csv(
    "polygon_o3_weights.csv"
)

print(o3_weights.head())

print(o3_weights.columns)

print(o3_weights.shape)

# =====================================================
# LOAD TEMPERATURE DATA
# =====================================================

temp2022 = pd.read_csv(
    "weekly_temperature_station_2022.csv"
)
temp2023= pd.read_csv(
    "weekly_temperature_station_2023.csv"
)
temp2024 = pd.read_csv(
    "weekly_temperature_station_2024.csv"
)
temp2025 = pd.read_csv(
    "weekly_temperature_station_2025.csv"
)

temp2026 = pd.read_csv(
    "weekly_temperature_station_2026.csv"
)


# =====================================================
# ADD YEAR
# =====================================================

temp2022["Anno"] = 2022
temp2023["Anno"] = 2023
temp2024["Anno"] = 2024
temp2025["Anno"] = 2025
temp2026["Anno"] = 2026

# =====================================================
# COMBINE YEARS
# =====================================================

temp = pd.concat(
    [
        temp2022,
        temp2023,
        temp2024,
        temp2025,
        temp2026
    ],
    ignore_index=True
)

print(temp.shape)

print(
    temp["Anno"]
    .value_counts()
    .sort_index()
)

print(temp.columns)

# =====================================================
# LOAD PM10 DATA
# =====================================================

pm102022 = pd.read_csv(
    "weekly_pm10_station_2022.csv"
)
pm102023 = pd.read_csv(
    "weekly_pm10_station_2023.csv"
)
pm102024 = pd.read_csv(
    "weekly_pm10_station_2024.csv"
)
pm102025 = pd.read_csv(
    "weekly_pm10_station_2025.csv"
)


pm102026 = pd.read_csv(
    "weekly_pm10_station_2026.csv"
)


# =====================================================
# ADD YEAR
# =====================================================

pm102022["Anno"] = 2022
pm102023["Anno"] = 2023
pm102024["Anno"] = 2024
pm102025["Anno"] = 2025
pm102026["Anno"] = 2026

# =====================================================
# COMBINE YEARS
# =====================================================

pm10 = pd.concat(
    [
        pm102022,
        pm102023,
        pm102024,
        pm102025,
        pm102026
    ],
    ignore_index=True
)

print(pm10.shape)

print(
    pm10["Anno"]
    .value_counts()
    .sort_index()
)

print(pm10.columns)

# =====================================================
# LOAD O3 DATA
# =====================================================

o32022 = pd.read_csv(
    "weekly_o3_station_2022.csv"
)

o32023 = pd.read_csv(
    "weekly_o3_station_2023.csv"
)
o32024 = pd.read_csv(
    "weekly_o3_station_2024.csv"
)

o32025 = pd.read_csv(
    "weekly_o3_station_2025.csv"
)
o32026 = pd.read_csv(
    "weekly_o3_station_2026.csv"
)
# =====================================================
# ADD YEAR
# =====================================================

o32022["Anno"] = 2022
o32023["Anno"] = 2023
o32024["Anno"] = 2024
o32025["Anno"] = 2025
o32026["Anno"] = 2026

# =====================================================
# COMBINE YEARS
# =====================================================

o3 = pd.concat(
    [
        o32022,
        o32023,
        o32024,
        o32025,
        o32026
    ],
    ignore_index=True
)

print(o3.shape)

print(
    o3["Anno"]
    .value_counts()
    .sort_index()
)

print(o3.columns)

# =====================================================
# CREATE YEAR TABLE
# =====================================================

years = pd.DataFrame({
    "Anno": [2022, 2023, 2024, 2025, 2026]
})

# =====================================================
# CREATE WEEK TABLE
# =====================================================

weeks = pd.DataFrame({
    "study_week": range(1, 22)
})

# =====================================================
# CREATE POLYGON-YEAR-WEEK PANEL
# =====================================================

master_panel = (
    master.assign(key=1)
    .merge(
        years.assign(key=1),
        on="key"
    )
    .merge(
        weeks.assign(key=1),
        on="key"
    )
    .drop("key", axis=1)
)

print(master_panel.shape)

print(master_panel["IdSensore"].nunique())

print(master_panel["Anno"].nunique())

print(master_panel["study_week"].nunique())

# =====================================================
# MERGE TEMPERATURE
# =====================================================

master_panel = master_panel.merge(
    temp,
    left_on=[
        "IdSensore",
        "Anno",
        "study_week"
    ],
    right_on=[
        "idsensore",
        "Anno",
        "study_week"
    ],
    how="left"
)

print(master_panel.shape)

print(
    master_panel[
        [
            "IdSensore",
            "Anno",
            "study_week",
            "weekly_mean"
        ]
    ].head()
)

print(
    master_panel["weekly_mean"]
    .isna()
    .sum()
)
# =====================================================
# MERGE PM10 STATION DATA
# =====================================================

pm10_panel = pm10_weights.merge(
    pm10,
    left_on="pm10_station",
    right_on="idsensore",
    how="left"
)

print(pm10_panel.shape)

print(pm10_panel.head())

print(pm10_panel.columns)

# =====================================================
# APPLY PM10 WEIGHTS
# =====================================================

pm10_variables = [
    "weekly_mean",
    "weekly_std",
    "weekly_max",
    "weekly_min",
    "pm10_exceed"
]

for var in pm10_variables:

    pm10_panel[var] = (
        pm10_panel[var]
        * pm10_panel["weight_pm10"]
    )

print(
    pm10_panel[
        [
            "IdSensore",
            "Anno",
            "study_week",
            "weekly_mean",
            "weight_pm10"
        ]
    ].head()
)

# =====================================================
# AGGREGATE PM10 TO POLYGON-YEAR-WEEK
# =====================================================

pm10_polygon = (
    pm10_panel.groupby(
        [
            "IdSensore",
            "Anno",
            "study_week"
        ]
    )[pm10_variables]
    .sum()
    .reset_index()
)

pm10_polygon = pm10_polygon.rename(
    columns={
        "weekly_mean": "pm10_mean",
        "weekly_std": "pm10_std",
        "weekly_max": "pm10_max",
        "weekly_min": "pm10_min",
        "pm10_exceed": "pm10_exceed_days"
    }
)

print(pm10_polygon.shape)

print(pm10_polygon.head())


# =====================================================
# MERGE PM10 INTO MASTER PANEL
# =====================================================

master_panel = master_panel.merge(
    pm10_polygon,
    on=[
        "IdSensore",
        "Anno",
        "study_week"
    ],
    how="left"
)

print(master_panel.shape)

print(
    master_panel[
        [
            "IdSensore",
            "Anno",
            "study_week",
            "pm10_mean"
        ]
    ].head()
)

print(
    master_panel["pm10_mean"]
    .isna()
    .sum()
)

# =====================================================
# MERGE O3 STATION DATA
# =====================================================

o3_panel = o3_weights.merge(
    o3,
    left_on="o3_station",
    right_on="idsensore",
    how="left"
)

print(o3_panel.shape)

print(o3_panel.head())

# =====================================================
# APPLY O3 WEIGHTS
# =====================================================

o3_variables = [
    "weekly_mean",
    "weekly_std",
    "weekly_max_8h",
    "weekly_min",
    "o3_exceed_days"
]

for var in o3_variables:

    o3_panel[var] = (
        o3_panel[var]
        * o3_panel["weight_o3"]
    )

# =====================================================
    # AGGREGATE O3 TO POLYGON-YEAR-WEEK
    # =====================================================

o3_polygon = (
    o3_panel.groupby(
        [
            "IdSensore",
            "Anno",
            "study_week"
        ]
    )[o3_variables]
    .sum()
    .reset_index()
)

o3_polygon = o3_polygon.rename(
    columns={
        "weekly_mean": "o3_mean",
        "weekly_std": "o3_std",
        "weekly_max_8h": "o3_max_8h",
        "weekly_min": "o3_min",
        "o3_exceed_days": "o3_exceed_days"
    }
)

print(o3_polygon.shape)

master_panel = master_panel.merge(
    o3_polygon,
    on=[
        "IdSensore",
        "Anno",
        "study_week"
    ],
    how="left"
)

print(master_panel.shape)

print(
    master_panel["o3_mean"]
    .isna()
    .sum()
)

print(master_panel.columns)

print(
    master_panel[
        [
            "IdSensore",
            "Anno",
            "study_week"
        ]
    ]
    .duplicated()
    .sum()
)

# =====================================================
# LOAD LAND USE
# =====================================================

landuse = pd.read_csv(
   "polygon_landuse_summary.csv"
)

print(landuse.head())

# =====================================================
# PIVOT TO WIDE FORMAT
# =====================================================

landuse_wide = (
    landuse.pivot_table(
        index="IdSensore",
        columns="LIVELLO_1_DESCRIZIONE",
        values="percentage",
        aggfunc="sum"
    )
    .reset_index()
)


# =====================================================
# RENAME COLUMNS
# =====================================================

landuse_wide = landuse_wide.rename(
    columns={
        "Aree agricole": "agriculture_pct",
        "Aree antropizzate": "urban_pct",
        "Aree umide": "wetland_pct",
        "Corpi idrici": "water_pct",
        "Territori boscati e ambienti seminaturali": "forest_pct"
    }
)

# =====================================================
# REPLACE MISSING LAND-USE CATEGORIES WITH 0
# =====================================================

landuse_wide = landuse_wide.fillna(0)

print(landuse_wide.head())

print(landuse_wide.columns)

print(landuse_wide.shape)

# =====================================================
# MERGE LAND USE
# =====================================================

master_panel = master_panel.merge(
    landuse_wide,
    on="IdSensore",
    how="left"
)

print(master_panel.shape)

print(
    master_panel[
        [
            "IdSensore",
            "agriculture_pct",
            "urban_pct",
            "forest_pct",
            "wetland_pct",
            "water_pct"
        ]
    ].head()
)

# =====================================================
# FINAL CHECKS
# =====================================================

print(
    master_panel[
        [
            "IdSensore",
            "Anno",
            "study_week"
        ]
    ]
    .duplicated()
    .sum()
)

print(
    master_panel[
        [
            "agriculture_pct",
            "urban_pct",
            "forest_pct",
            "wetland_pct",
            "water_pct"
        ]
    ]
    .isna()
    .sum()
)

# =====================================================
# CLEANUP
# =====================================================

master_panel = master_panel.drop(
    columns=["idsensore"],
    errors="ignore"
)

# =====================================================
# SAVE MASTER ENVIRONMENT PANEL
# =====================================================

master_panel.to_csv(
    "master_environment_panel_2022_2026.csv",
    index=False
)

print("Master environmental panel saved")
print(master_panel.shape)

print(
    master_panel[
        ["IdSensore", "Anno", "study_week"]
    ].duplicated().sum()
)

print(master_panel.isna().sum())

print(
    master_panel.groupby("Anno")["weekly_mean"]
    .apply(lambda x: x.isna().sum())
)
