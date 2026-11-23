# Experimental supervised AQI estimation

## Purpose

This experiment compares supervised regression models that estimate the project's **24-hour PM2.5-based US EPA AQI estimate** from other pollutant and weather measurements. It is an offline research/analysis module and is not wired into the production dashboard yet.

It is **not an AQI forecast**. It estimates an AQI label for a city-day represented by the input observations. The existing EPA calculation remains the primary, transparent method used to calculate AQI.

## Avoiding target leakage

The target is created from the daily mean of hourly pm2_5 values using the revised 2024 US EPA PM2.5 breakpoints in Scripts/aqi_calculator.py.

pm2_5 is deliberately excluded from the model's input features because it directly determines the target AQI. Using it as an input would let the model learn a near-direct transformation rather than estimate AQI from other measurements.

The model uses whichever of these columns are present and contain data:

- pm10
- carbon_monoxide
- nitrogen_dioxide
- sulphur_dioxide
- ozone
- dust
- temperature
- humidity
- precipitation
- wind_speed
- wind_direction
- pressure

Features are daily means for the same city and date. Missing feature values are imputed inside each training pipeline using the training-set median. Missing values are not converted to zero.

## Data preparation

1. Read the historical hourly CSV.
2. Parse timestamps and numeric columns.
3. Group observations by city and calendar date.
4. Keep a city-day target only when at least 18 of the 24 hourly PM2.5 values are available.
5. Calculate the daily PM2.5 mean and convert it to a 2024 US EPA PM2.5 AQI estimate.
6. Aggregate available non-PM2.5 predictors to daily means.
7. Exclude city-days without a valid target or with no available predictors.

The 18-hour threshold is a minimum data-completeness rule for a 24-hour average. It does not turn a partial-day mean into a measured full-day value; interpret the result as an estimate based on the available hourly coverage.

## Models compared

| Model | Purpose |
|---|---|
| Linear Regression | Straight-line baseline |
| Polynomial Regression (degree 2) | Adds squared and interaction terms to capture curved relationships |
| Random Forest Regression | Nonlinear tree-ensemble comparison |

The polynomial model is still a linear regression estimator operating on expanded polynomial features. Random Forest is a separate comparison model.

## Evaluation design

The split is chronological, not random: earlier dates are used for training and the latest 20% of distinct dates are held out for testing. This reduces the risk of training on later observations and testing on earlier ones. All cities from a date stay on the same side of the split.

Reported metrics:

- **MAE:** average absolute AQI estimation error, in AQI points.
- **RMSE:** gives larger errors more influence, in AQI points.
- **R²:** proportion of test-target variation explained by the model; it can be negative when predictions are worse than a constant-mean baseline.

The test metrics are an initial time-based benchmark, not proof that the model generalizes to every Pakistani city or future period. City coverage, source consistency, temporal drift, and dataset provenance should be reviewed before making broader claims.

## Visualizations

The experiment saves:

- actual_vs_predicted.png: held-out actual AQI against each model's predictions.
- linear_vs_nonlinear.png: observed daily AQI against one pollutant/weather feature, with straight-line and quadratic trend curves.
- model_metrics.csv: MAE, RMSE, and R² for each model.

The relationship chart is descriptive and bivariate. It is not the same thing as the multivariable polynomial model.

## Run it

Install the repository requirements, then from the Pakistan Air Quality Index/Scripts directory run:

~~~bash
python -m ml.aqi_regression --show
~~~

To choose a different input file or output directory:

~~~bash
python -m ml.aqi_regression --csv "../Dataset/pakistan_air_quality_final_clean_v2.csv" --output-dir "../Outputs/aqi_regression" --show
~~~

The default input is the repository's historical CSV. The output directory is created locally when the experiment runs. No synthetic training data is used by the experiment.

## Limitations

- The target is derived from PM2.5 using the EPA method, so the model approximates an existing calculation rather than discovering an independent AQI formula.
- The model does not predict future pollution or AQI.
- AQI labels are PM2.5-based estimates, not a complete multi-pollutant AQI and not an official Pakistan AQI reading.
- Modelled/reanalysis inputs and station-measured inputs should not be mixed without preserving their source and data-type metadata.
- The experiment is separate from the dashboard's K-Means clustering feature and is not currently exposed in the GUI.
- No performance figures should be reported until the script has been run against the actual project dataset and the resulting metrics have been reviewed.
