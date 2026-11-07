import pytest

from aqi_calculator import (
    calculate_pm25_aqi,
    get_aqi_category,
    get_average_aqi,
    get_worst_reading
)


# -----------------------------------------
# calculate_pm25_aqi
# -----------------------------------------

# Every breakpoint edge: (PM2.5, expected AQI).
@pytest.mark.parametrize("pm25, expected", [
    (0.0, 0),
    (12.0, 50),
    (12.1, 51),
    (35.4, 100),
    (35.5, 101),
    (55.4, 150),
    (55.5, 151),
    (150.4, 200),
    (150.5, 201),
    (250.4, 300),
    (250.5, 301),
    (350.4, 400),
    (350.5, 401),
    (500.4, 500),
])
def test_pm25_breakpoint_edges(pm25, expected):
    assert calculate_pm25_aqi(pm25) == expected


def test_pm25_middle_of_a_band():
    # 103.4 is the Multan reading we checked by hand.
    assert calculate_pm25_aqi(103.4) == 176


def test_pm25_is_rounded_to_one_decimal():
    # 12.04 rounds to 12.0, so it stays in the "Good" band.
    assert calculate_pm25_aqi(12.04) == 50


def test_pm25_missing_value_returns_none():
    assert calculate_pm25_aqi(None) is None


@pytest.mark.parametrize("bad_value", [-1, -0.5, 500.5, 1000])
def test_pm25_outside_table_returns_none(bad_value):
    assert calculate_pm25_aqi(bad_value) is None


# -----------------------------------------
# get_aqi_category
# -----------------------------------------

@pytest.mark.parametrize("aqi, expected", [
    (0, "Good"),
    (50, "Good"),
    (51, "Moderate"),
    (100, "Moderate"),
    (101, "Unhealthy for Sensitive Groups"),
    (150, "Unhealthy for Sensitive Groups"),
    (151, "Unhealthy"),
    (200, "Unhealthy"),
    (201, "Very Unhealthy"),
    (300, "Very Unhealthy"),
    (301, "Hazardous"),
    (500, "Hazardous"),
])
def test_category_boundaries(aqi, expected):
    assert get_aqi_category(aqi) == expected


def test_category_of_none_is_none():
    assert get_aqi_category(None) is None


# -----------------------------------------
# get_average_aqi
# -----------------------------------------

def test_average_aqi():
    readings = [{"pm2_5": 12.0}, {"pm2_5": 35.4}]   # AQI 50 and 100
    assert get_average_aqi(readings) == 75


def test_average_skips_missing_values():
    readings = [{"pm2_5": 12.0}, {"pm2_5": None}, {"pm2_5": 35.4}]
    assert get_average_aqi(readings) == 75


def test_average_of_empty_list_is_none():
    assert get_average_aqi([]) is None


def test_average_when_all_values_missing_is_none():
    assert get_average_aqi([{"pm2_5": None}]) is None


# -----------------------------------------
# get_worst_reading
# -----------------------------------------

def test_worst_reading():
    low = {"pm2_5": 12.0, "timestamp": "a"}
    high = {"pm2_5": 103.4, "timestamp": "b"}
    mid = {"pm2_5": 35.4, "timestamp": "c"}

    row, aqi = get_worst_reading([low, high, mid])

    assert row is high
    assert aqi == 176


def test_worst_reading_of_empty_list():
    assert get_worst_reading([]) == (None, None)