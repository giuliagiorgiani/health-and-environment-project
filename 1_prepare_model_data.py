import pandas as pd
import numpy as np
# =====================================================
# MODEL DATASET CREATION
# =====================================================
#
# Purpose:
# Create the final modelling dataset from the
# environment-health panel.
#
# Input:
# - FINAL_polygon_environment_health_panel_population_age.csv
#
# Output:
# - model_dataset.csv
#
# Derived variables:
# - warm_period
# - warm_temp
# - pm10_lag1
# - o3_lag1
# - temp_lag1
#
# =====================================================
# ── Input / Output ────────────────────────────────────────────────────────────
INPUT_FILE = "FINAL_polygon_environment_health_panel_population_age.csv"
OUTPUT_FILE = "model_dataset.csv"

# ── Load data ─────────────────────────────────────────────────────────────────

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df):,} rows.")
print()

# ── Step 1: Create seasonal indicators ───────────────────────────────────────

# Warm season based on study week

df["warm_period"] = (
df["study_week"] >= 14
).astype(int)

# Warm week based on temperature threshold

df["warm_temp"] = (
df["weekly_mean"] >= 8
).astype(int)

print("Warm season indicator:")
print(df["warm_period"].value_counts())
print()

print("Warm temperature indicator:")
print(df["warm_temp"].value_counts())
print()
# -----------------------------------------------------
# LAG VARIABLES
# -----------------------------------------------------
#
# Lagged exposures are calculated within each
# polygon-year combination.
#
# Example:
# Week 5 uses exposure values from Week 4.
#
# -----------------------------------------------------
# ── Step 2: Sort panel for lag calculation ───────────────────────────────────

df = df.sort_values(
["IdSensore", "Anno", "study_week"]
)

# ── Step 3: Create lag variables ─────────────────────────────────────────────

df["pm10_lag1"] = (
df.groupby(["IdSensore", "Anno"])["pm10_mean"]
.shift(1)
)

df["o3_lag1"] = (
df.groupby(["IdSensore", "Anno"])["o3_mean"]
.shift(1)
)

df["temp_lag1"] = (
df.groupby(["IdSensore", "Anno"])["weekly_mean"]
.shift(1)
)

print("Lag variable missing values:")
print(
df[
[
"pm10_lag1",
"o3_lag1",
"temp_lag1"
]
].isna().sum()
)
print()

# ── Step 4: Select modelling variables ──────────────────────────────────────

model_data = df[
[
"IdSensore",
"Anno",
"study_week",


    "SindromiResp_Tot",

    "weekly_mean",
    "pm10_mean",
    "o3_mean",

    "warm_period",
    "warm_temp",

    "pm10_lag1",
    "o3_lag1",
    "temp_lag1",

    "urban_pct",
    "forest_pct",

    "elderly_pct",
    "child_pct",

    "female_pct",
    "male_pct",

    "population"
]

]

print("Selected variables:")
print(model_data.columns.tolist())
print()

# ── Step 5: Missing value summary ────────────────────────────────────────────

print("Missing values:")
print(model_data.isna().sum())
print()

# ── Step 6: Summary ──────────────────────────────────────────────────────────

print("Dataset shape:")
print(model_data.shape)
print()

print("Outcome summary:")
print(
model_data["SindromiResp_Tot"]
.describe()
.round(3)
)
print()

print("First rows:")
print(model_data.head())
print()

# ── Save ─────────────────────────────────────────────────────────────────────

model_data.to_csv(
OUTPUT_FILE,
index=False
)

print(f"Saved to: {OUTPUT_FILE}")
