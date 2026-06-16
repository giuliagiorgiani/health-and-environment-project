# Respiratory Health Modelling Pipeline

A Python workflow for investigating the relationship between air pollution, temperature, land use, demographic vulnerability, and respiratory syndromes using population-adjusted Poisson regression models.

---

## Overview

```text
Final Environment-Health Panel
      │
      ├─► Step 1: Data Preparation
      │       • Seasonal indicators
      │       • Lag variables
      │       • Modelling dataset
      │
      ├─► Step 2: Model Type Assessment
      │       • Standard Poisson
      │       • Robust Poisson
      │       • Negative Binomial
      │
      ├─► Step 3: Model Development
      │       • Baseline model
      │       • Interaction model
      │       • Land-use model
      │       • Vulnerability model
      │       • Demographic models
      │       • Lag assessment
      │
      ├─► Step 4: Final Analysis & Validation
      │       • Full model
      │       • Reduced model
      │       • Model selection
      │       • Temporal validation
      │       • Spatial diagnostics
      │       • Calibrated risk index
      │
      ├─► Step 5: Forest Plot
      │
      └─► Step 6: Spatial Visualisation
              • Environmental indicators
              • Demographic indicators
              • Respiratory outcomes
              • Calibrated risk
```

---

## Requirements

* Python 3.8+
* pandas
* numpy
* statsmodels
* matplotlib
* geopandas
* libpysal
* esda
* scikit-learn

Install dependencies:

```bash
pip install pandas numpy statsmodels matplotlib geopandas libpysal esda scikit-learn
```

Windows users may use:

```bash
py -m pip install pandas numpy statsmodels matplotlib geopandas libpysal esda scikit-learn
```

---

## Input Data

Required input file:

```text
FINAL_polygon_environment_health_panel_population_age.csv
```

Required variables:

| Variable         | Description                   |
| ---------------- | ----------------------------- |
| IdSensore        | Polygon identifier            |
| Anno             | Study year                    |
| study_week       | Study week                    |
| SindromiResp_Tot | Respiratory syndrome count    |
| pm10_mean        | Weekly PM10 concentration     |
| o3_mean          | Weekly ozone concentration    |
| weekly_mean      | Weekly mean temperature       |
| urban_pct        | Urban land cover proportion   |
| forest_pct       | Forest land cover proportion  |
| elderly_pct      | Elderly population proportion |
| child_pct        | Child population proportion   |
| female_pct       | Female population proportion  |
| population       | Population denominator        |

---

## Statistical Framework

All regression models are estimated using Poisson generalized linear models with a population offset:

```text
log(E[Y]) = β₀ + β₁X₁ + β₂X₂ + ... + βₖXₖ + log(population)
```

where:

* Y = respiratory syndrome count
* X = environmental, land-use, and demographic predictors
* log(population) is included as an offset term

---

# Scripts

## Step 1 — Data Preparation

**File:** `1_prepare_model_data.py`

Purpose:

* Create seasonal indicators
* Create temperature-based indicators
* Generate one-week lag variables
* Select modelling variables
* Create the final modelling dataset

Outputs:

```text
model_dataset.csv
```

---

## Step 2 — Model Type Assessment

**File:** `2_model_type_comparison.py`

Purpose:

Evaluate alternative count-data model specifications.

Models evaluated:

* Standard Poisson
* Robust Poisson (HC3)
* Negative Binomial

Outputs:

```text
model_type_comparison.csv
poisson_summary.csv
robust_poisson_summary.csv
negative_binomial_summary.csv
```

---

## Step 3 — Model Development

**File:** `3_model_development.py`

Purpose:

Develop and compare alternative model specifications.

Models evaluated:

### Baseline Model

```text
weekly_mean
pm10_mean
o3_mean
```

### Interaction Model

```text
weekly_mean
pm10_mean
o3_mean
warm_temp

PM10 × warm_temp
O3 × warm_temp
```

### Land-Use Model

```text
Interaction Model
+ urban_pct
+ forest_pct
```

### Vulnerability Model

```text
Land-Use Model
+ elderly_pct
+ child_pct
```

### Demographic Models

```text
Vulnerability Model
+ female_pct
```

### Lag Assessment

Comparison of:

```text
Current exposure model
Lagged exposure model
Current + lagged exposure model
```

Outputs:

```text
baseline_summary.csv
interaction_summary.csv
landuse_summary.csv
vulnerability_summary.csv

current_summary.csv
lag_summary.csv
current_lag_summary.csv

development_model_comparison.csv
lag_model_comparison.csv
model_comparison.csv
```

---

## Step 4 — Final Analysis

**File:** `4_final_analysis.py`

Purpose:

Compare full and reduced models and export the final selected model.

### Full Model

```text
pm10_mean
pm10_lag1
o3_mean
o3_lag1
weekly_mean
temp_lag1
urban_pct
forest_pct
elderly_pct
child_pct
female_pct
```

### Reduced Model

```text
pm10_mean
o3_lag1
temp_lag1
urban_pct
forest_pct
elderly_pct
child_pct
female_pct
```

Outputs:

```text
final_model_comparison.csv
final_model_coefficients.csv
final_model_irr.csv
final_model_diagnostics.csv
final_model_summary.csv
```
### Temporal Validation
**File:** `4b_temporal_validation.py`
Purpose: Verify the true predictive capacity of the model on unseen data (Out-of-Sample Validation). The dataset is split into a Training Set (2022-2024) to estimate coefficients and a Test Set (2025-2026) to generate predictions. Standard error metrics (RMSE, MAE, R-squared) are calculated to ensure the model isn't overfitting and to confirm its reliability for future simulations.

Outputs:
```text
temporal_validation_metrics.csv
```

### Spatial Diagnostics
**File:** `4c_spatial_diagnostics.py`
Purpose: Identify any systematic geographic errors in the model through spatial residual analysis. Utilizes geopandas and libpysal to calculate the spatial weights matrix (Queen contiguity) and the Global Moran's I on the model's Pearson residuals. This assessment determines whether the model's prediction errors are randomly distributed across space or exhibit significant spatial autocorrelation.

Outputs:
```text
spatial_residuals_map.png
```
### Calibrated Risk Index
**File:** `4d_calibrated_risk_index.py`
Purpose: Replace hardcoded decision weights with a data-driven Risk Index based on the actual coefficients (β) learned by the model. Uses the linear predictor of the Poisson model to calculate the combined multiplicative effect of pollution, climate, and demographics on baseline risk. Absolute risk is calculated for each polygon/week and normalized on a 0 to 100 scale, transforming statistical output into a highly interpretable management tool.

Outputs:
```text
calibrated_risk_index.csv
```

---

## Step 5 — Forest Plot

**File:** `5_forest_plot.py`

Purpose:

Create a forest plot showing adjusted incidence rate ratios (IRRs) and 95% confidence intervals from the final model.

Output:

```text
forest_plot_final_model.png
```

---

## Step 6 — Spatial Visualisation

**File:** `6_create_maps.py`

Purpose:

Generate spatial maps of environmental, demographic, and health indicators.

Outputs:

```text
Respiratory_Rate_Map.png
Respiratory_Cases_Map.png
PM10_Map.png
O3_Map.png
Temperature_Map.png
Female_Map.png
Elderly_Map.png
Child_Map.png
```
**File:** `6b_map_calibrated_risk.py`
Purpose: Spatially visualize the areas with the highest structural risk according to the model's objective estimates. Merges the aggregated results from calibrated_risk_index.csv with the spatial geometries of the .shp file (e.g., Voronoi polygons). Generates a choropleth map illustrating the distribution of average risk, allowing decision-makers to visually identify city "hotspots" of chronic respiratory vulnerability at a glance.
Outputs:
```text
Calibrated_Risk_Map.png
```

---

## Running Order

Run scripts in the following order:

```bash
python 1_prepare_model_data.py
python 2_model_type_comparison.py
python 3_model_development.py
python 4_final_analysis.py
python 4b_temporal_validation.py
python 4c_spatial_diagnostics_lisa.py
python 4d_calibrated_risk_index.py
python 5_forest_plot.py
python 6_create_maps.py
python 6b_map_calibrated_risk.py
```

Windows users may replace `python` with `py`.

---

## Key Outputs

| File                             | Description                             |
|----------------------------------|-----------------------------------------|
| model_dataset.csv                | Final modelling dataset                 |
| model_type_comparison.csv        | Comparison of model families            |
| development_model_comparison.csv | Model development comparison            |
| lag_model_comparison.csv         | Lag assessment comparison               |
| final_model_comparison.csv       | Full versus reduced model comparison    |
| final_model_coefficients.csv     | Final coefficient estimates             |
| final_model_irr.csv              | Incidence Rate Ratios                   |
| final_model_diagnostics.csv      | Final model diagnostics                 |
| temporal_validation_metrics.csv  | Out-of-sample error metrics             |
| calibrated_risk_index.csv        | Normalized risk index based on actual β |
| forest_plot_final_model.png      | Forest plot of adjusted IRRs            |
| Calibrated_Risk_Map.png          | Structural risk distribution map        |

---

## Notes

* Models are fitted using Poisson regression with a population offset.
* Lag variables represent one-week delayed environmental exposures.
* Model selection is based on AIC, dispersion, and model parsimony.
* Model-type assessment compares Poisson, Robust Poisson, and Negative Binomial specifications.
* Final model diagnostics are exported to `final_model_diagnostics.csv`.
* Forest plots display adjusted incidence rate ratios (IRRs) with 95% confidence intervals.
* Spatial visualisations summarise environmental, demographic, and health characteristics across polygons.

```
```
