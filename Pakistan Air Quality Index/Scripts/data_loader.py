"""Loads the historical CSV file, converts fields into usable Python values, and provides query helpers used by the dashboard."""

# ============================================================
# DATA LOADER MODULE
# ============================================================
# Responsible for loading the Pakistan air quality CSV dataset
# and providing simple helper functions to query the data.
# ============================================================

import csv
import os

# ----------------------------------------------------------
# COLUMNS THAT CONTAIN NUMERICAL VALUES
# ----------------------------------------------------------
# These columns must be converted from text (string) to float
# so that mathematical calculations can be performed later.

NUMERIC_COLUMNS = [
    "pm10",
    "pm2_5",
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
    "pressure"
]

# ----------------------------------------------------------
# DATASET PATH
# ----------------------------------------------------------
# Automatically finds the CSV file relative to this script,
# so the program works no matter where it is run from.

SCRIPTS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(SCRIPTS_FOLDER)

DATASET_PATH = os.path.join(
    PROJECT_FOLDER, "Dataset", "pakistan_air_quality_final_clean_v2.csv"
)


# ----------------------------------------------------------
# LOAD THE ENTIRE DATASET
# ----------------------------------------------------------
# Reads the CSV, checks required columns, cleans city names, converts known numeric fields, and returns a list of row dictionaries.
def load_dataset(file_path=DATASET_PATH):
    """
    Open the CSV file, validate required columns, convert numeric
    fields to float, and return a list of dictionaries (one per row).
    """
    records = []

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        # Make sure the most important columns exist
        required_columns = ["city", "timestamp", "pm2_5", "pm10"]
        for column in required_columns:
            if column not in reader.fieldnames:
                raise ValueError(f"Missing required column: {column}")

        for row in reader:
            # Clean city name (remove extra spaces)
            row["city"] = row["city"].strip()

            # Convert numeric columns from string → float
            for column in NUMERIC_COLUMNS:
                value = row[column].strip()

                if value == "":
                    row[column] = None          # Missing value
                else:
                    row[column] = float(value)  # Convert to number

            records.append(row)

    return records


# ----------------------------------------------------------
# GET LIST OF ALL AVAILABLE CITIES
# ----------------------------------------------------------
# Builds a sorted list containing each city name once.
def get_available_cities(records):
    """
    Return a sorted list of unique city names present in the dataset.
    Used to fill the city dropdown in the GUI.
    """
    cities = []

    for row in records:
        city = row["city"]
        if city not in cities:
            cities.append(city)

    cities.sort()
    return cities


# ----------------------------------------------------------
# GET ALL READINGS FOR ONE CITY
# ----------------------------------------------------------
# Filters all records to the selected city, ignoring capitalization differences.
def get_city_readings(records, selected_city):
    """
    Return every record that belongs to the selected city
    (case-insensitive matching).
    """
    city_readings = []

    for row in records:
        if row["city"].lower() == selected_city.strip().lower():
            city_readings.append(row)

    return city_readings


# ----------------------------------------------------------
# GET THE MOST RECENT READING FOR A CITY
# ----------------------------------------------------------
# Returns the most recent available record for a city, or None if the city has no rows.
def get_latest_city_reading(records, selected_city):
    """
    Return the newest record for the given city (based on timestamp).
    Used as a fallback when live API data is unavailable.
    """
    city_readings = get_city_readings(records, selected_city)

    if len(city_readings) == 0:
        return None

    # max() with a key finds the row that has the latest timestamp
    latest_reading = max(city_readings, key=lambda row: row["timestamp"])
    return latest_reading


# ----------------------------------------------------------
# GET THE DATE RANGE COVERED BY THE DATASET
# ----------------------------------------------------------
# Returns the earliest and latest dates represented in the loaded records.
def get_date_range(records):
    """
    Return the earliest and latest date present in the dataset.
    Used to validate the date the user types in the GUI.
    """
    dates = [row["date"] for row in records]
    return min(dates), max(dates)


# ----------------------------------------------------------
# GET ONE SPECIFIC READING (CITY + DATE + HOUR)
# ----------------------------------------------------------
# Finds a record matching a city, date, and hour; returns None when no match exists.
def get_city_reading_at(records, selected_city, date_text, hour):
    """
    Find the exact reading for a city on a given date and hour.
    Powers the "Check Dataset" button in the GUI.
    """
    city_readings = get_city_readings(records, selected_city)

    for row in city_readings:
        if row["date"] == date_text and int(row["hour"]) == hour:
            return row

    return None   # No matching record found
