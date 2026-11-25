"""Experimental supervised models for estimating PM2.5-based AQI.

The target is derived from a valid daily PM2.5 average using the revised
2024 US EPA PM2.5 breakpoints. PM2.5 is deliberately excluded from model
features to prevent target leakage. This is an estimation experiment, not
an AQI forecast and not a replacement for the EPA calculation.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from aqi_calculator import calculate_pm25_aqi as pm25_24h_to_aqi


PROJECT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_PATH = PROJECT_DIR / "Dataset" / "pakistan_air_quality_final_clean_v2.csv"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "Outputs" / "aqi_regression"

# PM2.5 is intentionally absent. It is used only to create the AQI target.
CANDIDATE_FEATURES = (
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "dust",
    "temperature",
    "humidity",
    "precipitation",
    "wind_speed",
    "wind_direction",
    "pressure",
)


# Cleans hourly rows, creates city-day AQI targets, aggregates available predictor columns, and returns the daily training table plus selected feature names.
def prepare_daily_training_data(
    data: pd.DataFrame,
    min_valid_hours: int = 18,
) -> tuple[pd.DataFrame, list[str]]:
    """Create city-day rows and AQI targets from hourly pollution records.

    A daily target is retained only when at least min_valid_hours of the
    24 hourly PM2.5 values are present. Other pollutant/weather features are
    averaged over the same city-day. Missing feature values remain missing
    and are handled inside each model's training pipeline.
    """
    required = {"city", "timestamp", "pm2_5"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    if not 1 <= min_valid_hours <= 24:
        raise ValueError("min_valid_hours must be between 1 and 24.")

    frame = data.copy()
    frame["city"] = frame["city"].astype("string").str.strip()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    frame["pm2_5"] = pd.to_numeric(frame["pm2_5"], errors="coerce")
    frame["pm2_5"] = frame["pm2_5"].where(np.isfinite(frame["pm2_5"]))
    frame = frame.dropna(subset=["city", "timestamp"])
    frame = frame[frame["city"] != ""]
    # Duplicate city/timestamp rows must not inflate daily valid-hour counts.
    frame = frame.sort_values("timestamp").drop_duplicates(
        subset=["city", "timestamp"], keep="last"
    )

    feature_columns = [
        column for column in CANDIDATE_FEATURES
        if column in frame.columns and pd.to_numeric(frame[column], errors="coerce").notna().any()
    ]
    if not feature_columns:
        raise ValueError("No usable pollutant or weather feature columns were found.")

    for column in feature_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame[column] = frame[column].where(np.isfinite(frame[column]))

    frame["date"] = frame["timestamp"].dt.date
    grouped = frame.groupby(["city", "date"], sort=True)

    pm25_summary = grouped["pm2_5"].agg(pm25_mean="mean", pm25_valid_hours="count")
    feature_summary = grouped[feature_columns].mean()
    daily = pm25_summary.join(feature_summary).reset_index()

    daily = daily[daily["pm25_valid_hours"] >= min_valid_hours].copy()
    daily["aqi"] = daily["pm25_mean"].map(pm25_24h_to_aqi)
    daily = daily.dropna(subset=["aqi"])
    daily["aqi"] = daily["aqi"].astype(int)
    daily = daily.drop(columns=["pm25_mean", "pm25_valid_hours"])

    # A row with no available predictor values cannot be used by any model.
    daily = daily.dropna(subset=feature_columns, how="all")
    if daily.empty:
        raise ValueError(
            "No trainable city-day rows remain. Check hourly coverage and PM2.5 values."
        )

    return daily.reset_index(drop=True), feature_columns


# Splits rows by date so earlier observations are training data and later observations are held out for evaluation.
def chronological_split(
    daily: pd.DataFrame,
    test_fraction: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split by date so later observations form the test set."""
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1.")

    dates = sorted(pd.to_datetime(daily["date"]).dt.date.unique())
    if len(dates) < 5:
        raise ValueError("At least five distinct dates are required for a time-based split.")

    test_days = max(1, math.ceil(len(dates) * test_fraction))
    if len(dates) - test_days < 2:
        raise ValueError("Not enough dates remain for training after the test split.")

    cutoff = dates[-test_days]
    row_dates = pd.to_datetime(daily["date"]).dt.date
    train = daily[row_dates < cutoff].copy()
    test = daily[row_dates >= cutoff].copy()
    if len(train) < 2 or len(test) < 2:
        raise ValueError("The chronological split produced too few rows to evaluate reliably.")
    return train, test


# Creates the preprocessing and regression pipelines being compared.
def build_models() -> dict[str, Pipeline]:
    """Return the three agreed regression pipelines."""
    return {
        "Linear Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("regressor", LinearRegression()),
        ]),
        "Polynomial Regression (degree 2)": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("polynomial", PolynomialFeatures(degree=2, include_bias=False)),
            ("scaler", StandardScaler()),
            ("regressor", LinearRegression()),
        ]),
        "Random Forest Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("regressor", RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                min_samples_leaf=2,
                n_jobs=-1,
            )),
        ]),
    }


# Fits each model on training dates, predicts held-out dates, and calculates MAE, RMSE, and R-squared.
def train_and_evaluate(
    daily: pd.DataFrame,
    feature_columns: list[str],
) -> dict[str, Any]:
    """Fit each model on earlier dates and evaluate on later dates."""
    train, test = chronological_split(daily)
    x_train = train[feature_columns]
    x_test = test[feature_columns]
    y_train = train["aqi"]
    y_test = test["aqi"]

    fitted_models: dict[str, Pipeline] = {}
    predictions: dict[str, np.ndarray] = {}
    metric_rows = []

    for name, model in build_models().items():
        model.fit(x_train, y_train)
        predicted = model.predict(x_test)
        fitted_models[name] = model
        predictions[name] = predicted
        metric_rows.append({
            "Model": name,
            "MAE": mean_absolute_error(y_test, predicted),
            "RMSE": math.sqrt(mean_squared_error(y_test, predicted)),
            "R2": r2_score(y_test, predicted),
        })

    return {
        "models": fitted_models,
        "predictions": predictions,
        "actual": y_test.to_numpy(),
        "test_rows": test,
        "metrics": pd.DataFrame(metric_rows).sort_values("MAE").reset_index(drop=True),
    }


# Plots held-out actual AQI values against the predictions from each regression model.
def plot_actual_vs_predicted(
    results: dict[str, Any],
    output_path: str | Path | None = None,
):
    """Plot held-out actual AQI against predictions from all three models."""
    actual = np.asarray(results["actual"])
    fig, ax = plt.subplots(figsize=(9, 6))
    lower = min(float(np.min(actual)), *(float(np.min(p)) for p in results["predictions"].values()))
    upper = max(float(np.max(actual)), *(float(np.max(p)) for p in results["predictions"].values()))
    ax.plot([lower, upper], [lower, upper], linestyle="--", label="Perfect prediction")

    for name, predicted in results["predictions"].items():
        ax.scatter(actual, predicted, alpha=0.65, label=name)

    ax.set(
        title="AQI estimation: actual vs predicted",
        xlabel="Actual PM2.5-based AQI",
        ylabel="Predicted AQI",
    )
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")
    return fig


# Plots one selected feature against AQI with descriptive linear and quadratic fitted curves.
def plot_linear_and_nonlinear_relationship(
    daily: pd.DataFrame,
    feature: str | None = None,
    output_path: str | Path | None = None,
):
    """Plot a predictor against AQI with straight and quadratic trend curves."""
    available = [column for column in CANDIDATE_FEATURES if column in daily.columns]
    if feature is None:
        feature = "pm10" if "pm10" in available else (available[0] if available else None)
    if feature is None or feature not in daily.columns:
        raise ValueError("No valid feature is available for the relationship plot.")

    points = daily[[feature, "aqi"]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(points) < 3 or points[feature].nunique() < 3:
        raise ValueError(f"Not enough distinct {feature} values to draw linear and nonlinear curves.")

    x = points[feature].to_numpy(dtype=float)
    y = points["aqi"].to_numpy(dtype=float)
    x_line = np.linspace(float(x.min()), float(x.max()), 250)
    linear_coefficients = np.polyfit(x, y, deg=1)
    quadratic_coefficients = np.polyfit(x, y, deg=2)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(x, y, alpha=0.35, label="Observed city-day records")
    ax.plot(x_line, np.polyval(linear_coefficients, x_line), label="Linear fit")
    ax.plot(x_line, np.polyval(quadratic_coefficients, x_line), label="Nonlinear quadratic fit")
    ax.set(
        title=f"AQI relationship with {feature}",
        xlabel=f"Daily mean {feature}",
        ylabel="PM2.5-based AQI",
    )
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(output_path, dpi=160, bbox_inches="tight")
    return fig


# Runs data preparation, training, evaluation, CSV export, and graph generation as one workflow.
def run_experiment(
    csv_path: str | Path = DEFAULT_DATASET_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    show_plots: bool = False,
) -> dict[str, Any]:
    """Run the complete experiment and save metrics and visualizations."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    raw = pd.read_csv(csv_path)
    daily, features = prepare_daily_training_data(raw)
    results = train_and_evaluate(daily, features)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results["metrics"].to_csv(output_dir / "model_metrics.csv", index=False)
    plot_actual_vs_predicted(results, output_dir / "actual_vs_predicted.png")
    plot_linear_and_nonlinear_relationship(
        daily,
        output_path=output_dir / "linear_vs_nonlinear.png",
    )

    print("\nAQI estimation model comparison (chronological holdout)\n")
    print(results["metrics"].to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    print(f"\nFeatures used (PM2.5 excluded): {', '.join(features)}")
    print(f"Saved results to: {output_dir.resolve()}")

    if show_plots:
        plt.show()
    else:
        plt.close("all")
    return {
        **results,
        "daily_data": daily,
        "features": features,
        "output_dir": output_dir,
    }


# Parses command-line options and starts the regression experiment.
def main() -> None:
    parser = argparse.ArgumentParser(description="Train and compare AQI regression models.")
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
        help="Directory for metrics and plots.",
    )
    parser.add_argument("--show", action="store_true", help="Display the generated plots after saving them.")
    args = parser.parse_args()
    run_experiment(args.csv, args.output_dir, args.show)


if __name__ == "__main__":
    main()
