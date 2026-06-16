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
      ├─► Step 4: Final Analysis
      │       • Full model
      │       • Reduced model
      │       • Model selection
      │       • Incidence Rate Ratios (IRRs)
      │       • Diagnostics
      │
      ├─► Step 5: Forest Plot
      │
      └─► Step 6: Spatial Visualisation
              • Environmental indicators
              • Demographic indicators
              • Respiratory outcomes
```

---

## Requirements

* Python 3.8+
* pandas
* numpy
* statsmodels
* matplotlib
* geopandas

Install dependencies:

```bash
pip install pandas numpy statsmodels matplotlib geopandas
```

Windows users may use:

```bash
py -m pip install pandas numpy statsmodels matplotlib geopandas
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

---

## Running Order

Run scripts in the following order:

```bash
python 1_prepare_model_data.py
python 2_model_type_comparison.py
python 3_model_development.py
python 4_final_analysis.py
python 5_forest_plot.py
python 6_create_maps.py
```

Windows users may replace `python` with `py`.

---

## Key Outputs

| File                             | Description                          |
| -------------------------------- | ------------------------------------ |
| model_dataset.csv                | Final modelling dataset              |
| model_type_comparison.csv        | Comparison of model families         |
| development_model_comparison.csv | Model development comparison         |
| lag_model_comparison.csv         | Lag assessment comparison            |
| final_model_comparison.csv       | Full versus reduced model comparison |
| final_model_coefficients.csv     | Final coefficient estimates          |
| final_model_irr.csv              | Incidence Rate Ratios                |
| final_model_diagnostics.csv      | Final model diagnostics              |
| forest_plot_final_model.png      | Forest plot of adjusted IRRs         |

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
