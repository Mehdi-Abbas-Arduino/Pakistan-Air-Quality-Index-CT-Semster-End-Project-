# ============================================================
# AQI CALCULATOR MODULE
# ============================================================
# This module converts PM2.5 concentration values into the
# official US EPA Air Quality Index (AQI) and provides related
# helper functions (category, health advice, average, worst reading).
# ============================================================

from recursion_tools import recursive_sum

# ----------------------------------------------------------
# US EPA PM2.5 BREAKPOINTS (official table)
# ----------------------------------------------------------
# Each row contains:
#   (lowest PM2.5, highest PM2.5, lowest AQI, highest AQI)
#
# The AQI is calculated by finding which range the PM2.5 value
# falls into, then performing linear interpolation inside that range.

PM25_BREAKPOINTS = [
    (0.0,   12.0,    0,   50),     # Good
    (12.1,  35.4,   51,  100),     # Moderate
    (35.5,  55.4,  101,  150),     # Unhealthy for Sensitive Groups
    (55.5,  150.4, 151,  200),     # Unhealthy
    (150.5, 250.4, 201,  300),     # Very Unhealthy
    (250.5, 350.4, 301,  400),     # Hazardous
    (350.5, 500.4, 401,  500),     # Hazardous (higher)
]


# ----------------------------------------------------------
# CALCULATE AQI FROM A SINGLE PM2.5 VALUE
# ----------------------------------------------------------
def calculate_pm25_aqi(pm25):
    """
    Convert a PM2.5 concentration (µg/m³) into a US EPA AQI value.

    Returns:
        int  → AQI number (0-500)
        None → if the value is missing or outside the valid range
    """
    # Cannot calculate AQI if the reading is missing
    if pm25 is None:
        return None

    # EPA table uses one decimal place
    pm25 = round(pm25, 1)

    # Find the correct breakpoint range and interpolate
    for c_low, c_high, i_low, i_high in PM25_BREAKPOINTS:
        if c_low <= pm25 <= c_high:
            # Linear interpolation formula used by the EPA
            aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
            return round(aqi)

    # Value is outside the official table (negative or > 500.4)
    return None


# ----------------------------------------------------------
# GET THE HUMAN-READABLE CATEGORY FOR AN AQI VALUE
# ----------------------------------------------------------
def get_aqi_category(aqi):
    """
    Convert a numeric AQI into its official category name.
    """
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


# ----------------------------------------------------------
# CALCULATE AVERAGE AQI FOR A LIST OF READINGS
# ----------------------------------------------------------
def get_average_aqi(readings):
    """
    Calculate the average AQI across many readings.
    Uses recursive_sum (from recursion_tools) to demonstrate recursion.
    """
    aqi_values = []

    for row in readings:
        aqi = calculate_pm25_aqi(row["pm2_5"])
        if aqi is not None:
            aqi_values.append(aqi)

    if len(aqi_values) == 0:
        return None

    # Average = total / count  (total is calculated recursively)
    return round(recursive_sum(aqi_values) / len(aqi_values))


# ----------------------------------------------------------
# FIND THE WORST (HIGHEST AQI) READING
# ----------------------------------------------------------
def get_worst_reading(readings):
    """
    Return the reading that has the highest AQI together with its AQI value.
    """
    worst_row = None
    worst_aqi = None

    for row in readings:
        aqi = calculate_pm25_aqi(row["pm2_5"])

        if aqi is None:
            continue

        if worst_aqi is None or aqi > worst_aqi:
            worst_row = row
            worst_aqi = aqi

    return worst_row, worst_aqi


# ----------------------------------------------------------
# HEALTH ADVICE FOR EACH AQI CATEGORY
# ----------------------------------------------------------
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
    """
    Return the recommended health advice for a given AQI category.
    """
    return HEALTH_ADVICE.get(category, "")
