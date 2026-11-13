from recursion_tools import recursive_sum
'''
• calculate_pm25_aqi: Converts a PM2.5 value to an AQI using the EPA breakpoint table and linear interpolation. It returns None for missing or out-of-range values.
• get_aqi_category: Maps an AQI number to a label (Good, Moderate, ... Hazardous).
• get_average_aqi: Computes the AQI of each reading, skips invalid ones, and averages them. It uses recursive_sum for the total.
• get_worst_reading: Finds the reading with the highest AQI.
• get_health_advice: Looks up the advice text for a category.

'''

# -----------------------------------------
# PM2.5 BREAKPOINTS (US EPA)
# -----------------------------------------

# Each row is:
# (lowest PM2.5, highest PM2.5, lowest AQI, highest AQI)
#
# The AQI is calculated by finding which row the PM2.5 value
# falls into, then placing it proportionally inside that AQI range.

PM25_BREAKPOINTS = [
    (0.0,   12.0,    0,   50),
    (12.1,  35.4,   51,  100),
    (35.5,  55.4,  101,  150),
    (55.5,  150.4, 151,  200),
    (150.5, 250.4, 201,  300),
    (250.5, 350.4, 301,  400),
    (350.5, 500.4, 401,  500),
]


# -----------------------------------------
# CALCULATE AQI FROM PM2.5
# -----------------------------------------

def calculate_pm25_aqi(pm25):

    # A missing reading cannot produce an AQI.
    if pm25 is None:
        return None

    # The breakpoint table uses one decimal place.
    pm25 = round(pm25, 1)

    # Go through every breakpoint row.
    for c_low, c_high, i_low, i_high in PM25_BREAKPOINTS:

        # Check whether the PM2.5 value falls inside this row.
        if c_low <= pm25 <= c_high:

            # Linear interpolation formula used by the EPA.
            aqi = (i_high - i_low) / (c_high - c_low) * (pm25 - c_low) + i_low

            # Return the AQI as a whole number.
            return round(aqi)

    # The value is outside the table (negative, or above 500.4).
    return None


# -----------------------------------------
# GET AQI CATEGORY
# -----------------------------------------

def get_aqi_category(aqi):

    if aqi is None:
        return None

    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# -----------------------------------------
# AVERAGE AQI FOR A LIST OF READINGS
# -----------------------------------------

def get_average_aqi(readings):

    # Collect the AQI of every reading that has a valid PM2.5 value.
    aqi_values = []

    for row in readings:
        aqi = calculate_pm25_aqi(row["pm2_5"])

        # Skip readings where the AQI could not be calculated.
        if aqi is not None:
            aqi_values.append(aqi)

    # No valid readings means no average.
    if len(aqi_values) == 0:
        return None

    # Average = total divided by count.
    # The total is added up with recursion (see recursion_tools.py).
    return round(recursive_sum(aqi_values) / len(aqi_values))


# -----------------------------------------
# WORST (HIGHEST AQI) READING
# -----------------------------------------

def get_worst_reading(readings):

    worst_row = None
    worst_aqi = None

    for row in readings:
        aqi = calculate_pm25_aqi(row["pm2_5"])

        # Skip readings without a valid AQI.
        if aqi is None:
            continue

        # Keep this reading if it is the highest AQI seen so far.
        if worst_aqi is None or aqi > worst_aqi:
            worst_row = row
            worst_aqi = aqi

    # Return both the reading and its AQI.
    return worst_row, worst_aqi


# -----------------------------------------
# HEALTH ADVICE FOR EACH CATEGORY
# -----------------------------------------

HEALTH_ADVICE = {
    "Good":
        "Air quality is satisfactory. Enjoy your outdoor activities.",
    "Moderate":
        "Acceptable for most people. Unusually sensitive people should "
        "consider reducing long outdoor exertion.",
    "Unhealthy for Sensitive Groups":
        "Children, older adults and people with heart or lung conditions "
        "should limit long outdoor exertion.",
    "Unhealthy":
        "Everyone may start to feel health effects. Limit long outdoor "
        "exertion; sensitive groups should stay indoors.",
    "Very Unhealthy":
        "Health alert. Avoid outdoor exertion, and wear a well-fitted "
        "N95 mask if you must go outside.",
    "Hazardous":
        "Emergency conditions. Stay indoors with windows closed and "
        "avoid all outdoor activity.",
}


def get_health_advice(category):

    # Unknown or missing categories return an empty string.
    return HEALTH_ADVICE.get(category, "")