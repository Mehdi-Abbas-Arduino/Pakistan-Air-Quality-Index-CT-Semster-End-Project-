import random

from aqi_calculator import calculate_pm25_aqi


# -----------------------------------------
# QUIZ RULES
# -----------------------------------------

QUESTION_COUNT = 5
TRIES_PER_QUESTION = 5
TOLERANCE = 10          # a guess within +/- 10 AQI counts as correct
MAX_AQI = 500


# -----------------------------------------
# BUILD RANDOM QUESTIONS
# -----------------------------------------

def build_questions(records, count=QUESTION_COUNT, generator=None):

    # Use Python's random module unless a seeded generator is given (for tests).
    if generator is None:
        generator = random

    # Group the readings that have a valid AQI by city.
    readings_by_city = {}

    for row in records:

        if calculate_pm25_aqi(row["pm2_5"]) is None:
            continue

        if row["city"] not in readings_by_city:
            readings_by_city[row["city"]] = []

        readings_by_city[row["city"]].append(row)

    # Every question comes from a different city.
    city_names = sorted(readings_by_city)
    chosen_cities = generator.sample(city_names, min(count, len(city_names)))

    questions = []

    for city in chosen_cities:
        reading = generator.choice(readings_by_city[city])

        questions.append({
            "reading": reading,
            "answer": calculate_pm25_aqi(reading["pm2_5"])
        })

    return questions


# -----------------------------------------
# THE CLUES SHOWN TO THE PLAYER
# -----------------------------------------

def describe_clues(reading):

    # Only weather and time clues. The pollution values stay hidden.
    return (
        "City: " + reading["city"] + "\n"
        + "Date and time: " + reading["timestamp"]
        + "  (" + reading["day_of_week"] + ")\n"
        + "Season: " + reading["season"] + "\n"
        + "Temperature: " + str(reading["temperature"]) + " °C     "
        + "Humidity: " + str(reading["humidity"]) + " %\n"
        + "Wind speed: " + str(reading["wind_speed"]) + "     "
        + "Pressure: " + str(reading["pressure"]) + " hPa\n"
        + "Rain: " + str(reading["precipitation"]) + " mm"
    )


# -----------------------------------------
# CHECK A GUESS
# -----------------------------------------

def check_guess(guess, answer, tolerance=TOLERANCE):

    # Close enough counts as correct.
    if abs(guess - answer) <= tolerance:
        return "correct"

    # Guess too small: the real answer is higher.
    if guess < answer:
        return "higher"

    return "lower"


# -----------------------------------------
# POINTS: FEWER TRIES = MORE POINTS
# -----------------------------------------

def points_for_try(try_number):

    if 1 <= try_number <= TRIES_PER_QUESTION:
        return TRIES_PER_QUESTION - try_number + 1

    return 0


# -----------------------------------------
# NARROW DOWN THE POSSIBLE RANGE
# -----------------------------------------

def narrow_range(low, high, guess, result, tolerance=TOLERANCE):

    # "higher" means the answer is more than guess + tolerance.
    if result == "higher":
        low = max(low, guess + tolerance + 1)

    # "lower" means the answer is less than guess - tolerance.
    elif result == "lower":
        high = min(high, guess - tolerance - 1)

    return low, high


# -----------------------------------------
# RANK FROM THE FINAL SCORE
# -----------------------------------------

def get_rank(total, maximum):

    share = total / maximum

    if share >= 0.8:
        return "AQI Expert"
    elif share >= 0.5:
        return "Air Aware"
    elif share >= 0.2:
        return "Getting the hang of it"
    else:
        return "Keep practising"