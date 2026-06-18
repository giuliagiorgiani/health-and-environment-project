# Health and Environment Data Processing Pipeline

A Python workflow for creating a polygon-level environmental and respiratory health panel for Lombardy, Italy (2022–2026) by integrating environmental monitoring data, land-use characteristics, demographic information, and respiratory health outcomes.

---

## Overview

```text
Environmental Monitoring Data
Population Data
Land-Use Data
Health Records
      │
      ├─► Step 1: Temperature Polygon Preparation
      │       • Voronoi polygons
      │       • ATS population weights
      │       • Age-sex structure
      │
      ├─► Step 2: Temperature Data Download
      │
      ├─► Step 3: Air Pollution Data Download
      │       • PM10
      │       • O3
      │
      ├─► Step 4–6: Environmental Processing
      │       • Temperature indicators
      │       • PM10 indicators
      │       • O3 indicators
      │
      ├─► Step 7: Land-Use Characterisation
      │
      ├─► Step 8: Pollutant Assignment
      │       • PM10 station weights
      │       • O3 station weights
      │
      ├─► Step 9: Environmental Panel Creation
      │
      ├─► Step 10: Health–Environment Integration
      │
      └─► Step 11: Vulnerability Indicators
              • Population
              • Age structure
              • Sex composition
```

---

## Requirements

* Python 3.8+
* pandas
* numpy
* geopandas
* shapely
* scikit-learn
* requests

Install dependencies:

```bash
pip install pandas numpy geopandas shapely scikit-learn requests
```

Windows users may use:

```bash
py -m pip install pandas numpy geopandas shapely scikit-learn requests
```

---

## Input Data

The workflow requires:

```text
Temperature monitoring stations
PM10 monitoring stations
O3 monitoring stations
Temperature observations
PM10 observations
O3 observations
ATS boundaries
DUSAF land-use polygons
Population data
Age-sex population data
Respiratory health records
```

---

# Scripts

## Step 1 — Temperature Polygon Preparation

**File:** `01_prepare_temperature_lists.py`

Purpose:

* Create Voronoi polygons around temperature stations
* Derive ATS population weights
* Derive demographic structure indicators

Outputs:

```text
temperature_voronoi.shp
temperature_ats_weights.csv
temperature_age_structure.csv
```

---

## Step 2 — Temperature Data Download

**File:** `02_download_temperature_data.py`

Purpose:

* Download hourly temperature observations from Lombardia Open Data
* Retrieve all stations included in the study

Outputs:

```text
temperature_YYYY.csv
```

---

## Step 3 — Air Pollution Data Download

**File:** `03_download_environmental_data.py`

Purpose:

* Download PM10 observations
* Download O3 observations
* Retrieve all monitoring stations included in the study

Outputs:

```text
pm10_YYYY.csv
o3_YYYY.csv
```

---

## Step 4 — Temperature Processing

**File:** `04_clean_and_process_temperature.py`

Purpose:

* Clean temperature observations
* Remove invalid records
* Calculate daily indicators
* Aggregate weekly temperature metrics

Outputs:

```text
weekly_temperature_station_YYYY.csv
```

---

## Step 5 — PM10 Processing

**File:** `05_clean_and_process_pm10.py`

Purpose:

* Clean PM10 observations
* Interpolate missing values
* Calculate exceedance indicators
* Aggregate weekly PM10 metrics

Outputs:

```text
weekly_pm10_station_YYYY.csv
```

---

## Step 6 — O3 Processing

**File:** `06_clean_and_process_o3.py`

Purpose:

* Clean O3 observations
* Calculate 8-hour running averages
* Calculate exceedance indicators
* Aggregate weekly O3 metrics

Outputs:

```text
weekly_o3_station_YYYY.csv
```

---

## Step 7 — Land-Use Characterisation

**File:** `07_process_land_use_master_polygons.py`

Purpose:

* Overlay DUSAF land-use data with temperature polygons
* Calculate land-use composition within each polygon
* Derive land-use percentages

Outputs:

```text
polygon_landuse_summary.csv
```

---

## Step 8 — Pollutant Assignment

**File:** `08_assign_pollutant_stations_to_polygon.py`

Purpose:

* Identify the three nearest PM10 stations for each polygon
* Identify the three nearest O3 stations for each polygon
* Calculate inverse-distance weights
* Create pollutant assignment tables

Outputs:

```text
polygon_pm10_weights.csv
polygon_o3_weights.csv
master_environment_polygons.shp
```

---

## Step 9 — Environmental Panel Creation

**File:** `09_Environmental_master_panel.py`

Purpose:

* Combine temperature, PM10, and O3 indicators
* Apply inverse-distance weighted pollutant exposures
* Create weekly polygon-level environmental exposures

Outputs:

```text
FINAL_COMPLETE_master_environment_panel_2022_2026.csv
```

---

## Step 10 — Health–Environment Integration

**File:** `10_Merging_health_and_env_panel.py`

Purpose:

* Merge respiratory health outcomes with environmental exposures
* Allocate ATS-level health records to polygons using population weights
* Create a polygon-level environment-health panel

Outputs:

```text
FINAL_polygon_environment_health_panel_2022_2026.csv
```

---

## Step 11 — Vulnerability Indicators

**File:** `11_Pnael_full_with_Vulnerability.py`

Purpose:

* Merge population information
* Merge age structure indicators
* Merge sex composition indicators
* Create demographic vulnerability variables

Outputs:

```text
FINAL_polygon_environment_health_panel_population_age.csv
```

---

## Running Order

Run scripts in the following order:

```bash
python 01_prepare_temperature_lists.py
python 02_download_temperature_data.py
python 03_download_environmental_data.py
python 04_clean_and_process_temperature.py
python 05_clean_and_process_pm10.py
python 06_clean_and_process_o3.py
python 07_process_land_use_master_polygons.py
python 08_assign_pollutant_stations_to_polygon.py
python 09_Environmental_master_panel.py
python 10_Merging_health_and_env_panel.py
python 11_Pnael_full_with_Vulnerability.py
```

Windows users may replace `python` with `py`.

---

## Key Outputs

| File                                                      | Description                     |
| --------------------------------------------------------- | ------------------------------- |
| temperature_voronoi.shp                                   | Temperature exposure polygons   |
| temperature_ats_weights.csv                               | ATS population weights          |
| temperature_age_structure.csv                             | Age-sex structure indicators    |
| polygon_pm10_weights.csv                                  | PM10 station assignment weights |
| polygon_o3_weights.csv                                    | O3 station assignment weights   |
| polygon_landuse_summary.csv                               | Land-use composition by polygon |
| FINAL_COMPLETE_master_environment_panel_2022_2026.csv     | Environmental exposure panel    |
| FINAL_polygon_environment_health_panel_2022_2026.csv      | Environment-health panel        |
| FINAL_polygon_environment_health_panel_population_age.csv | Final analysis dataset          |

---

## Notes

* Environmental exposures are estimated at the polygon-week level.
* PM10 and O3 exposures are assigned using inverse-distance weighted averages from the three nearest monitoring stations.
* Land-use indicators are derived from DUSAF land-cover data.
* ATS-level health outcomes are allocated to polygons using population-based weights.
* Population, age structure, and sex composition indicators are incorporated to support vulnerability assessment.
* The final output dataset combines environmental, demographic, land-use, and respiratory health information for all study polygons between 2022 and 2026.

## Data Sources

### Population Data

Population counts and demographic indicators were derived from WorldPop gridded population datasets (100 m spatial resolution), including age- and sex-specific population estimates. WorldPop provides open-access, high-resolution population data developed using peer-reviewed spatial demographic methods.

Source:

[WorldPop Data Portal](https://www.worldpop.org)

---

### Land-Use Data

Land-use indicators were derived from the DUSAF 6.0 (Destinazione d'Uso dei Suoli Agricoli e Forestali) database produced by Regione Lombardia. DUSAF provides detailed land-cover and land-use information for the Lombardy region and was used to calculate polygon-level land-use composition.

Source:

[DUSAF 6.0 – Regione Lombardia Open Data](https://www.dati.lombardia.it/browse?sortBy=last_modified&page=1&pageSize=20)
---
