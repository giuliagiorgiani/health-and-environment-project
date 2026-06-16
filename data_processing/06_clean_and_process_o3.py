import pandas as pd
# =====================================================
# WEEKLY O3 PROCESSING
# =====================================================
#
# Input:
#   o3_2026.csv
#
# Output:
#   weekly_o3_station_2026.csv
#
# Processing steps:
#   1. Convert dates
#   2. Remove invalid values (-9999)
#   3. Interpolate missing observations
#   4. Create study weeks
#   5. Calculate 8-hour running averages
#   6. Calculate daily maximum 8-hour averages
#   7. Count exceedance days (>120 µg/m³)
#   8. Aggregate to station-week level
#
# To use for another year:
#   1. Change input filename
#   2. Change start_date
#   3. Change study week range
#   4. Change output filename
#
# Example:
#   2026 -> start_date = "2025-12-29"
#   2025 -> start_date = "2024-12-30"
#   2024 -> start_date = "2023-12-25"
#
# O3 exceedance threshold:
#   Daily maximum 8-hour average > 120 µg/m³
#
# =====================================================
# =====================================================
# LOAD O3 DATA
# =====================================================

df = pd.read_csv(
    "o3_2026.csv"
)

print(df.head())

print(df.dtypes)

print(df.shape)

# =====================================================
# CONVERT DATE/TIME
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
start_date = pd.Timestamp("2025-12-29")

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
# CALCULATE 8-HOUR RUNNING AVERAGE
# =====================================================

df["o3_8h_avg"] = (
    df.groupby("idsensore")["valore"]
    .transform(
        lambda x:
        x.rolling(
            window=8,
            min_periods=8
        ).mean()
    )
)

print(
    df[
        [
            "idsensore",
            "data",
            "valore",
            "o3_8h_avg"
        ]
    ].head(20)
)

# =====================================================
# CREATE DAILY O3 DATA
# daily maximum 8-hour average
# =====================================================

daily_o3 = (
    df.groupby(
        [
            "idsensore",
            "date",
            "study_week"
        ]
    )
    .agg(
        daily_mean=("valore", "mean"),
        daily_max_8h=("o3_8h_avg", "max"),
        daily_min=("valore", "min")
    )
    .reset_index()
)

print(daily_o3.head())

print(daily_o3.shape)

# =====================================================
# DAILY O3 EXCEEDANCE
# threshold = 120 µg/m³
# =====================================================

daily_o3["o3_exceed_day"] = (
    daily_o3["daily_max_8h"] > 120
).astype(int)

print(
    daily_o3[
        [
            "daily_mean",
            "daily_max_8h",
            "daily_min",
            "o3_exceed_day"
        ]
    ].head()
)

# =====================================================
# WEEKLY AGGREGATION
# =====================================================

weekly_o3 = (
    daily_o3.groupby(
        [
            "idsensore",
            "study_week"
        ]
    )
    .agg(
        weekly_mean=("daily_mean", "mean"),
        weekly_std=("daily_mean", "std"),
        weekly_max_8h=("daily_max_8h", "max"),
        weekly_min=("daily_min", "min"),
        o3_exceed_days=("o3_exceed_day", "sum")
    )
    .reset_index()
)

print(weekly_o3.head())

print(weekly_o3.shape)

# =====================================================
# SAVE STATION-WEEK DATASET
# =====================================================

weekly_o3.to_csv(
    "weekly_o3_station_2026.csv",
    index=False
)

print("weekly O3 station dataset saved")
print(
    weekly_o3.loc[
        weekly_o3["weekly_max_8h"].idxmax()
    ]
)
