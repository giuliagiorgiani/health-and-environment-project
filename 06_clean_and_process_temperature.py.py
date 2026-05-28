import pandas as pd

df = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\temperature_2026.csv"
)

print(df.head())
print(df.dtypes)
print(df.shape)

df["data"] = pd.to_datetime(df["data"])

print(df.dtypes)

print(df["data"].min())
print(df["data"].max())

print(df.isna().sum())
print(df["stato"].unique())
df = df[df["stato"] == "VA"]


# remove unrealistic temperatures
df = df[
    (df["valore"] >= -25) &
    (df["valore"] <= 50)
]

print(df.shape)


df = df.sort_values(
    by=["idsensore", "data"]
)

print(df.head())

print(df["valore"].describe())

# create study week variable

start_date = pd.Timestamp("2026-01-12")

df["study_week"] = (
    ((df["data"] - start_date).dt.days // 7) + 3
)

df = df[df["study_week"] <= 16]
print(df[["data", "study_week"]].head(20))

weekly_temp = (
    df.groupby(["idsensore", "study_week"])["valore"]
    .agg(
        weekly_mean="mean",
        weekly_std="std"
    )
    .reset_index()
)

print(weekly_temp.head())
print(weekly_temp.shape)

weights = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\PYTHON\temperature_weights.csv"
)

print(weights.head())
print(weights.columns)

weekly_temp = weekly_temp.rename(
    columns={"idsensore": "IdSensore"}
)

merged = weekly_temp.merge(
    weights,
    on="IdSensore",
    how="left"
)

print(merged.head())
print(merged.shape)


merged["weighted_mean"] = (
    merged["weekly_mean"] * merged["weight"]
)

merged["weighted_std"] = (
    merged["weekly_std"] * merged["weight"]
)

ats_weekly_temp = (
    merged.groupby(
        ["CODICE_ATS", "DESCRIZION", "study_week"]
    )[["weighted_mean", "weighted_std"]]
    .sum()
    .reset_index()
)

print(ats_weekly_temp.head())
print(ats_weekly_temp.shape)

ats_weekly_temp.to_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_temperature_2026.csv",
    index=False
)

print("2026 temperature dataset saved")
print(df["study_week"].min())
print(df["study_week"].max())
print(df["study_week"].value_counts().sort_index())