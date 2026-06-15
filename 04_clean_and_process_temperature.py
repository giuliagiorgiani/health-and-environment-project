import pandas as pd

# =====================================================
# LOAD TEMPERATURE DATA
# =====================================================
# =====================================================
# WEEKLY TEMPERATURE PROCESSING
# =====================================================
#
# Input:
#   temperature_2026.csv
#
# Output:
#   weekly_temperature_station_2026.csv
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
#
# =====================================================
df = pd.read_csv(
    "temperature_2026.csv"
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

print(df.dtypes)

# =====================================================
# CHECK PERIOD
# =====================================================

print(df["data"].min())

print(df["data"].max())

# =====================================================
# MISSING VALUES
# =====================================================

print(df.isna().sum())

# =====================================================
# CHECK VALIDATION STATUS
# =====================================================

print(df["stato"].unique())

# keep validated data only
df = df[df["stato"] == "VA"]

# =====================================================
# REMOVE UNREALISTIC TEMPERATURES
# =====================================================

df = df[
    (df["valore"] >= -25) &
    (df["valore"] <= 50)
]

print(df.shape)

# =====================================================
# SORT VALUES
# =====================================================

df = df.sort_values(
    by=["idsensore", "data"]
)

print(df.head())

# =====================================================
# DESCRIPTIVE STATISTICS
# =====================================================

print(df["valore"].describe())

# =====================================================
# CREATE STUDY WEEK VARIABLE
# =====================================================
# -----------------------------------------------------
# STUDY PERIOD SETTINGS
# -----------------------------------------------------
#
# Update start_date to the first day of study week 1
# for the year being processed.
#
# Also update the study week range if needed.
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

# =====================================================
# CREATE DAILY TEMPERATURE DATA
# =====================================================

daily_temp = (
    df.groupby(
        [
            "idsensore",
            "date",
            "study_week"
        ]
    )["valore"]
    .agg(
        daily_mean="mean",
        daily_max="max",
        daily_min="min"
    )
    .reset_index()
)

print(daily_temp.head())

print(daily_temp.shape)

# =====================================================
# DAILY THRESHOLD INDICATORS
# =====================================================

daily_temp["hot_27"] = (
    daily_temp["daily_max"] > 27
).astype(int)

daily_temp["hot_30"] = (
    daily_temp["daily_max"] > 30
).astype(int)

daily_temp["cold_10"] = (
    daily_temp["daily_mean"] < 10
).astype(int)

daily_temp["cold_0"] = (
    daily_temp["daily_min"] < 0
).astype(int)

daily_temp["very_cold"] = (
    daily_temp["daily_min"] < -5
).astype(int)

print(
    daily_temp[
        [
            "daily_mean",
            "daily_max",
            "daily_min",
            "hot_27",
            "cold_10"
        ]
    ].head()
)

# =====================================================
# WEEKLY AGGREGATION
# =====================================================

weekly_temp = (
    daily_temp.groupby(
        [
            "idsensore",
            "study_week"
        ]
    )
    .agg(
        weekly_mean=("daily_mean", "mean"),
        weekly_std=("daily_mean", "std"),
        weekly_max=("daily_max", "max"),
        weekly_min=("daily_min", "min"),
        hot_days_27=("hot_27", "sum"),
        hot_days_30=("hot_30", "sum"),
        cold_days_10=("cold_10", "sum"),
        cold_days_0=("cold_0", "sum"),
        very_cold_days=("very_cold", "sum")
    )
    .reset_index()
)

print(weekly_temp.head())

print(weekly_temp.shape)

# =====================================================
# SAVE DATASET
# =====================================================

weekly_temp.to_csv(
    "weekly_temperature_station_2026.csv",
    index=False
)

print("weekly station temperature saved")

# =====================================================
# CHECK WEEKS
# =====================================================

print(df["study_week"].min())

print(df["study_week"].max())

print(
    df["study_week"]
    .value_counts()
    .sort_index()
)