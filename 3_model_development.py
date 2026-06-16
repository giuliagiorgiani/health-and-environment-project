import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
# =====================================================
# POISSON MODEL DEVELOPMENT AND COMPARISON
# =====================================================
#
# Purpose:
# Compare alternative Poisson regression models
# for respiratory outcomes.
#
# Input:
# - model_dataset.csv
#
# Outputs:
# - baseline_summary.csv
# - interaction_summary.csv
# - landuse_summary.csv
# - vulnerability_summary.csv
# - demographic_female_summary.csv
# - demographic_male_summary.csv
# - current_summary.csv
# - lag_summary.csv
# - current_lag_summary.csv
# - model_comparison.csv
# - development_model_comparison.csv
# - lag_model_comparison.csv
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
# =====================================================
# ── Input / Output ────────────────────────────────────────────────────────────

INPUT_FILE  = "model_dataset.csv"
OUTPUT_FILE = "model_comparison.csv"

# ── Load data ─────────────────────────────────────────────────────────────────

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df):,} rows.")
print()

results = []

# ── Helper function ───────────────────────────────────────────────────────────

def save_model_results(name, model):

    dispersion = (
        model.pearson_chi2 /
        model.df_resid
    )

    results.append(
        {
            "Model": name,
            "AIC": model.aic,
            "Dispersion": dispersion
        }
    )

    print(f"{name}")
    print(f"AIC: {model.aic:.3f}")
    print(f"Dispersion: {dispersion:.3f}")
    print()

def save_summary_table(model, filename):

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

    print(f"Saved: {filename}")
# ── Step 1: Baseline model ───────────────────────────────────────────────────

baseline_data = df[
[
"SindromiResp_Tot",
"weekly_mean",
"pm10_mean",
"o3_mean",
"population"
]
].dropna()

baseline_model = smf.glm(
formula=
"""
SindromiResp_Tot ~
weekly_mean +
pm10_mean +
o3_mean
""",
data=baseline_data,
family=sm.families.Poisson(),
offset=np.log(baseline_data["population"])
).fit()

save_model_results(
"Baseline",
baseline_model
)

save_summary_table(
baseline_model,
"baseline_summary.csv"
)

# ── Step 2: Interaction model ────────────────────────────────────────────────

interaction_data = df[
[
"SindromiResp_Tot",
"weekly_mean",
"pm10_mean",
"o3_mean",
"warm_temp",
"population"
]
].dropna()

interaction_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean+
pm10_mean +
o3_mean +
warm_temp +

pm10_mean:warm_temp +
o3_mean:warm_temp
""",
data=interaction_data,
family=sm.families.Poisson(),
offset=np.log(interaction_data["population"])

).fit()

save_model_results(
"Interaction",
interaction_model
)

save_summary_table(
interaction_model,
"interaction_summary.csv"
)

# ── Step 3: Land-use model ───────────────────────────────────────────────────

landuse_data = df[
[
"SindromiResp_Tot",
"weekly_mean",
"pm10_mean",
"o3_mean",
"warm_temp",
"urban_pct",
"forest_pct",
"population"
]
].dropna()

landuse_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean+
pm10_mean +
o3_mean +
warm_temp +

pm10_mean:warm_temp +
o3_mean:warm_temp +

urban_pct +
forest_pct
""",
data=landuse_data,
family=sm.families.Poisson(),
offset=np.log(landuse_data["population"])


).fit()

save_model_results(
"Land Use",
landuse_model
)

save_summary_table(
landuse_model,
"landuse_summary.csv"
)

# ── Step 4: Vulnerability model ──────────────────────────────────────────────

vulnerability_data = df[
[
"SindromiResp_Tot",
"weekly_mean",
"pm10_mean",
"o3_mean",
"warm_temp",
"urban_pct",
"forest_pct",
"elderly_pct",
"child_pct",
"female_pct",
"male_pct",
"population"
]
].dropna()

vulnerability_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean+
pm10_mean +
o3_mean +
warm_temp +

pm10_mean:warm_temp +
o3_mean:warm_temp +

urban_pct +
forest_pct +

elderly_pct +
child_pct
""",
data=vulnerability_data,
family=sm.families.Poisson(),
offset=np.log(vulnerability_data["population"])


).fit()

save_model_results(
"Vulnerability",
vulnerability_model
)

save_summary_table(
vulnerability_model,
"vulnerability_summary.csv"
)

# ── Step 4b: Demographic Structure (Female) ─────────────────────────
# -----------------------------------------------------
# Sex composition models
# -----------------------------------------------------
#
# Female and male percentages are perfectly
# collinear. Therefore they are evaluated in
# separate models.
#
# -----------------------------------------------------
female_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean +
pm10_mean +
o3_mean +
warm_temp +

pm10_mean:warm_temp +
o3_mean:warm_temp +

urban_pct +
forest_pct +

elderly_pct +
child_pct +

female_pct
""",
data=vulnerability_data,
family=sm.families.Poisson(),
offset=np.log(vulnerability_data["population"])
).fit()

save_model_results(
"Demographic Structure (Female)",
female_model
)

save_summary_table(
female_model,
"demographic_female_summary.csv"
)

# ── Step 4c: Demographic Structure (Male) ───────────────────────────

male_model = smf.glm(
formula=
"""
SindromiResp_Tot ~

weekly_mean +
pm10_mean +
o3_mean +
warm_temp +

pm10_mean:warm_temp +
o3_mean:warm_temp +

urban_pct +
forest_pct +

elderly_pct +
child_pct +

male_pct
""",
data=vulnerability_data,
family=sm.families.Poisson(),
offset=np.log(vulnerability_data["population"])
).fit()

save_model_results(
"Demographic Structure (Male)",
male_model
)

save_summary_table(
male_model,
"demographic_male_summary.csv"
)



# ── Step 5: Lag and current separated and combined───────────────────────────────────────────────────

lag_data = df[
[
"SindromiResp_Tot",


    "weekly_mean",
    "pm10_mean",
    "o3_mean",

    "temp_lag1",
    "pm10_lag1",
    "o3_lag1",

    "urban_pct",
    "forest_pct",

    "elderly_pct",
    "child_pct",

    "population"
]


].dropna()


current_model = smf.glm(
formula=
"""
SindromiResp_Tot ~


pm10_mean +
o3_mean +
weekly_mean +

urban_pct +
forest_pct +

elderly_pct +
child_pct
""",
data=lag_data,
family=sm.families.Poisson(),
offset=np.log(lag_data["population"])

).fit()

save_model_results(
"Current",
current_model
)

save_summary_table(
current_model,
"current_summary.csv"
)
lag_model = smf.glm(
formula=
"""
SindromiResp_Tot ~


pm10_lag1 +
o3_lag1 +
temp_lag1 +

urban_pct +
forest_pct +

elderly_pct +
child_pct
""",
data=lag_data,
family=sm.families.Poisson(),
offset=np.log(lag_data["population"])


).fit()

save_model_results(
"Lag",
lag_model
)

save_summary_table(
lag_model,
"lag_summary.csv"
)


combined_model = smf.glm(
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
child_pct
""",
data=lag_data,
family=sm.families.Poisson(),
offset=np.log(lag_data["population"])


).fit()

save_model_results(
"Current + Lag",
combined_model
)

save_summary_table(
combined_model,
"current_lag_summary.csv"
)
# ── Step 6: Model comparison table ───────────────────────────────────────────
# ── Step 6: Model comparison tables ──────────────────────────────────────────

comparison = pd.DataFrame(results)

comparison = comparison.sort_values(
    "AIC"
)

print("Model comparison:")
print(comparison)
print()

comparison.to_csv(
    "model_comparison.csv",
    index=False
)

development_models = comparison[
    comparison["Model"].isin(
        [
            "Baseline",
            "Interaction",
            "Land Use",
            "Vulnerability",
            "Demographic Structure (Female)",
            "Demographic Structure (Male)"
        ]
    )
]

development_models.to_csv(
    "development_model_comparison.csv",
    index=False
)

lag_models = comparison[
    comparison["Model"].isin(
        [
            "Current",
            "Lag",
            "Current + Lag"
        ]
    )
]

lag_models.to_csv(
    "lag_model_comparison.csv",
    index=False
)

print("Saved model_comparison.csv")
print("Saved development_model_comparison.csv")
print("Saved lag_model_comparison.csv")