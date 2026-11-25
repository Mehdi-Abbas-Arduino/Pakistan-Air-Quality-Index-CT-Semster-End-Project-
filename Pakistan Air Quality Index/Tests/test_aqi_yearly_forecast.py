import pandas as pd

from ml.aqi_yearly_forecast import prepare_annual_aqi, project_city_trends


def make_hourly_data():
    rows = []
    # Daily PM2.5 rises across three years, producing a clear test trend.
    for year, pm25 in [(2021, 12.0), (2022, 20.0), (2023, 30.0)]:
        for hour in range(18):
            rows.append({
                "city": "Karachi",
                "timestamp": f"{year}-06-01 {hour:02d}:00:00",
                "pm2_5": pm25,
            })
    return pd.DataFrame(rows)


def test_prepare_annual_aqi_uses_daily_aqi_and_yearly_average():
    annual = prepare_annual_aqi(make_hourly_data())

    assert annual["city"].tolist() == ["Karachi"] * 3
    assert annual["year"].tolist() == [2021, 2022, 2023]
    assert annual["valid_days"].tolist() == [1, 1, 1]
    assert annual["average_aqi"].is_monotonic_increasing


def test_prepare_annual_aqi_rejects_days_below_hour_threshold():
    data = make_hourly_data()
    data = data[data["timestamp"].str.startswith("2021")]

    annual = prepare_annual_aqi(data)
    assert annual.empty


def test_project_city_trends_creates_five_future_years():
    annual = prepare_annual_aqi(make_hourly_data())
    forecasts, metrics = project_city_trends(annual, forecast_years=5)

    assert forecasts["year"].tolist() == [2024, 2025, 2026, 2027, 2028]
    assert forecasts["city"].eq("Karachi").all()
    assert forecasts["average_aqi"].between(0, 500).all()
    assert len(metrics) == 1
    assert metrics.loc[0, "historical_years"] == 3


def test_cities_with_too_few_years_are_not_forecast():
    annual = pd.DataFrame({
        "city": ["Karachi", "Karachi"],
        "year": [2022, 2023],
        "average_aqi": [80.0, 90.0],
        "valid_days": [100, 100],
    })

    forecasts, metrics = project_city_trends(annual, forecast_years=5)

    assert forecasts.empty
    assert metrics.empty
