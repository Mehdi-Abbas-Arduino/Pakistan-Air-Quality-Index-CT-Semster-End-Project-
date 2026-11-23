import pytest

from aqi_calculator import (
    calculate_pm25_aqi,
    get_aqi_category,
    get_average_aqi,
    get_worst_reading,
)


@pytest.mark.parametrize("pm25, expected", [
    (0.0, 0), (9.0, 50), (9.1, 51), (12.0, 56), (12.1, 57),
    (35.4, 100), (35.5, 101), (55.4, 150), (55.5, 151),
    (103.4, 185), (125.4, 200), (125.5, 201), (225.4, 300),
    (225.5, 301), (325.4, 400), (325.5, 401), (500.4, 500),
])
def test_2024_pm25_breakpoint_edges(pm25, expected):
    assert calculate_pm25_aqi(pm25) == expected


def test_pm25_is_truncated_to_one_decimal():
    assert calculate_pm25_aqi(12.04) == 56


@pytest.mark.parametrize("bad_value", [None, -1, -0.5, 500.5, 1000, "not a number"])
def test_invalid_pm25_returns_none(bad_value):
    assert calculate_pm25_aqi(bad_value) is None


@pytest.mark.parametrize("aqi, expected", [
    (0, "Good"), (50, "Good"), (51, "Moderate"), (100, "Moderate"),
    (101, "Unhealthy for Sensitive Groups"), (150, "Unhealthy for Sensitive Groups"),
    (151, "Unhealthy"), (200, "Unhealthy"), (201, "Very Unhealthy"),
    (300, "Very Unhealthy"), (301, "Hazardous"), (500, "Hazardous"),
])
def test_category_boundaries(aqi, expected):
    assert get_aqi_category(aqi) == expected


def test_category_of_none_is_none():
    assert get_aqi_category(None) is None


def test_average_aqi():
    readings = [{"pm2_5": 12.0}, {"pm2_5": 35.4}]  # AQI 56 and 100
    assert get_average_aqi(readings) == 78


def test_average_skips_missing_values():
    readings = [{"pm2_5": 12.0}, {"pm2_5": None}, {"pm2_5": 35.4}]
    assert get_average_aqi(readings) == 78


def test_average_of_empty_list_is_none():
    assert get_average_aqi([]) is None


def test_average_when_all_values_missing_is_none():
    assert get_average_aqi([{"pm2_5": None}]) is None


def test_worst_reading():
    low = {"pm2_5": 9.0, "timestamp": "a"}
    high = {"pm2_5": 103.4, "timestamp": "b"}
    mid = {"pm2_5": 35.4, "timestamp": "c"}
    row, aqi = get_worst_reading([low, high, mid])
    assert row is high
    assert aqi == 185


def test_worst_reading_of_empty_list():
    assert get_worst_reading([]) == (None, None)
