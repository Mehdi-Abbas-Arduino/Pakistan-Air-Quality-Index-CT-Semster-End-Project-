"""Centralizes input validation. Functions return cleaned values when inputs are valid and raise ValueError with a user-readable message otherwise."""

# ============================================================
# VALIDATION MODULE
# ============================================================
# All user input is checked here before being used in the app.
# Every function either returns a clean value or raises a
# ValueError with a clear message that can be shown to the user.
# ============================================================

import difflib
import math
from datetime import datetime


# ----------------------------------------------------------
# VALIDATE CITY NAME
# ----------------------------------------------------------
# Checks whether a city exists in the dataset and suggests a close spelling when possible.
def validate_city(text, cities):
    """
    Check that the typed city exists in the dataset.
    - Ignores upper/lower case
    - Suggests the closest match if there is a small typo
    """
    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter a city name.")

    # Exact match (case-insensitive)
    for city in cities:
        if city.lower() == cleaned.lower():
            return city   # Return the official spelling

    # No exact match → try to suggest the closest city
    lower_names = [city.lower() for city in cities]
    close = difflib.get_close_matches(cleaned.lower(), lower_names, n=1)

    if close:
        suggestion = cities[lower_names.index(close[0])]
        raise ValueError(f"City '{cleaned}' not found. Did you mean {suggestion}?")

    raise ValueError(f"City '{cleaned}' not found. Available cities: {', '.join(cities)}")


# ----------------------------------------------------------
# VALIDATE DATE
# ----------------------------------------------------------
# Parses a date in YYYY-MM-DD form and checks that it falls within the dataset's available date range.
def validate_date(text, first_date, last_date):
    """
    Check that the date is in YYYY-MM-DD format and falls
    inside the range covered by the dataset.
    """
    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter a date (YYYY-MM-DD).")

    try:
        parsed = datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must look like 2026-01-15 (YYYY-MM-DD).")

    # Normalize the format (e.g. 2026-1-5 → 2026-01-05)
    date_text = parsed.strftime("%Y-%m-%d")

    if date_text < first_date or date_text > last_date:
        raise ValueError(
            f"No data for that date. Choose a date between {first_date} and {last_date}."
        )

    return date_text


# ----------------------------------------------------------
# VALIDATE HOUR
# ----------------------------------------------------------
# Accepts only an integer hour from 0 through 23.
def validate_hour(text):
    """
    Accept only whole numbers from 0 to 23.
    """
    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter an hour (0 to 23).")

    if not cleaned.isdigit():
        raise ValueError("Hour must be a whole number from 0 to 23.")

    hour = int(cleaned)

    if hour > 23:
        raise ValueError("Hour must be between 0 and 23.")

    return hour


# ----------------------------------------------------------
# VALIDATE PM2.5 VALUE
# ----------------------------------------------------------
# Converts a PM2.5 input to a finite number and checks the accepted concentration range.
def validate_pm25(text):
    """
    Accept a number between 0 and 500.4 (the range of the EPA table).
    Rejects 'nan', 'inf' and non-numeric text.
    """
    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter a PM2.5 value.")

    try:
        value = float(cleaned)
    except ValueError:
        raise ValueError("PM2.5 must be a number, for example 85.5.")

    if not math.isfinite(value):
        raise ValueError("PM2.5 must be a number, for example 85.5.")

    if value < 0 or value > 500.4:
        raise ValueError("PM2.5 must be between 0 and 500.4 µg/m³.")

    return value


# ----------------------------------------------------------
# VALIDATE QUIZ GUESS
# ----------------------------------------------------------
# Accepts only a whole-number AQI guess from 0 through 500.
def validate_guess(text):
    """
    Accept a whole number between 0 and 500 for the quiz game.
    """
    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please type your guess (a whole number from 0 to 500).")

    if not cleaned.isdigit():
        raise ValueError("Your guess must be a whole number from 0 to 500.")

    guess = int(cleaned)

    if guess > 500:
        raise ValueError("The AQI scale ends at 500, so guess 500 or less.")

    return guess
