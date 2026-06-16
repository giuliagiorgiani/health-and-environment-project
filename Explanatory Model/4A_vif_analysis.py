import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv(
    "FINAL_polygon_environment_health_panel_population_age.csv"
)
# =====================================================
# SORT PANEL
# =====================================================

df = df.sort_values(
    ["IdSensore", "Anno", "study_week"]
)

# =====================================================
# CREATE LAG VARIABLES
# =====================================================

df["pm10_lag1"] = (
    df.groupby("IdSensore")["pm10_mean"]
    .shift(1)
)

df["o3_lag1"] = (
    df.groupby("IdSensore")["o3_mean"]
    .shift(1)
)

df["temp_lag1"] = (
    df.groupby("IdSensore")["weekly_mean"]
    .shift(1)
)
# =====================================================
# VARIABLES
# =====================================================

vars_corr = [
    "pm10_mean",
    "pm10_lag1",
    "o3_mean",
    "o3_lag1",
    "weekly_mean",
    "temp_lag1",
    "urban_pct",
    "forest_pct",
    "elderly_pct",
    "child_pct",
    "female_pct"
]

corr = df[vars_corr].corr()
corr.columns = [
    "PM10",
    "PM10 Lag 1",
    "O₃",
    "O₃ Lag 1",
    "Temperature",
    "Temperature Lag 1",
    "Urban %",
    "Forest %",
    "Elderly %",
    "Child %",
    "Female %"
]

corr.index = corr.columns
# =====================================================
# PLOT
# =====================================================

plt.figure(figsize=(10, 8))

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    square=True
)

plt.title(
    "Correlation Matrix of Health, Environmental and Demographic Variables",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    "Correlation_Heatmap.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant


# =====================================================
# FINAL MODEL VARIABLES
# =====================================================

X = df[
[
    "pm10_mean",
    "pm10_lag1",
    "o3_mean",
    "o3_lag1",
    "weekly_mean",
    "temp_lag1",
    "urban_pct",
    "forest_pct",
    "elderly_pct",
    "child_pct",
    "female_pct"
]
].dropna()

# =====================================================
# ADD CONSTANT
# =====================================================

X = add_constant(X)

# =====================================================
# CALCULATE VIF
# =====================================================

vif_df = pd.DataFrame()

vif_df["Variable"] = X.columns

vif_df["VIF"] = [
    variance_inflation_factor(X.values, i)
    for i in range(X.shape[1])
]

vif_df = vif_df[vif_df["Variable"] != "const"]

vif_df = vif_df.sort_values(
    by="VIF",
    ascending=False
)

print("\nVIF RESULTS\n")
print(vif_df)

vif_df.to_csv(
    "final_model_vif.csv",
    index=False
)

print("\nSaved: final_model_vif.csv")
