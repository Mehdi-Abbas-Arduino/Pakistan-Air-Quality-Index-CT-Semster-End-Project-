# Project Scope and Technical Plan

## 1. Project objective

Build a Pakistan-focused desktop application that combines historical air-quality records with Open-Meteo modelled data, provides transparent PM2.5-based US EPA AQI estimates, supports historical exploration and city comparison, and uses K-Means to discover patterns in validated pollution observations.

## 2. Included features

### Core
- City selection and overview.
- Open-Meteo Air Quality API integration.
- Existing CSV loading and validation.
- Validated storage of newly retrieved observations.
- 24-hour PM2.5 aggregation and US EPA 2024 PM2.5 AQI calculation.
- Pollutant summaries and historical charts.
- City comparison when source, time window, and units are comparable.
- K-Means clustering of suitable city-day observations.
- Clear source, timestamp, and measured/modelled labels.
- AQI methodology and pollutant guide.

### Supporting
- Pakistan city map.
- CSV export of selected analysis.
- Cluster visualizations and plain-language cluster summaries.
- Clear loading, stale-data, empty-data, and API-error states.

### Excluded from version one
- AQI forecasting.
- Deep learning.
- User accounts and authentication.
- Cloud database or cloud hosting.
- Mobile application.
- Automated pollution-source attribution.
- Medical diagnosis or personalized medical advice.
- Multiple competing ML algorithms.

## 3. AQI calculation contract

The initial calculation is a **PM2.5-based US EPA AQI estimate**, not a complete overall AQI and not an official Pakistan AQI reading.

Use the revised 2024 US EPA PM2.5 concentration breakpoints:

| PM2.5 concentration (µg/m³) | AQI range | Category |
|---:|---:|---|
| 0.0–9.0 | 0–50 | Good |
| 9.1–35.4 | 51–100 | Moderate |
| 35.5–55.4 | 101–150 | Unhealthy for Sensitive Groups |
| 55.5–125.4 | 151–200 | Unhealthy |
| 125.5–225.4 | 201–300 | Very Unhealthy |
| 225.5–325.4 | 301–400 | Hazardous |
| 325.5–500.4 | 401–500 | Hazardous |

The AQI input must be an appropriately calculated 24-hour average. Follow the EPA concentration truncation/rounding and AQI interpolation rules when implementing the calculation. Do not apply the 24-hour method directly to a single instantaneous reading.

A future full AQI implementation would need valid sub-indices for additional pollutants and their pollutant-specific averaging periods. The overall AQI is the highest applicable sub-index, not the arithmetic mean of pollutant indices.

## 4. Data-source strategy

### Open-Meteo
- Primary live/modelled data provider.
- Retrieve hourly pollutant series so a 24-hour PM2.5 average can be calculated when sufficient valid hourly values exist.
- Retain API location, source timestamp, retrieval timestamp, units, and modelled-data designation.
- Do not describe modelled CAMS values as station measurements.

### Existing historical CSV
- Preserve the original dataset.
- Audit its schema, date coverage, city coverage, units, missingness, duplicates, and provenance.
- Validate rows before using them for AQI calculations or clustering.
- Keep newly retrieved observations identifiable by source and retrieval time.

### Standard observation fields

At minimum, retain:
- city
- latitude and longitude
- timestamp
- retrieval timestamp
- source
- data type (measured or modelled)
- pollutant concentrations and units
- quality/validation status

Missing values remain missing; they must not be silently changed to zero.

## 5. K-Means plan

1. Prepare validated city-day observations.
2. Start with daily PM2.5 and PM10 averages.
3. Add other pollutant features only if the historical/live data has sufficient consistent coverage.
4. Handle missing values explicitly; do not train on incomplete feature rows without a documented strategy.
5. Standardize features with scikit-learn's StandardScaler.
6. Compare a small range of cluster counts (initially 2–5).
7. Use silhouette score as one diagnostic where sample size and cluster structure make it meaningful.
8. Inspect cluster centres and city/day membership.
9. Describe clusters from their observed pollutant profiles.
10. Set a fixed random_state for reproducibility.

Clusters are exploratory groupings. They are not health categories, official AQI labels, forecasts, or evidence of pollution sources. If the dataset is too small or too incomplete, collect more validated observations rather than inventing training data.

## 6. Target interface

Use CustomTkinter for a five-section desktop application:

1. Overview
2. Historical Analysis
3. Pakistan Explorer
4. ML Insights
5. AQI Guide

Keep data acquisition, validation, AQI calculation, analysis, clustering, visualization, and UI code in separate modules. UI code should call these modules rather than contain the calculation logic itself.

## 7. Target architecture

```text
Pakistan Air Quality Index/
├── Dataset/
├── Scripts/
│   ├── data/
│   │   ├── api_client.py
│   │   ├── data_loader.py
│   │   └── validation.py
│   ├── aqi/
│   │   └── aqi_calculator.py
│   ├── analysis/
│   │   └── exploratory_analysis.py
│   ├── ml/
│   │   └── clustering.py
│   ├── visualization/
│   │   ├── charts.py
│   │   └── map_drawer.py
│   ├── ui/
│   │   ├── dashboard.py
│   │   └── pages/
│   └── main.py
├── Tests/
├── docs/
├── README.md
├── requirements.txt
└── .gitignore
```

This is the target structure, not a claim that all modules already exist. Existing working modules should be migrated incrementally and tested.

## 8. Implementation phases

1. Audit the current repository, tests, and historical CSV.
2. Standardize the data schema and validation.
3. Implement and test 24-hour PM2.5 aggregation and 2024 AQI breakpoints.
4. Improve the Open-Meteo client to retrieve the hourly data required by the averaging method.
5. Build historical analysis and city comparison.
6. Implement and evaluate K-Means.
7. Migrate the interface to CustomTkinter and build the five sections.
8. Integrate, test, document, and prepare a demonstration.

## 9. Definition of done

- Historical and live data have traceable source metadata.
- Missing, duplicate, stale, and invalid records are handled explicitly.
- PM2.5 AQI is only calculated from a valid 24-hour average.
- The UI labels the result as a PM2.5-based US EPA estimate.
- Historical charts and city comparisons use compatible observations.
- K-Means is reproducible and its clusters are explained from actual cluster centres.
- Automated tests cover calculations, validation, and clustering preparation.
- README explains the system, data sources, methodology, and limitations.
