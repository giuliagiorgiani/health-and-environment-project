import pandas as pd

# =====================================================
# LOAD POLYGON ENVIRONMENT PANEL
# =====================================================

env = pd.read_csv(
    "FINAL_COMPLETE_master_environment_panel_2022_2026.csv"
)

print(env.head())

print(env.columns)

print(env.shape)

# =====================================================
# LOAD ATS WEIGHTS
# =====================================================

weights = pd.read_csv(
    "temperature_ats_weights.csv"
)

print(weights.head())

print(weights.columns)

print(weights.shape)

# =====================================================
# LOAD ATS HEALTH DATA
# =====================================================

health = pd.read_csv(
    "Health_data_ATS_level.csv"
)
print(health.head())

print(health.columns)

print(health.shape)
print(health.columns)

# =====================================================
# RENAME COLUMNS
# =====================================================

health = health.rename(
    columns={
        "Codice_ATS": "CODICE_ATS",
        "year": "Anno",
        "week": "study_week"
    }
)

print(health.columns)

print(
    health[
        [
            "CODICE_ATS",
            "Anno",
            "study_week"
        ]
    ].head()
)
print(
    health["CODICE_ATS"].nunique()
)

print(
    health["Anno"].unique()
)

print(
    health["study_week"].nunique()
)

# =====================================================
# MERGE ATS HEALTH + POLYGON WEIGHTS
# =====================================================

health_poly = health.merge(
    weights[
        [
            "IdSensore",
            "CODICE_ATS",
            "weight"
        ]
    ],
    on="CODICE_ATS",
    how="left"
)

print(health_poly.shape)

print(health_poly.head())

# =====================================================
# APPLY ATS WEIGHTS
# =====================================================

health_poly["Resp_poly"] = (
    health_poly["tot_Sindromi_Respiratorie"]
    * health_poly["weight"]
)

health_poly["Polmoniti_poly"] = (
    health_poly["tot_Polmoniti"]
    * health_poly["weight"]
)

health_poly["ILI_poly"] = (
    health_poly["tot_ILI"]
    * health_poly["weight"]
)

print(
    health_poly[
        [
            "CODICE_ATS",
            "IdSensore",
            "weight",
            "tot_Sindromi_Respiratorie",
            "Resp_poly"
        ]
    ].head()
)
# =====================================================
# POLYGON HEALTH PANEL
# =====================================================

polygon_health = (
    health_poly.groupby(
        [
            "IdSensore",
            "Anno",
            "study_week"
        ]
    )
    .agg(
        SindromiResp_Tot=("Resp_poly", "sum"),
        Polmoniti_Tot=("Polmoniti_poly", "sum"),
        ILI_Tot=("ILI_poly", "sum")
    )
    .reset_index()
)

print(polygon_health.shape)

print(polygon_health.head())

print(
    polygon_health[
        [
            "IdSensore",
            "Anno",
            "study_week"
        ]
    ]
    .duplicated()
    .sum()
)
print(polygon_health.shape)

print(
    polygon_health[
        ["IdSensore","Anno","study_week"]
    ].duplicated().sum()
)

# =====================================================
# MERGE ENVIRONMENT + HEALTH
# =====================================================

master = env.merge(
    polygon_health,
    on=[
        "IdSensore",
        "Anno",
        "study_week"
    ],
    how="left"
)

print(master.shape)

print(
    master[
        [
            "SindromiResp_Tot",
            "Polmoniti_Tot",
            "ILI_Tot"
        ]
    ]
    .isna()
    .sum()
)


age = pd.read_csv(
    "age_detail_ER_access_RespInsuff_complete.csv"
)

age = age.rename(
    columns={
        "Year": "Anno",
        "Week": "study_week"
    }
)

print(age.columns)

# =====================================================
# LOAD AGE DISTRIBUTION DATA
# =====================================================

age = pd.read_csv(
    "age_detail_ER_access_RespInsuff_complete.csv"
)

print(age.head())

print(age.columns)

print(age.shape)

# =====================================================
# MERGE AGE DATA
# =====================================================
# =====================================================
# RENAME AGE FILE COLUMNS
# =====================================================

age = age.rename(
    columns={
        "Year": "Anno",
        "Week": "study_week"
    }
)

print(age.columns)
master = master.merge(
    age,
    on=[
        "Anno",
        "study_week"
    ],
    how="left"
)

print(master.shape)

print(
    master[
        [
            "SindromiResp_Tot_0-9_%",
            "SindromiResp_Tot_10-19_%",
            "SindromiResp_Tot_20-49_%",
            "SindromiResp_Tot_50-70_%",
            "SindromiResp_Tot_70+_%"
        ]
    ]
    .isna()
    .sum()
)
print(master.columns)

# =====================================================
# CLEAN DUPLICATE COLUMN
# =====================================================

master = master.drop(
    columns=["SindromiResp_Tot_y"]
)

master = master.rename(
    columns={
        "SindromiResp_Tot_x": "SindromiResp_Tot"
    }
)

print(master.columns)
print(master.shape)

print(
    master[
        [
            "SindromiResp_Tot",
            "Polmoniti_Tot",
            "ILI_Tot"
        ]
    ].head()
)

master.to_csv(
    "FINAL_polygon_environment_health_panel_2022_2026.csv",
    index=False
)

print("Final polygon environment-health panel saved")

# =====================================================
# REMOVE GIS / GEOMETRY COLUMNS
# =====================================================

master = master.drop(
    columns=[
        "COD_RIP",
        "COD_REG",
        "DEN_REG",
        "Shape_Leng",
        "Shape_Area",
        "index_righ",
        "geometry",
        "sum%"
    ]
)

print(master.shape)

print(master.columns)

master.to_csv(
    "FINAL_polygon_environment_health_panel_clean.csv",
    index=False
)
print("Clean panel saved")
