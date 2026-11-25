# City-wise Annual AQI Trend and Forecast

## Purpose

This experiment plots each city's historical annual mean daily PM2.5-based US EPA AQI estimate and extends its trend using a separate Linear Regression model for each city.

It is a statistical trend projection, not an official AQI forecast, a causal model, or a guarantee of future air quality.

## Method

1. Read hourly observations with `city`, `timestamp`, and `pm2_5` columns.
2. Remove invalid PM2.5 values and duplicate city/timestamp rows.
3. Group observations by city and calendar day.
4. Keep a city-day only when it has at least 18 valid hourly PM2.5 readings.
5. Calculate the daily mean PM2.5 and convert it to a 2024 US EPA PM2.5-based AQI estimate using the project's existing calculator.
6. Average the valid daily AQI estimates within each city and calendar year.
7. Fit a separate Linear Regression model to each city's annual values.
8. Project five future years by default. Cities with fewer than three historical annual observations remain visible in the historical dataset but are not forecast.
9. Bound projected values to the AQI scale of 0-500.

The yearly target is the mean of daily AQI estimates. The code does not average annual PM2.5 and then convert that value to AQI.

## Run

From the project root:

```bash
cd "Pakistan Air Quality Index/Scripts"
python -m ml.aqi_yearly_forecast --show
```

Choose a different forecast horizon:

```bash
python -m ml.aqi_yearly_forecast --years 5 --show
```

Provide a custom CSV or output directory:

```bash
python -m ml.aqi_yearly_forecast --csv "../Dataset/pakistan_air_quality_final_clean_v2.csv" --output-dir "../Outputs/aqi_yearly_forecast" --years 5 --show
```

## Outputs

The default output directory is `Pakistan Air Quality Index/Outputs/aqi_yearly_forecast`.

- `city_yearly_aqi_forecast.png`: city-coloured historical lines and dashed projections.
- `yearly_aqi_and_forecast.csv`: historical and projected city-year values, with a `record_type` column.
- `city_forecast_metrics.csv`: number of historical years, fitted slope, intercept, and last-year holdout absolute error.

A positive slope means the model's fitted annual AQI trend is increasing; a negative slope means it is decreasing. Higher AQI indicates worse air quality.

## Limitations

- A linear model assumes the past trend continues. It cannot anticipate policy changes, unusual weather, emissions changes, or sudden events.
- Extrapolation becomes less dependable farther beyond the observed years.
- The last-year holdout error is a small-sample diagnostic, not proof that future predictions will be accurate.
- The dataset's source, coverage, and measured-versus-modelled status should be reviewed before interpreting city comparisons.
- The project target is a PM2.5-based US EPA AQI estimate, not the official overall AQI for Pakistan.
- The module does not create missing historical observations or combine pollutant sub-indices.
