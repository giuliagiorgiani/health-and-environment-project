import pandas as pd

df = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\pm10_2022.csv"
)

print(df.head())
print(df.dtypes)
print(df.shape)

df["data"] = pd.to_datetime(df["data"])

print(df["data"].min())
print(df["data"].max())
print(df.dtypes)

print(df.isna().sum())

print(df["stato"].unique())

print(df["valore"].describe())

print(
    df["stato"]
    .value_counts(dropna=False)
)
df["valore"] = df["valore"].replace(-9999, pd.NA)

df["valore"] = pd.to_numeric(
    df["valore"],
    errors="coerce"
)

df = df.sort_values(
    by=["idsensore", "data"]
)
df["valore"] = (
    df.groupby("idsensore")["valore"]
    .transform(lambda x: x.interpolate())
)
df["valore"] = (
    df.groupby("idsensore")["valore"]
    .transform(lambda x: x.ffill().bfill())
)

print(df["valore"].isna().sum())
print(df["valore"].describe())

start_date = pd.Timestamp("2022-01-12")

df["study_week"] = (
    ((df["data"] - start_date).dt.days // 7) + 3
)

# remove incomplete final week
df = df[df["study_week"] <= 16]

print(
    df[["data", "study_week"]]
    .head(20)
)

print(df["study_week"].value_counts().sort_index())

weekly_pm10 = (
    df.groupby(["idsensore", "study_week"])["valore"]
    .agg(
        weekly_mean="mean",
        weekly_std="std"
    )
    .reset_index()
)

print(weekly_pm10.head())

print(weekly_pm10.shape)

weights = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\pm10_weights.csv"
)

print(weights.head())
print(weights.columns)

weekly_pm10 = weekly_pm10.rename(
    columns={"idsensore": "idSensore"}
)

merged = weekly_pm10.merge(
    weights,
    on="idSensore",
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
ats_weekly_pm10 = (
    merged.groupby(
        ["CODICE_ATS", "DESCRIZION", "study_week"]
    )[["weighted_mean", "weighted_std"]]
    .sum()
    .reset_index()
)

print(ats_weekly_pm10.head())

print(ats_weekly_pm10.shape)

ats_weekly_pm10.to_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\python\processed_data\ats_weekly_pm10_2022.csv",
    index=False
)

print("2022 pm10 dataset saved")