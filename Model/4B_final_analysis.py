import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
# =====================================================
# FINAL MODEL SELECTION
# =====================================================
#
# Purpose:
# Compare the full and reduced Poisson models and
# select the final specification.
#
# Input:
# - model_dataset.csv
#
# Outputs:
# - final_model_comparison.csv
# - final_model_coefficients.csv
# - final_model_irr.csv
# - final_model_diagnostics.csv
# - final_model_summary.csv
#
# Outcome:
# - SindromiResp_Tot
#
# Model family:
# - Poisson GLM
#
# Offset:
# - log(population)
#
# Selection rule:
# - Reduced model selected when
#   ΔAIC ≤ 5 relative to full model.
#
# =====================================================
# ── Input ─────────────────────────────────────────────────────────────────────

INPUT_FILE = ("model_dataset_with_8223.csv")

# ── Load data ─────────────────────────────────────────────────────────────────

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df):,} rows.")
print()

# ── Step 1: Create final modelling dataset ───────────────────────────────────

final_data = df[
[
"SindromiResp_Tot",

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

    "female_pct",

    "population"
]

].dropna()

print(f"Analysis rows: {len(final_data):,}")
print()

# ── Step 2: Full final model ─────────────────────────────────────────────────

full_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

pm10_mean +
pm10_lag1 +

o3_mean +
o3_lag1 +

weekly_mean +
temp_lag1 +

urban_pct +
forest_pct +

elderly_pct +
child_pct +
female_pct
""",
data=final_data,
family=sm.families.Poisson(),
offset=np.log(final_data["population"])


).fit()

# ── Step 3: Reduced final model ──────────────────────────────────────────────

reduced_model = smf.glm(
formula=
"""
SindromiResp_Tot ~


pm10_mean +

o3_lag1 +

temp_lag1 +

urban_pct +
forest_pct +

elderly_pct +
child_pct +
female_pct
""",
data=final_data,
family=sm.families.Poisson(),
offset=np.log(final_data["population"])

).fit()

# ── Step 4: Compare models ───────────────────────────────────────────────────

comparison = pd.DataFrame({
"Model": ["Full", "Reduced"],
"AIC": [full_model.aic, reduced_model.aic],
"Dispersion": [
full_model.pearson_chi2 / full_model.df_resid,
reduced_model.pearson_chi2 / reduced_model.df_resid
]
})

print(comparison)
print()

comparison.to_csv(
"final_model_comparison.csv",
index=False
)

# ── Step 5: Select best model ────────────────────────────────────────────────

if reduced_model.aic <= full_model.aic + 5:
    final_model = reduced_model
    final_name = "Reduced"
else:
    final_model = full_model
    final_name = "Full"

print(f"Selected model: {final_name}")
print()


# ── Step 6: Coefficient table ────────────────────────────────────────────────

conf_int = final_model.conf_int()

coef_table = pd.DataFrame({
"Variable": final_model.params.index,
"Coefficient": final_model.params.values,
"Std_Error": final_model.bse.values,
"P_Value": final_model.pvalues.values,
"CI_Lower": conf_int[0].values,
"CI_Upper": conf_int[1].values
})

coef_table.to_csv(
"final_model_coefficients.csv",
index=False
)

# ── Step 7: Incidence Rate Ratios (IRR) ─────────────────────────────────────

irr_table = pd.DataFrame({
"Variable": final_model.params.index,
"IRR": np.exp(final_model.params.values),
"IRR_CI_Lower": np.exp(conf_int[0].values),
"IRR_CI_Upper": np.exp(conf_int[1].values),
"P_Value": final_model.pvalues.values
})

irr_table.to_csv(
"final_model_irr.csv",
index=False
)

# ── Step 8: Diagnostics ──────────────────────────────────────────────────────

diagnostics = pd.DataFrame({
"Metric": [
"AIC",
"Dispersion",
"Observations"
],
"Value": [
final_model.aic,
final_model.pearson_chi2 / final_model.df_resid,
len(final_data)
]
})

diagnostics.to_csv(
"final_model_diagnostics.csv",
index=False
)

# ── Step 9: Save full summaries ──────────────────────────────────────────────

coef_table.to_csv(
"final_model_summary.csv",
index=False
)

print("Saved final_model_comparison.csv")
print("Saved final_model_coefficients.csv")
print("Saved final_model_irr.csv")
print("Saved final_model_diagnostics.csv")
print("Saved final_model_summary.csv")
