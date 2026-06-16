import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# =====================================================
# FOREST PLOT OF FINAL MODEL IRRs
# =====================================================
#
# Purpose:
# Create a forest plot showing adjusted incidence
# rate ratios (IRRs) and 95% confidence intervals
# from the final Poisson regression model.
#
# Input:
# - final_model_irr.csv
#
# Output:
# - forest_plot_final_model.png
#
# Notes:
# - Percentage variables are displayed as the
#   effect of a 10 percentage-point increase.
# - Continuous environmental variables are shown
#   on their original scale.
#
# =====================================================
# =====================================================

# LOAD IRR TABLE

# =====================================================

df = pd.read_csv("final_model_irr.csv")

# =====================================================

# REMOVE INTERCEPT

# =====================================================

df = df[df["Variable"] != "Intercept"].copy()

# =====================================================

# CONVERT PERCENTAGE VARIABLES TO +10 PP EFFECTS

# =====================================================
# Percentage variables are scaled to represent
# a +10 percentage-point increase rather than
# a one-unit (100 percentage-point) increase.
percentage_vars = [
"female_pct",
"elderly_pct",
"child_pct",
"urban_pct",
"forest_pct"
]

for var in percentage_vars:


    mask = df["Variable"] == var

    df.loc[mask, "IRR"] = (
        df.loc[mask, "IRR"] ** 0.10
    )

    df.loc[mask, "IRR_CI_Lower"] = (
        df.loc[mask, "IRR_CI_Lower"] ** 0.10
    )

    df.loc[mask, "IRR_CI_Upper"] = (
        df.loc[mask, "IRR_CI_Upper"] ** 0.10
    )


# =====================================================

# KEEP VARIABLES FOR DISPLAY

# =====================================================

keep_vars = [
"female_pct",
"elderly_pct",
"child_pct",
"forest_pct",
"urban_pct",
"temp_lag1",
"pm10_mean",
"pm10_lag1",
"o3_lag1"
]

df = df[df["Variable"].isin(keep_vars)]

# =====================================================

# LABELS

# =====================================================

labels = {


"female_pct": "Female Share (+10 pp)",
"elderly_pct": "Elderly Population (+10 pp)",
"child_pct": "Child Population (+10 pp)",
"urban_pct": "Urban Cover (+10 pp)",
"forest_pct": "Forest Cover (+10 pp)",

"temp_lag1": "Temperature (Lag 1)",
"pm10_mean": "PM10 (Current)",
"pm10_lag1": "PM10 (Lag 1)",
"o3_lag1": "O₃ (Lag 1)"


}

df["Label"] = df["Variable"].map(labels)

# =====================================================

# ORDER

# =====================================================

order = [
"female_pct",
"elderly_pct",
"child_pct",
"forest_pct",
"urban_pct",
"temp_lag1",
"o3_lag1",
"pm10_lag1",
"pm10_mean"
]

df["Variable"] = pd.Categorical(
df["Variable"],
categories=order,
ordered=True
)

df = df.sort_values("Variable")

# =====================================================

# CREATE FOREST PLOT

# =====================================================

fig, ax = plt.subplots(figsize=(10, 6))

y = np.arange(len(df))

ax.errorbar(
df["IRR"],
y,
xerr=[
df["IRR"] - df["IRR_CI_Lower"],
df["IRR_CI_Upper"] - df["IRR"]
],
fmt="o",
capsize=4
)

# Reference line

ax.axvline(
1,
color="black",
linestyle="--",
linewidth=1
)

ax.set_yticks(y)
ax.set_yticklabels(df["Label"])

ax.set_xscale("log")

ax.set_xlabel("Incidence Rate Ratio (IRR)")

ax.set_title(
"Final Poisson Regression Model\nAdjusted IRRs (95% Confidence Intervals)"
)

plt.tight_layout()

plt.savefig(
"forest_plot_final_model.png",
dpi=300,
bbox_inches="tight"
)

plt.show()

print("Saved: forest_plot_final_model.png")

