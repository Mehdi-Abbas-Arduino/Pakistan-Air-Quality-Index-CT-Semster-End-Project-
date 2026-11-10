
import pytest

from input_validation import (
    validate_city,
    validate_date,
    validate_hour,
    validate_pm25
)
from data_loader import get_date_range, get_city_reading_at
from aqi_calculator import HEALTH_ADVICE, get_aqi_category, get_health_advice

CITIES = ["Karachi", "Lahore", "Multan"]


# -----------------------------------------
# validate_city
# -----------------------------------------

def test_city_exact_match():
    assert validate_city("Lahore", CITIES) == "Lahore"


def test_city_ignores_case_and_spaces():
    assert validate_city("  lAhOrE ", CITIES) == "Lahore"


@pytest.mark.parametrize("empty", ["", "   "])
def test_city_empty_is_rejected(empty):
    with pytest.raises(ValueError):
        validate_city(empty, CITIES)


def test_city_typo_suggests_closest():
    with pytest.raises(ValueError, match="Did you mean Karachi"):
        validate_city("Karchi", CITIES)


def test_city_unknown_lists_available():
    with pytest.raises(ValueError, match="Available cities"):
        validate_city("Atlantis", CITIES)


# -----------------------------------------
# validate_date
# -----------------------------------------

FIRST, LAST = "2025-11-06", "2026-02-04"


def test_date_valid():
    assert validate_date("2026-01-15", FIRST, LAST) == "2026-01-15"


def test_date_without_leading_zeros_is_normalised():
    assert validate_date("2026-1-5", FIRST, LAST) == "2026-01-05"


def test_date_edges_are_allowed():
    assert validate_date(FIRST, FIRST, LAST) == FIRST
    assert validate_date(LAST, FIRST, LAST) == LAST


@pytest.mark.parametrize("bad", ["", "15-01-2026", "tomorrow", "2026-02-30", "2026/01/15"])
def test_date_bad_format_is_rejected(bad):
    with pytest.raises(ValueError):
        validate_date(bad, FIRST, LAST)


@pytest.mark.parametrize("outside", ["2025-11-05", "2026-02-05", "2030-01-01"])
def test_date_outside_dataset_is_rejected(outside):
    with pytest.raises(ValueError, match="No data"):
        validate_date(outside, FIRST, LAST)


# -----------------------------------------
# validate_hour
# -----------------------------------------

@pytest.mark.parametrize("text, expected", [("0", 0), ("12", 12), ("23", 23), (" 7 ", 7)])
def test_hour_valid(text, expected):
    assert validate_hour(text) == expected


@pytest.mark.parametrize("bad", ["", "24", "-1", "3.5", "noon", "99"])
def test_hour_invalid_is_rejected(bad):
    with pytest.raises(ValueError):
        validate_hour(bad)


# -----------------------------------------
# validate_pm25
# -----------------------------------------

@pytest.mark.parametrize("text, expected", [("0", 0.0), ("85.5", 85.5), (" 500.4 ", 500.4)])
def test_pm25_valid(text, expected):
    assert validate_pm25(text) == expected


@pytest.mark.parametrize("bad", ["", "abc", "nan", "inf", "-1", "500.5", "1e9"])
def test_pm25_invalid_is_rejected(bad):
    with pytest.raises(ValueError):
        validate_pm25(bad)


# -----------------------------------------
# data_loader additions
# -----------------------------------------

def test_date_range():
    records = [{"date": "2026-01-05"}, {"date": "2025-12-30"}, {"date": "2026-01-20"}]

    assert get_date_range(records) == ("2025-12-30", "2026-01-20")


def test_reading_at_date_and_hour():
    records = [
        {"city": "Multan", "date": "2026-01-01", "hour": "5", "pm2_5": 1.0},
        {"city": "Multan", "date": "2026-01-01", "hour": "6", "pm2_5": 2.0},
    ]

    assert get_city_reading_at(records, "multan", "2026-01-01", 6)["pm2_5"] == 2.0


def test_reading_at_missing_time_is_none():
    records = [{"city": "Multan", "date": "2026-01-01", "hour": "5", "pm2_5": 1.0}]

    assert get_city_reading_at(records, "Multan", "2026-01-01", 9) is None
    assert get_city_reading_at(records, "Lahore", "2026-01-01", 5) is None


# -----------------------------------------
# health advice
# -----------------------------------------

def test_every_category_has_advice():
    for category in ["Good", "Moderate", "Unhealthy for Sensitive Groups",
                     "Unhealthy", "Very Unhealthy", "Hazardous"]:
        assert get_health_advice(category) != ""


def test_unknown_category_has_no_advice():
    assert get_health_advice(None) == ""
