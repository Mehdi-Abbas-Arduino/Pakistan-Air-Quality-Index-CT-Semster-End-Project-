import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "Scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from ml.aqi_regression import (  # noqa: E402
    chronological_split,
    pm25_24h_to_aqi,
    prepare_daily_training_data,
    train_and_evaluate,
)


def make_hourly_data(days=8):
    rows = []
    for day in range(days):
        for hour in range(24):
            rows.append({
                "city": "Karachi",
                "timestamp": pd.Timestamp("2026-01-01") + pd.Timedelta(days=day, hours=hour),
                "pm2_5": 10 + day + hour / 100,
                "pm10": 20 + day * 2 + hour / 10,
                "carbon_monoxide": 100 + day * 3 + hour,
                "temperature": 25 + day / 2,
                "humidity": 60 + hour / 10,
            })
    return pd.DataFrame(rows)


def test_2024_pm25_aqi_breakpoints():
    assert pm25_24h_to_aqi(0.0) == 0
    assert pm25_24h_to_aqi(9.0) == 50
    assert pm25_24h_to_aqi(9.1) == 51
    assert pm25_24h_to_aqi(35.4) == 100
    assert pm25_24h_to_aqi(55.5) == 151
    assert pm25_24h_to_aqi(None) is None
    assert pm25_24h_to_aqi(-1) is None
    assert pm25_24h_to_aqi(500.5) is None


def test_daily_target_requires_18_valid_hourly_pm25_values():
    data = make_hourly_data(days=2)
    data.loc[data.index[:7], "pm2_5"] = np.nan
    daily, features = prepare_daily_training_data(data)
    assert len(daily) == 1
    assert daily.iloc[0]["date"] == pd.Timestamp("2026-01-02").date()
    assert "pm2_5" not in features
    assert "pm2_5" not in daily.columns


def test_duplicate_timestamps_do_not_count_as_extra_valid_hours():
    data = make_hourly_data(days=1)
    duplicated = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    daily, _ = prepare_daily_training_data(duplicated)
    assert len(daily) == 1
    assert daily.iloc[0]["date"] == pd.Timestamp("2026-01-01").date()


def test_feature_selection_excludes_pm25():
    daily, features = prepare_daily_training_data(make_hourly_data())
    assert "pm2_5" not in features
    assert "pm10" in features
    assert daily["aqi"].notna().all()


def test_missing_required_columns_raise_error():
    with pytest.raises(ValueError, match="city"):
        prepare_daily_training_data(pd.DataFrame({"timestamp": [], "pm2_5": []}))


def test_chronological_split_has_no_date_overlap():
    daily, _ = prepare_daily_training_data(make_hourly_data(days=10))
    train, test = chronological_split(daily)
    train_dates = set(train["date"])
    test_dates = set(test["date"])
    assert train_dates.isdisjoint(test_dates)
    assert max(train_dates) < min(test_dates)


def test_three_models_train_and_return_metrics():
    daily, features = prepare_daily_training_data(make_hourly_data(days=12))
    results = train_and_evaluate(daily, features)
    assert set(results["models"]) == {
        "Linear Regression",
        "Polynomial Regression (degree 2)",
        "Random Forest Regression",
    }
    assert set(results["metrics"]["Model"]) == set(results["models"])
    assert len(results["actual"]) == len(results["test_rows"])
