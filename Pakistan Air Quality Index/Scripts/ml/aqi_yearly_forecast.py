"""City-wise historical AQI trends and short-term annual projections.

The target is the annual mean of valid daily PM2.5-based US EPA AQI
estimates. This is a trend projection, not an official AQI forecast.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from aqi_calculator import calculate_pm25_aqi


PROJECT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_DIR / "Dataset" / "pakistan_air_quality_final_clean_v2.csv"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "Outputs" / "aqi_yearly_forecast"
DEFAULT_FORECAST_YEARS = 5
MIN_VALID_HOURS = 18
MIN_TRAINING_YEARS = 3
AQI_MIN = 0.0
AQI_MAX = 500.0


def prepare_annual_aqi(
    data: pd.DataFrame,
    min_valid_hours: int = MIN_VALID_HOURS,
) -> pd.DataFrame:
    """Return one annual mean of daily AQI per city.

    Each daily AQI is calculated from that city's mean hourly PM2.5. A
    city-day is accepted only when it has at least min_valid_hours valid,
    unique hourly PM2.5 observations. Annual values are the mean of those
    daily AQI values, not an AQI recalculated from annual PM2.5.
    """
    required = {"city", "timestamp", "pm2_5"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(sorted(missing))}"
        )
    if not 1 <= min_valid_hours <= 24:
        raise ValueError("min_valid_hours must be between 1 and 24.")

    frame = data.loc[:, ["city", "timestamp", "pm2_5"]].copy()
    frame["city"] = frame["city"].astype("string").str.strip()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    frame["pm2_5"] = pd.to_numeric(frame["pm2_5"], errors="coerce")
    frame["pm2_5"] = frame["pm2_5"].where(np.isfinite(frame["pm2_5"]))
    frame = frame.dropna(subset=["city", "timestamp"])
    frame = frame[frame["city"] != ""]
    frame = frame[frame["pm2_5"].between(0, 500.4, inclusive="both")]
    frame = frame.sort_values("timestamp").drop_duplicates(
        subset=["city", "timestamp"], keep="last"
    )

    if frame.empty:
        raise ValueError("No valid city, timestamp, and PM2.5 observations were found.")

    frame["date"] = frame["timestamp"].dt.date
    daily = (
        frame.groupby(["city", "date"], sort=True)["pm2_5"]
        .agg(pm25_mean="mean", valid_hours="count")
        .reset_index()
    )
    daily = daily[daily["valid_hours"] >= min_valid_hours].copy()
    daily["aqi"] = daily["pm25_mean"].map(calculate_pm25_aqi)
    daily = daily.dropna(subset=["aqi"])
    if daily.empty:
        raise ValueError(
            "No valid city-days remain. Check hourly coverage and PM2.5 values."
        )

    daily["year"] = pd.to_datetime(daily["date"]).dt.year
    annual = (
        daily.groupby(["city", "year"], as_index=False)
        .agg(
            average_aqi=("aqi", "mean"),
            valid_days=("aqi", "count"),
        )
        .sort_values(["city", "year"])
        .reset_index(drop=True)
    )
    annual["average_aqi"] = annual["average_aqi"].round(2)
    return annual


def project_city_trends(
    annual: pd.DataFrame,
    forecast_years: int = DEFAULT_FORECAST_YEARS,
    min_training_years: int = MIN_TRAINING_YEARS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fit one linear model per city and project future annual mean AQI.

    Cities with fewer than min_training_years distinct annual observations
    remain in the historical data but are not forecast. Predictions are
    bounded to the AQI scale (0-500). Holdout MAE is measured by fitting on
    all but the latest observed year and predicting that final year.
    """
    if forecast_years < 1:
        raise ValueError("forecast_years must be at least 1.")
    if min_training_years < 2:
        raise ValueError("min_training_years must be at least 2.")

    required = {"city", "year", "average_aqi"}
    missing = required.difference(annual.columns)
    if missing:
        raise ValueError(
            f"Annual data is missing required columns: {', '.join(sorted(missing))}"
        )

    forecast_frames: list[pd.DataFrame] = []
    metric_rows: list[dict[str, Any]] = []

    for city, city_data in annual.groupby("city", sort=True):
        city_data = city_data.sort_values("year").dropna(
            subset=["year", "average_aqi"]
        )
        city_data = city_data.drop_duplicates(subset=["year"], keep="last")
        if len(city_data) < min_training_years:
            continue

        years = city_data["year"].to_numpy(dtype=float)
        values = city_data["average_aqi"].to_numpy(dtype=float)
        if not np.isfinite(years).all() or not np.isfinite(values).all():
            continue

        # A one-year chronological holdout gives an honest, simple error check.
        holdout_model = LinearRegression()
        holdout_model.fit(years[:-1].reshape(-1, 1), values[:-1])
        holdout_prediction = float(
            holdout_model.predict(np.array([[years[-1]]]))[0]
        )
        holdout_mae = abs(float(values[-1]) - holdout_prediction)

        model = LinearRegression()
        model.fit(years.reshape(-1, 1), values)
        future_years = np.arange(
            int(years.max()) + 1,
            int(years.max()) + forecast_years + 1,
            dtype=int,
        )
        predictions = model.predict(future_years.reshape(-1, 1))
        predictions = np.clip(predictions, AQI_MIN, AQI_MAX)

        forecast_frames.append(pd.DataFrame({
            "city": city,
            "year": future_years,
            "average_aqi": np.round(predictions, 2),
            "valid_days": pd.NA,
            "record_type": "forecast",
        }))
        metric_rows.append({
            "city": city,
            "historical_years": len(city_data),
            "first_year": int(years.min()),
            "last_year": int(years.max()),
            "slope_aqi_per_year": round(float(model.coef_[0]), 4),
            "intercept": round(float(model.intercept_), 4),
            "last_year_holdout_actual": round(float(values[-1]), 2),
            "last_year_holdout_predicted": round(
                float(np.clip(holdout_prediction, AQI_MIN, AQI_MAX)), 2
            ),
            "last_year_holdout_mae": round(holdout_mae, 2),
        })

    if forecast_frames:
        forecasts = pd.concat(forecast_frames, ignore_index=True)
    else:
        forecasts = pd.DataFrame(
            columns=["city", "year", "average_aqi", "valid_days", "record_type"]
        )

    metrics = pd.DataFrame(metric_rows)
    return forecasts, metrics


def plot_city_trends(
    annual: pd.DataFrame,
    forecasts: pd.DataFrame,
    output_path: str | Path | None = None,
):
    """Plot actual annual values and dashed per-city linear projections."""
    cities = sorted(annual["city"].dropna().unique())
    palette = plt.get_cmap("tab10")
    colors = {city: palette(index % 10) for index, city in enumerate(cities)}

    fig, ax = plt.subplots(figsize=(12, 7))
    for city in cities:
        actual = annual[annual["city"] == city].sort_values("year")
        color = colors[city]
        ax.plot(
            actual["year"],
            actual["average_aqi"],
            color=color,
            marker="o",
            linewidth=2,
            label=f"{city} (historical)",
        )

        future = forecasts[forecasts["city"] == city].sort_values("year")
        if not future.empty:
            # Join the last observed point to the first forecast point.
            last_actual = actual.iloc[-1]
            x_values = [int(last_actual["year"])] + future["year"].astype(int).tolist()
            y_values = [float(last_actual["average_aqi"])] + future[
                "average_aqi"
            ].astype(float).tolist()
            ax.plot(
                x_values,
                y_values,
                color=color,
                linestyle="--",
                marker="o",
                linewidth=2,
                label=f"{city} (projection)",
            )

    if not forecasts.empty:
        first_forecast_year = int(forecasts["year"].min())
        ax.axvline(
            first_forecast_year - 0.5,
            color="grey",
            linestyle=":",
            linewidth=1.2,
            label="Forecast begins",
        )

    ax.set(
        title="City-wise annual PM2.5-based AQI: history and linear projection",
        xlabel="Year",
        ylabel="Annual mean daily AQI",
    )
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(output_path, dpi=170, bbox_inches="tight")
    return fig


def run_forecast(
    csv_path: str | Path = DEFAULT_DATASET_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    forecast_years: int = DEFAULT_FORECAST_YEARS,
    show_plots: bool = False,
) -> dict[str, Any]:
    """Run annual aggregation, per-city regression, and export the results."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    raw = pd.read_csv(csv_path)
    annual = prepare_annual_aqi(raw)
    forecasts, metrics = project_city_trends(annual, forecast_years)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    actual_export = annual.copy()
    actual_export["record_type"] = "historical"
    combined = pd.concat([actual_export, forecasts], ignore_index=True)
    combined = combined.sort_values(["city", "year", "record_type"])
    combined.to_csv(output_dir / "yearly_aqi_and_forecast.csv", index=False)
    metrics.to_csv(output_dir / "city_forecast_metrics.csv", index=False)
    plot_city_trends(
        annual,
        forecasts,
        output_dir / "city_yearly_aqi_forecast.png",
    )

    print("\nCity-wise annual AQI trend and projection\n")
    print(f"Historical city-year rows: {len(annual)}")
    print(f"Cities with forecasts: {len(metrics)}")
    if metrics.empty:
        print(
            "No city had enough distinct historical years for a forecast. "
            f"At least {MIN_TRAINING_YEARS} years are required."
        )
    else:
        print(metrics.to_string(index=False))
    print(f"Saved outputs to: {output_dir.resolve()}")

    if show_plots:
        plt.show()
    else:
        plt.close("all")

    return {
        "annual": annual,
        "forecasts": forecasts,
        "metrics": metrics,
        "combined": combined,
        "output_dir": output_dir,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot city-wise annual AQI history and linear projections."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to the hourly air-quality CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the graph and CSV outputs.",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=DEFAULT_FORECAST_YEARS,
        help="Number of future years to project (default: 5).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the graph after saving it.",
    )
    args = parser.parse_args()
    run_forecast(args.csv, args.output_dir, args.years, args.show)


if __name__ == "__main__":
    main()
