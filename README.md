# Pakistan Air Quality Index

A Python desktop application for exploring air-quality information across selected Pakistani cities. The project combines a historical CSV dataset with modelled air-quality data from Open-Meteo, calculates clearly labelled PM2.5-based US EPA AQI estimates, visualizes historical patterns, and uses machine learning experiments to explore AQI estimation and annual city trends.

> **Project status:** Scope and architecture are being finalized. The current application is an early Tkinter implementation. The CustomTkinter interface, validated 24-hour AQI pipeline, historical analysis screens, and K-Means insights are planned development work, not features that should be assumed complete.

## Agreed project decisions

| Area | Decision |
|---|---|
| Application | Python desktop application |
| Interface | CustomTkinter |
| Primary live data provider | Open-Meteo Air Quality API |
| Historical data | Existing CSV plus validated new observations |
| AQI method | US EPA 2024 PM2.5 AQI methodology |
| Machine learning | Regression experiments and exploratory analysis |
| Data processing | Pandas and NumPy |
| Machine learning library | Scikit-learn |
| Charts | Matplotlib |
| Initial storage | CSV files |

## Main application sections

1. **Overview:** selected city, latest available pollutant information, PM2.5 AQI estimate, data source, and timestamp.
2. **Historical Analysis:** pollutant trends, daily summaries, and time-based comparisons.
3. **Pakistan Explorer:** city-level comparisons and a geographic view where reliable coordinates and data are available.
4. **ML Insights:** model estimates, evaluation metrics, annual city trends, and projections.
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

## Machine-learning scripts

The `Pakistan Air Quality Index/Scripts/ml/` folder currently contains two independent experiments:

| File | Purpose |
|---|---|
| `aqi_regression.py` | Trains and compares Linear Regression, Polynomial Regression, and Random Forest models to estimate daily PM2.5-based AQI from other available pollutant and weather features. This is an estimation experiment, not a future-time forecast. |
| `aqi_yearly_forecast.py` | Calculates historical annual mean daily PM2.5-based AQI for each city and fits a separate Linear Regression trend to project future annual values. |

Both scripts use `aqi_calculator.py` to create PM2.5-based AQI targets. They do not calculate the complete official multi-pollutant AQI for Pakistan.

### Setup

Use Python 3.10 or newer. From the repository root, create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Run the ML scripts

The commands below must be run from the `Pakistan Air Quality Index/Scripts` directory:

```powershell
cd "Pakistan Air Quality Index\Scripts"
```

Run the daily AQI estimation experiment:

```powershell
python -m ml.aqi_regression --show
```

Run the city-wise annual AQI trend and five-year projection:

```powershell
python -m ml.aqi_yearly_forecast --show
```

Change the annual projection horizon:

```powershell
python -m ml.aqi_yearly_forecast --years 10 --show
```

The regression outputs are saved under `Outputs/aqi_regression/`. The annual forecast outputs are saved under `Outputs/aqi_yearly_forecast/`.

**Important:** Do not run `python -m ml...` from the repository root. The `ml` package is inside `Pakistan Air Quality Index/Scripts`, so running from the wrong directory causes `ModuleNotFoundError: No module named 'ml'`.

For each script's workflow, outputs, metrics, assumptions, CLI options, and limitations, read the [Machine Learning Guide](Pakistan%20Air%20Quality%20Index/Scripts/ml/README.md).

## Run the desktop application

From the repository root, install dependencies as shown above. Then:

```powershell
cd "Pakistan Air Quality Index/Scripts"
python main.py
```

## Run tests

From the repository root:

```powershell
python -m pytest
```

## Repository layout

```text
.
├── requirements.txt
├── docs/
│   ├── PROJECT_SCOPE.md
│   └── AQI_YEARLY_CITY_FORECAST.md
└── Pakistan Air Quality Index/
    ├── Dataset/
    │   └── pakistan_air_quality_final_clean_v2.csv
    ├── Outputs/
    │   ├── aqi_regression/          # Created when regression script runs
    │   └── aqi_yearly_forecast/     # Created when annual forecast runs
    ├── Scripts/
    │   ├── ml/
    │   │   ├── README.md
    │   │   ├── aqi_regression.py
    │   │   └── aqi_yearly_forecast.py
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
