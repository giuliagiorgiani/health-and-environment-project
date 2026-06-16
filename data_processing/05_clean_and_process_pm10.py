import pandas as pd
# =====================================================
# WEEKLY PM10 PROCESSING
# =====================================================
#
# Input:
#   pm10_2022.csv
#
# Output:
#   weekly_pm10_station_2022.csv
#
# Processing steps:
#   1. Convert dates
#   2. Remove invalid values (-9999)
#   3. Interpolate missing observations
#   4. Create study weeks
#   5. Calculate weekly PM10 indicators
#   6. Count daily exceedances (>50 µg/m³)
#
# To use for another year:
#   1. Change input filename
#   2. Change start_date
#   3. Change study week range
#   4. Change output filename
#
# Example:
#   2022 -> start_date = "2021-12-29"
#   2023 -> start_date = "2022-12-28"
#   2024 -> start_date = "2023-12-27"
#
# =====================================================
# =====================================================
# LOAD PM10 DATA
# =====================================================

df = pd.read_csv(
    "pm10_2022.csv"
)

print(df.head())

print(df.dtypes)

print(df.shape)

# =====================================================
# CONVERT DATE
# =====================================================

df["data"] = pd.to_datetime(df["data"])

# extract calendar date
df["date"] = df["data"].dt.date

print(df["data"].min())

print(df["data"].max())

print(df.dtypes)

# =====================================================
# MISSING VALUES
# =====================================================

print(df.isna().sum())

# =====================================================
# VALIDATION STATUS
# =====================================================

print(df["stato"].unique())

print(df["valore"].describe())

print(
    df["stato"]
    .value_counts(dropna=False)
)

# =====================================================
# REPLACE INVALID VALUES
# =====================================================

df["valore"] = df["valore"].replace(
    -9999,
    pd.NA
)

# convert to numeric
df["valore"] = pd.to_numeric(
    df["valore"],
    errors="coerce"
)

# =====================================================
# SORT DATA
# =====================================================

df = df.sort_values(
    by=[
        "idsensore",
        "data"
    ]
)

# =====================================================
# INTERPOLATE MISSING VALUES
# =====================================================

df["valore"] = (
    df.groupby("idsensore")["valore"]
    .transform(
        lambda x: x.interpolate()
    )
)

# =====================================================
# FILL REMAINING MISSING VALUES
# =====================================================

df["valore"] = (
    df.groupby("idsensore")["valore"]
    .transform(
        lambda x: x.ffill().bfill()
    )
)

print(df["valore"].isna().sum())

print(df["valore"].describe())

# =====================================================
# CREATE STUDY WEEK VARIABLE
# =====================================================
# -----------------------------------------------------
# STUDY PERIOD SETTINGS
# -----------------------------------------------------
#
# Update start_date to match the first day of
# study week 1 for the selected year.
#
# Update the study week range if necessary.
#
# -----------------------------------------------------
start_date = pd.Timestamp("2021-12-29")

df["study_week"] = (
    ((df["data"] - start_date).dt.days // 7) + 1
)

# keep only study weeks 1–21
df = df[
    (df["study_week"] >= 1) &
    (df["study_week"] <= 21)
]

print(
    df[
        [
            "data",
            "study_week"
        ]
    ].head(20)
)

print(
    df["study_week"]
    .value_counts()
    .sort_index()
)

# =====================================================
# PM10 THRESHOLD INDICATOR
# EU DAILY LIMIT = 50 µg/m³
# =====================================================

df["pm10_exceed"] = (
    df["valore"] > 50
).astype(int)

# =====================================================
# WEEKLY AGGREGATION
# =====================================================

weekly_pm10 = (
    df.groupby(
        [
            "idsensore",
            "study_week"
        ]
    )["valore"]
    .agg(
        weekly_mean="mean",
        weekly_std="std",
        weekly_max="max",
        weekly_min="min"
    )
    .reset_index()
)

# =====================================================
# WEEKLY EXCEEDANCE COUNTS
# =====================================================

thresholds = (
    df.groupby(
        [
            "idsensore",
            "study_week"
        ]
    )[
        [
            "pm10_exceed"
        ]
    ]
    .sum()
    .reset_index()
)

# =====================================================
# MERGE THRESHOLDS
# =====================================================

weekly_pm10 = weekly_pm10.merge(
    thresholds,
    on=[
        "idsensore",
        "study_week"
    ],
    how="left"
)

print(weekly_pm10.head())

print(weekly_pm10.shape)

# =====================================================
# SAVE STATION-WEEK DATASET
# =====================================================

weekly_pm10.to_csv(
    "weekly_pm10_station_2022.csv",
    index=False
)

print("weekly pm10 station dataset saved")
