import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
# =====================================================
# MODEL TYPE COMPARISON
# =====================================================
#
# Purpose:
# Compare alternative count-data model specifications
# for respiratory outcomes.
#
# Input:
# - model_dataset.csv
#
# Outputs:
# - model_type_comparison.csv
# - poisson_summary.csv
# - robust_poisson_summary.csv
# - negative_binomial_summary.csv
#
# Outcome:
# - SindromiResp_Tot
#
# Predictors:
# - weekly_mean
# - pm10_mean
# - o3_mean
#
# Offset:
# - log(population)
#
# Models:
# - Standard Poisson
# - Robust Poisson (HC3)
# - Negative Binomial
#
# =====================================================
# ── Input / Output ───────────────────────────────────────────────────────────

INPUT_FILE = "model_dataset.csv"
OUTPUT_FILE = "model_type_comparison.csv"

# ── Load data ────────────────────────────────────────────────────────────────

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df):,} rows.")
print()

# ── Baseline dataset ─────────────────────────────────────────────────────────

model_data = df[
[
"SindromiResp_Tot",
"weekly_mean",
"pm10_mean",
"o3_mean",
"population"
]
].dropna()

print(f"Analysis rows: {len(model_data):,}")
print()

# ── Model 1: Standard Poisson ────────────────────────────────────────────────

poisson_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean +
pm10_mean +
o3_mean
""",
data=model_data,
family=sm.families.Poisson(),
offset=np.log(model_data["population"])
).fit()
# Dispersion > 1 suggests overdispersion
# Dispersion ≈ 1 indicates Poisson assumptions
# are reasonably satisfied.
poisson_dispersion = (
poisson_model.pearson_chi2 /
poisson_model.df_resid
)

print("STANDARD POISSON")
print("AIC:", poisson_model.aic)
print("Dispersion:", poisson_dispersion)
print()

# ── Model 2: Robust Poisson ──────────────────────────────────────────────────

robust_poisson = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean +
pm10_mean +
o3_mean
""",
data=model_data,
family=sm.families.Poisson(),
offset=np.log(model_data["population"])
).fit(cov_type="HC3")

robust_dispersion = (
robust_poisson.pearson_chi2 /
robust_poisson.df_resid
)

print("ROBUST POISSON")
print("AIC:", robust_poisson.aic)
print("Dispersion:", robust_dispersion)
print()

# ── Model 3: Negative Binomial ───────────────────────────────────────────────
# Negative Binomial is evaluated as an alternative
# count-data model when overdispersion is present.
nb_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean +
pm10_mean +
o3_mean
""",
data=model_data,
family=sm.families.NegativeBinomial(),
offset=np.log(model_data["population"])
).fit()

print("NEGATIVE BINOMIAL")
print("AIC:", nb_model.aic)
print()

# ── Comparison table ─────────────────────────────────────────────────────────

comparison = pd.DataFrame({
"Model": [
"Poisson",
"Robust Poisson",
"Negative Binomial"
],
"AIC": [
poisson_model.aic,
robust_poisson.aic,
nb_model.aic
],
"Dispersion": [
poisson_dispersion,
robust_dispersion,
np.nan
]
})

print("Model Type Comparison")
print(comparison)
print()

comparison.to_csv(
OUTPUT_FILE,
index=False
)

# ── Coefficient tables ───────────────────────────────────────────────────────

def save_summary(model, filename):

    conf_int = model.conf_int()

    summary_df = pd.DataFrame({
        "Variable": model.params.index,
        "Coefficient": model.params.values,
        "Std_Error": model.bse.values,
        "P_Value": model.pvalues.values,
        "CI_Lower": conf_int[0].values,
        "CI_Upper": conf_int[1].values
    })

    summary_df.to_csv(
        filename,
        index=False
    )



save_summary(
poisson_model,
"poisson_summary.csv"
)

save_summary(
robust_poisson,
"robust_poisson_summary.csv"
)

save_summary(
nb_model,
"negative_binomial_summary.csv"
)

print("Saved model_type_comparison.csv")
print("Saved poisson_summary.csv")
print("Saved robust_poisson_summary.csv")
print("Saved negative_binomial_summary.csv")
