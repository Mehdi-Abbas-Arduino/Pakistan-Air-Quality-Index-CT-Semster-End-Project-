
from validation import (
    find_missing_pm25,
    find_out_of_range_pm25,
    find_category_mismatches,
    run_validation
)


def test_find_missing_pm25():
    records = [{"pm2_5": 10.0}, {"pm2_5": None}]

    assert len(find_missing_pm25(records)) == 1


def test_find_out_of_range_pm25():
    records = [{"pm2_5": 10.0}, {"pm2_5": -3.0}, {"pm2_5": 600.0}, {"pm2_5": None}]

    # Only -3.0 and 600.0 are out of range. None counts as missing, not out of range.
    assert len(find_out_of_range_pm25(records)) == 2


def test_category_mismatch_is_detected():
    records = [
        {"pm2_5": 10.0, "aqi_category": "Good"},       # correct
        {"pm2_5": 10.0, "aqi_category": "Hazardous"},  # wrong label
    ]

    assert len(find_category_mismatches(records)) == 1


def test_real_dataset_passes_all_checks():
    assert run_validation() is True
