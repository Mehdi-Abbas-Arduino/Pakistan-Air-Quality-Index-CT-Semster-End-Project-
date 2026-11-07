
import pytest

from data_loader import (
    NUMERIC_COLUMNS,
    load_dataset,
    get_available_cities,
    get_city_readings,
    get_latest_city_reading
)


# -----------------------------------------
# HELPER: build a tiny CSV file for tests
# -----------------------------------------

def make_csv(tmp_path, rows, columns=None):

    # By default the file has every column the loader expects.
    if columns is None:
        columns = ["timestamp", "city"] + NUMERIC_COLUMNS

    path = tmp_path / "test.csv"

    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(row))

    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def make_row(city="Lahore", timestamp="2026-01-01 00:00:00", value="10.0"):
    return [timestamp, city] + [value] * len(NUMERIC_COLUMNS)


# -----------------------------------------
# load_dataset
# -----------------------------------------

def test_real_dataset_loads_all_rows():
    records = load_dataset()
    assert len(records) == 21840


def test_numeric_columns_become_floats(tmp_path):
    path = make_csv(tmp_path, [make_row()])
    records = load_dataset(path)

    assert records[0]["pm2_5"] == 10.0
    assert isinstance(records[0]["pm2_5"], float)


def test_empty_numeric_value_becomes_none(tmp_path):
    row = make_row()
    row[2] = ""   # first numeric column (pm10) left empty

    records = load_dataset(make_csv(tmp_path, [row]))

    assert records[0]["pm10"] is None


def test_city_name_is_stripped(tmp_path):
    path = make_csv(tmp_path, [make_row(city="  Lahore  ")])
    records = load_dataset(path)

    assert records[0]["city"] == "Lahore"


def test_missing_required_column_raises_error(tmp_path):
    # A file with no "city" column.
    columns = ["timestamp", "pm2_5", "pm10"]
    path = make_csv(tmp_path, [["2026-01-01 00:00:00", "1", "2"]], columns)

    with pytest.raises(ValueError):
        load_dataset(path)


def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        load_dataset("this_file_does_not_exist.csv")


# -----------------------------------------
# get_available_cities
# -----------------------------------------

def test_cities_are_unique_and_sorted():
    records = [{"city": "Multan"}, {"city": "Lahore"}, {"city": "Multan"}]

    assert get_available_cities(records) == ["Lahore", "Multan"]


def test_real_dataset_has_ten_cities():
    cities = get_available_cities(load_dataset())

    assert len(cities) == 10
    assert "Karachi" in cities


# -----------------------------------------
# get_city_readings
# -----------------------------------------

def test_city_search_ignores_case_and_spaces():
    records = [{"city": "Multan"}, {"city": "Lahore"}]

    assert len(get_city_readings(records, "  mULTan ")) == 1


def test_unknown_city_gives_empty_list():
    records = [{"city": "Multan"}]

    assert get_city_readings(records, "Atlantis") == []


# -----------------------------------------
# get_latest_city_reading
# -----------------------------------------

def test_latest_reading_has_newest_timestamp():
    records = [
        {"city": "Multan", "timestamp": "2026-01-01 05:00:00"},
        {"city": "Multan", "timestamp": "2026-01-03 01:00:00"},
        {"city": "Multan", "timestamp": "2026-01-02 23:00:00"},
        {"city": "Lahore", "timestamp": "2026-02-01 00:00:00"},
    ]

    latest = get_latest_city_reading(records, "Multan")

    assert latest["timestamp"] == "2026-01-03 01:00:00"


def test_latest_reading_of_unknown_city_is_none():
    assert get_latest_city_reading([{"city": "Multan", "timestamp": "x"}], "Atlantis") is None
