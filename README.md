# Air Temperature Syndromic Surveillance (ATS)

A repository for analysing the relationship between air quality, meteorological conditions, land use, demographic vulnerability, and respiratory syndromes.

The project is organised into two main components:

```text
ATS/
│
├── data_processing/
│   ├── ...
│   └── README_DataProcessing.md
│
├── Model/
│   ├── ...
│   └── README_Model.md
│
└── README.md
```

---

## Repository Structure

### `data_processing/`

Contains the complete data preparation workflow used to build the final environment–health panel dataset.

Main tasks include:

- Air quality data processing (PM10, O₃)
- Meteorological data aggregation
- Spatial joins and polygon-level aggregation
- Demographic and land-use integration
- Creation of the final modelling dataset

Detailed documentation:

➡️ See `data_processing/README_DataProcessing.md`

---

### `Model/`

Contains the statistical modelling and risk assessment pipeline.

Main components include:

1. Data preparation for modelling
2. Poisson and Negative Binomial model comparison
3. Model development and variable selection
4. Temporal and spatial validation
5. Risk index generation
6. Forest plots and spatial visualisation

Detailed documentation:

➡️ See `Model/README_Model.md`

---

## Workflow

```text
Raw Environmental Data
            │
            ▼
data_processing/
            │
            ▼
Final Environment–Health Panel
            │
            ▼
Model/
            │
            ├─ Statistical Modelling
            ├─ Validation
            ├─ Risk Assessment
            └─ Spatial Visualisation
```

---

## Outputs

The repository produces:

- Integrated environment–health datasets
- Statistical model results
- Incidence Rate Ratios (IRRs)
- Temporal validation metrics
- Spatial diagnostics
- Calibrated respiratory risk indices
- Publication-ready figures and maps

---

## Requirements

Python 3.8+

Core packages:

```bash
pip install pandas numpy statsmodels matplotlib geopandas libpysal esda scikit-learn
```

---

## Documentation

- `data_processing/README_DataProcessing.md` — data preparation workflow
- `Model/README_Model.md` — modelling and validation workflow

Both READMEs provide detailed descriptions of scripts, inputs, outputs, and execution order.
