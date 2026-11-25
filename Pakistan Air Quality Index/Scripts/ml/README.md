# Machine Learning Scripts

This folder contains two separate experiments. They answer different questions, so choose the script that matches the result you want.

| File | Purpose | Main question |
|---|---|---|
| `aqi_regression.py` | Trains and compares supervised regression models using daily pollutant and weather features. | Can the available non-PM2.5 features estimate a day's PM2.5-based AQI? |
| `aqi_yearly_forecast.py` | Builds annual city-level AQI trends and fits one linear trend model per city. | If each city's historical annual trend continued, what might its AQI look like over the next few years? |

These are experiments, not official air-quality forecasts. Both estimate a **PM2.5-based US EPA AQI value**, not the complete official multi-pollutant AQI for Pakistan.

## 1. Set up the project

Open PowerShell in the repository's root directory, the folder containing `README.md` and `requirements.txt`.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can still use the environment's Python executable directly, or follow your system's approved PowerShell execution-policy guidance.

Install the project's dependencies:

```powershell
python -m pip install -r requirements.txt
```

The ML scripts use:
- **Pandas:** reading, cleaning, grouping, and exporting tabular data.
- **NumPy:** numerical operations and arrays.
- **Matplotlib:** charts and saved plots.
- **Scikit-learn:** regression models, preprocessing pipelines, and evaluation metrics.

## 2. Run a model

First move into the `Scripts` directory:

```powershell
cd "Pakistan Air Quality Index\Scripts"
```

Run the supervised AQI estimation experiment:

```powershell
python -m ml.aqi_regression --show
```

Run the city-wise annual trend and projection:

```powershell
python -m ml.aqi_yearly_forecast --years 10 --show
```

**Important:** Run these module commands from `Pakistan Air Quality Index/Scripts`. The `ml` package is inside that directory. Running `python -m ml...` from the repository root causes `ModuleNotFoundError: No module named 'ml'`.

The dataset path is configured inside each script and points by default to:

```text
Pakistan Air Quality Index/Dataset/pakistan_air_quality_final_clean_v2.csv
```

## 3. Script guide: `aqi_regression.py`

### Purpose

This script compares three supervised regression approaches for estimating daily PM2.5-based AQI from other available pollutant and weather variables.

It does **not** predict future dates. It estimates AQI for held-out historical days.

### How it works

1. Reads hourly records and checks for the required `city`, `timestamp`, and `pm2_5` columns.
2. Removes duplicate city/timestamp records and invalid timestamps.
3. Groups hourly observations into city-day records.
4. Keeps a daily target only when at least 18 valid hourly PM2.5 readings are available.
5. Converts the daily mean PM2.5 concentration into an AQI target using `aqi_calculator.py`.
6. Builds daily predictor averages from available pollutant and weather columns.
7. Excludes PM2.5 from the predictor features because PM2.5 is used to create the target. Including it as an input would cause target leakage.
8. Splits the data chronologically, using earlier dates for training and later dates for testing.
9. Trains and compares three pipelines:
   - **Linear Regression:** a straight-line relationship between features and AQI.
   - **Polynomial Regression (degree 2):** adds squared and interaction terms to represent some curved relationships.
   - **Random Forest Regression:** combines decision trees to model more complex patterns.
10. Evaluates predictions using MAE, RMSE, and R².

### Outputs

Saved by default to `Pakistan Air Quality Index/Outputs/aqi_regression/`:

| File | What it contains |
|---|---|
| `model_metrics.csv` | MAE, RMSE, and R² for each model. |
| `actual_vs_predicted.png` | Compares held-out actual AQI values with each model's predictions. Points closer to the dashed perfect-prediction line indicate closer estimates. |
| `linear_vs_nonlinear.png` | Shows observed values against a selected feature, with linear and quadratic trend curves. |

### Run options

Display the charts:

```powershell
python -m ml.aqi_regression --show
```

Run without opening chart windows:

```powershell
python -m ml.aqi_regression
```

Use another CSV or output directory:

```powershell
python -m ml.aqi_regression --csv "..\Dataset\my_data.csv" --output-dir "..\Outputs\my_regression_run" --show
```

## 4. Script guide: `aqi_yearly_forecast.py`

### Purpose

This script summarizes historical annual AQI values for each city and extends each city's trend into future years using a separate Linear Regression model.

It is the script to use when you want **one historical and projected line per city**.

### How it works

1. Reads hourly city-level PM2.5 observations.
2. Removes invalid values and duplicate city/timestamp records.
3. Groups the observations by city and calendar day.
4. Keeps city-days with at least 18 valid hourly PM2.5 readings.
5. Calculates each day's mean PM2.5 and converts it to a PM2.5-based AQI estimate.
6. Calculates each city's annual value as the mean of its valid daily AQI estimates for that year.
7. Fits an independent Linear Regression model for each city with at least three distinct historical years.
8. Projects the requested number of future years. Projections are bounded to the 0-500 AQI scale.
9. Calculates a simple last-year holdout error as a diagnostic.

The annual value is the **mean of daily AQI estimates**. It is not calculated by averaging annual PM2.5 first and converting that annual concentration into AQI.

### Outputs

Saved by default to `Pakistan Air Quality Index/Outputs/aqi_yearly_forecast/`:

| File | What it contains |
|---|---|
| `city_yearly_aqi_forecast.png` | A combined chart. Each city has its own colour; solid lines show historical values and dashed lines show projections. |
| `yearly_aqi_and_forecast.csv` | Historical and projected city-year values. The `record_type` column identifies each row as `historical` or `forecast`. |
| `city_forecast_metrics.csv` | Per-city history length, first and last historical year, fitted slope, intercept, and last-year holdout diagnostic values. |

### Run options

Default five-year projection:

```powershell
python -m ml.aqi_yearly_forecast --show
```

Ten-year projection:

```powershell
python -m ml.aqi_yearly_forecast --years 10 --show
```

Three-year projection:

```powershell
python -m ml.aqi_yearly_forecast --years 3 --show
```

Use another CSV or output directory:

```powershell
python -m ml.aqi_yearly_forecast --csv "..\Dataset\my_data.csv" --output-dir "..\Outputs\my_forecast_run" --years 5 --show
```

A city with fewer than three distinct historical years will still appear in the historical CSV and chart, but it will not receive a projection.

## 5. Shared dependencies and supporting files

| File or folder | Purpose |
|---|---|
| `Scripts/ml/aqi_regression.py` | Trains and evaluates the daily AQI estimation models. |
| `Scripts/ml/aqi_yearly_forecast.py` | Aggregates annual city AQI and projects future annual trends. |
| `Scripts/aqi_calculator.py` | Converts a suitable 24-hour PM2.5 average into a 2024 US EPA PM2.5 AQI estimate. Both ML scripts import this function to create their target values. |
| `Dataset/pakistan_air_quality_final_clean_v2.csv` | Default hourly dataset used by both scripts. |
| `requirements.txt` | Lists the Python packages required by the project, including the ML dependencies. |
| `Tests/` | Contains project tests. |

The scripts expect the dataset to contain these required columns:

| Column | Meaning |
|---|---|
| `city` | City name associated with the observation. |
| `timestamp` | Date and time of the observation. |
| `pm2_5` | PM2.5 concentration, normally in µg/m³. |

The regression experiment can also use optional numeric columns when present, such as `pm10`, `carbon_monoxide`, `nitrogen_dioxide`, `sulphur_dioxide`, `ozone`, `temperature`, `humidity`, `precipitation`, `wind_speed`, `wind_direction`, and `pressure`.

## 6. Understanding the results responsibly

- **AQI direction:** higher AQI means worse air quality.
- **MAE:** average absolute prediction error, in AQI points. Lower is generally better.
- **RMSE:** gives larger errors more weight than MAE. Lower is generally better.
- **R²:** describes how much variation in the test targets is explained by the model. It can be negative when predictions perform worse than a simple mean baseline.
- **Trend slope:** in the annual model, a positive slope indicates an increasing fitted AQI trend; a negative slope indicates a decreasing fitted trend.

A model score is not proof that the model will perform equally well on future data. Results depend on data quality, coverage, city representation, and whether the historical relationships continue.

### Important limitations

1. These scripts estimate **PM2.5-based US EPA AQI**, not the official overall multi-pollutant AQI for Pakistan.
2. The annual model is a simple linear extrapolation. It cannot anticipate policy changes, unusual weather, new emission sources, or sudden events.
3. Long-range projections become less reliable as they extend farther beyond the observed years.
4. The regression model estimates historical daily AQI from other available features; it is not a future-time forecasting model.
5. The last-year holdout check is a limited diagnostic, especially when only a few years of data are available.
6. Missing data, inconsistent units, or mixing modelled estimates with station measurements can distort results. Check dataset provenance and coverage before drawing conclusions.

For the annual model's methodology, see [AQI_YEARLY_CITY_FORECAST.md](../../../docs/AQI_YEARLY_CITY_FORECAST.md).
