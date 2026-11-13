import difflib
import math
from datetime import datetime

'''• validate_city: Matches the name ignoring case and suggests the closest match with difflib if there is a typo.
• validate_date: Checks the YYYY-MM-DD format, is a real date, and falls within the dataset range.
• validate_hour: Accepts only whole numbers from 0 to 23.
• validate_pm25: Accepts a number from 0 to 500.4 and rejects nan and inf, which float() would otherwise accept.
• validate_guess: Accepts a whole number from 0 to 500 for the quiz.'''

# Every function here either returns a clean value,
# or raises a ValueError with a message that is safe to show the user.


# -----------------------------------------
# VALIDATE A CITY NAME
# -----------------------------------------

def validate_city(text, cities):

    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter a city name.")

    # Match ignoring upper/lower case, and return the official spelling.
    for city in cities:
        if city.lower() == cleaned.lower():
            return city

    # Not found: try to suggest the closest city name.
    lower_names = [city.lower() for city in cities]
    close = difflib.get_close_matches(cleaned.lower(), lower_names, n=1)

    if close:
        suggestion = cities[lower_names.index(close[0])]
        raise ValueError("City '" + cleaned + "' not found. Did you mean "
                         + suggestion + "?")

    raise ValueError("City '" + cleaned + "' not found. Available cities: "
                     + ", ".join(cities))


# -----------------------------------------
# VALIDATE A DATE
# -----------------------------------------

def validate_date(text, first_date, last_date):

    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter a date (YYYY-MM-DD).")

    # Check that it is a real calendar date in the right format.
    try:
        parsed = datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must look like 2026-01-15 (YYYY-MM-DD).")

    # Rebuild it so 2026-1-5 becomes 2026-01-05.
    date_text = parsed.strftime("%Y-%m-%d")

    # The dataset only covers a limited period.
    if date_text < first_date or date_text > last_date:
        raise ValueError("No data for that date. Choose a date between "
                         + first_date + " and " + last_date + ".")

    return date_text


# -----------------------------------------
# VALIDATE AN HOUR
# -----------------------------------------

def validate_hour(text):

    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter an hour (0 to 23).")

    # isdigit() rejects letters, decimals and negative numbers.
    if not cleaned.isdigit():
        raise ValueError("Hour must be a whole number from 0 to 23.")

    hour = int(cleaned)

    if hour > 23:
        raise ValueError("Hour must be between 0 and 23.")

    return hour


# -----------------------------------------
# VALIDATE A PM2.5 VALUE
# -----------------------------------------

def validate_pm25(text):

    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please enter a PM2.5 value.")

    try:
        value = float(cleaned)
    except ValueError:
        raise ValueError("PM2.5 must be a number, for example 85.5.")

    # float() also accepts 'nan' and 'inf', which are not real readings.
    if not math.isfinite(value):
        raise ValueError("PM2.5 must be a number, for example 85.5.")

    # The AQI table only covers 0 to 500.4.
    if value < 0 or value > 500.4:
        raise ValueError("PM2.5 must be between 0 and 500.4 µg/m³.")

    return value


# -----------------------------------------
# VALIDATE A QUIZ GUESS
# -----------------------------------------

def validate_guess(text):

    cleaned = text.strip()

    if cleaned == "":
        raise ValueError("Please type your guess (a whole number from 0 to 500).")

    # isdigit() rejects letters, decimals and negative numbers.
    if not cleaned.isdigit():
        raise ValueError("Your guess must be a whole number from 0 to 500.")

    guess = int(cleaned)

    if guess > 500:
        raise ValueError("The AQI scale ends at 500, so guess 500 or less.")

    return guess