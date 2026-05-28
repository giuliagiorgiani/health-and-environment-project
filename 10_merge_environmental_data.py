import pandas as pd
temp_2022 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_temperature_2022.csv"
)

temp_2023 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_temperature_2023.csv"
)

temp_2024 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_temperature_2024.csv"
)

temp_2025 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_temperature_2025.csv"
)

temp_2026 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_temperature_2026.csv"
)

temp_2022["year"] = 2022
temp_2023["year"] = 2023
temp_2024["year"] = 2024
temp_2025["year"] = 2025
temp_2026["year"] = 2026

temperature = pd.concat(
    [
        temp_2022,
        temp_2023,
        temp_2024,
        temp_2025,
        temp_2026
    ],
    ignore_index=True
)
temperature = temperature.rename(
    columns={
        "weighted_mean": "temp_mean",
        "weighted_std": "temp_std"
    }
)
print(temperature.head())

print(temperature.shape)

print(temperature.columns)


pm10_2022 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_pm10_2022.csv"
)

pm10_2023 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_pm10_2023.csv"
)

pm10_2024 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_pm10_2024.csv"
)

pm10_2025 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_pm10_2025.csv"
)

pm10_2026 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_pm10_2026.csv"
)

pm10_2022["year"] = 2022
pm10_2023["year"] = 2023
pm10_2024["year"] = 2024
pm10_2025["year"] = 2025
pm10_2026["year"] = 2026

pm10 = pd.concat(
    [
        pm10_2022,
        pm10_2023,
        pm10_2024,
        pm10_2025,
        pm10_2026
    ],
    ignore_index=True
)
pm10 = pm10.rename(
    columns={
        "weighted_mean": "pm10_mean",
        "weighted_std": "pm10_std"
    }
)
print(pm10.head())

print(pm10.shape)

print(pm10.columns)

# load O3 datasets

o3_2022 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_o3_2022.csv"
)

o3_2023 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_o3_2023.csv"
)

o3_2024 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_o3_2024.csv"
)

o3_2025 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_o3_2025.csv"
)

o3_2026 = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_o3_2026.csv"
)

# add year column

o3_2022["year"] = 2022
o3_2023["year"] = 2023
o3_2024["year"] = 2024
o3_2025["year"] = 2025
o3_2026["year"] = 2026

# combine all years

o3 = pd.concat(
    [
        o3_2022,
        o3_2023,
        o3_2024,
        o3_2025,
        o3_2026
    ],
    ignore_index=True
)
o3 = o3.rename(
    columns={
        "weighted_mean": "o3_mean",
        "weighted_std": "o3_std"
    }
)

print(o3.head())

print(o3.shape)

print(o3.columns)


environmental = temperature.merge(
    pm10,
    on=[
        "CODICE_ATS",
        "DESCRIZION",
        "study_week",
        "year"
    ],
    how="outer"
)

environmental = environmental.merge(
    o3,
    on=[
        "CODICE_ATS",
        "DESCRIZION",
        "study_week",
        "year"
    ],
    how="outer"
)
print(environmental.head())

print(environmental.shape)

print(environmental.columns)

print(
    environmental.isna().sum()
)

environmental.to_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\environmental_panel_2022_2026.csv",
    index=False
)

print("Environmental panel dataset saved")

landuse = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_landuse_summary.csv"
)

print(landuse.head())

print(landuse.shape)

print(landuse.columns)

landuse_wide = landuse.pivot(
    index=[
        "CODICE_ATS",
        "DESCRIZION"
    ],
    columns="LIVELLO_1_DESCRIZIONE",
    values="percentage"
).reset_index()

print(landuse_wide.head())

print(landuse_wide.shape)

print(landuse_wide.columns)

final_dataset = environmental.merge(
    landuse_wide,
    on=[
        "CODICE_ATS",
        "DESCRIZION"
    ],
    how="left"
)

print(final_dataset.head())

print(final_dataset.shape)

print(final_dataset.columns)

print(
    final_dataset.isna().sum()
)

final_dataset.to_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\final_environmental_panel_2022_2026.csv",
    index=False
)

print("Final environmental panel saved")