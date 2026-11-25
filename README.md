# Pakistan Air Quality Index

A Python desktop application for exploring air-quality information across selected Pakistani cities. The project combines a historical CSV dataset with modelled air-quality data from Open-Meteo, calculates clearly labelled PM2.5-based US EPA AQI estimates, visualizes historical patterns, and uses K-Means clustering to explore similarities between city-day pollution profiles.

> **Project status:** Scope and architecture are being finalized. The current application is an early Tkinter implementation. The CustomTkinter interface, validated 24-hour AQI pipeline, historical analysis screens, and K-Means insights are planned development work, not features that should be assumed complete.

## Agreed project decisions

| Area | Decision |
|---|---|
| Application | Python desktop application |
| Interface | CustomTkinter |
| Primary live data provider | Open-Meteo Air Quality API |
| Historical data | Existing CSV plus validated new observations |
| AQI method | US EPA 2024 PM2.5 AQI methodology |
| Machine learning | K-Means clustering |
| Data processing | Pandas and NumPy |
| Machine learning library | Scikit-learn |
| Charts | Matplotlib |
| Initial storage | CSV files |

## Main application sections

1. **Overview:** selected city, latest available pollutant information, PM2.5 AQI estimate, data source, and timestamp.
2. **Historical Analysis:** pollutant trends, daily summaries, and time-based comparisons.
3. **Pakistan Explorer:** city-level comparisons and a geographic view where reliable coordinates and data are available.
4. **ML Insights:** K-Means cluster summaries, cluster centres, and visual comparisons.
5. **AQI Guide:** AQI categories, pollutant explanations, calculation method, and limitations.

## AQI interpretation and limitations

The first implementation target is a **24-hour-average PM2.5-based US EPA AQI estimate** using the revised 2024 PM2.5 breakpoints. A single instantaneous PM2.5 value must not be presented as a 24-hour AQI.

This project must not describe a PM2.5-only result as the official overall AQI for Pakistan. A complete multi-pollutant AQI requires pollutant-specific averaging periods and valid sub-indices; the overall index is determined by the highest applicable pollutant sub-index.

Open-Meteo CAMS global values are modelled estimates, not direct measurements from a local monitoring station. The interface should identify the source, observation timestamp, retrieval timestamp, and whether a value is modelled or measured.

## Data quality principles

- Preserve source attribution for every observation.
- Keep raw inputs separate from cleaned/processed data.
- Do not replace missing pollutant values with zero.
- Detect duplicate timestamps and invalid numeric values.
- Keep units consistent and explicit.
- Mark stale data and avoid misleading city rankings.
- Do not combine modelled and station-measured observations without retaining their distinct data types.

## Machine-learning scope

K-Means will explore patterns in validated city-day pollution profiles. Candidate features include daily PM2.5 and PM10 averages; other pollutants may be included only when coverage and units are sufficiently consistent.

The workflow will scale numerical features, evaluate a small range of cluster counts, inspect cluster centres, and describe clusters based on observed feature values. Cluster labels are exploratory descriptions, not official AQI or health categories. The model is not an AQI forecasting system and does not identify pollution sources.

## Development setup

Use Python 3.10 or newer. From the project directory:

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the existing application from the `Scripts` directory:

```bash
cd "Pakistan Air Quality Index/Scripts"
python main.py
```

Run the supervised regression experiment from the `Scripts` directory:\n\n```bash\npython -m ml.aqi_regression --show\n```\n\nRun the city-wise annual AQI trend and five-year projection from the `Scripts` directory:

```bash
python -m ml.aqi_yearly_forecast --show
```

Change the projection horizon with `--years 3`, `--years 5`, or another positive number. The output graph and CSV files are saved under `Outputs/aqi_yearly_forecast`. See [docs/AQI_YEARLY_CITY_FORECAST.md](docs/AQI_YEARLY_CITY_FORECAST.md) for the methodology and limitations.

Run the existing test suite from the project root:

```bash
python -m pytest
```

## Repository layout

```text
Pakistan Air Quality Index/
├── Dataset/
│   └── pakistan_air_quality_final_clean_v2.csv
├── Scripts/
│   ├── aqi_calculator.py
│   ├── data_loader.py
│   ├── gui.py
│   ├── live_data.py
│   ├── main.py
│   ├── map_drawer.py
│   ├── quiz.py
│   ├── recursion_tools.py
│   └── validation.py
└── Tests/
```

The target modular architecture and implementation phases are documented in [docs/PROJECT_SCOPE.md](docs/PROJECT_SCOPE.md).

## Data provider

- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)

## Team

- Mehdi Abbas
- Bilal Mahmoodi
