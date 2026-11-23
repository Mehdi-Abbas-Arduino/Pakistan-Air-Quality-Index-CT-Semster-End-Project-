# ============================================================
# AQI CALCULATOR MODULE
# ============================================================
# Converts valid 24-hour PM2.5 concentration averages into a
# US EPA 2024 PM2.5 AQI estimate and provides related helpers.
# ============================================================

from recursion_tools import recursive_sum

# 2024 US EPA PM2.5 breakpoints:
# (lowest concentration, highest concentration, lowest AQI, highest AQI)
PM25_BREAKPOINTS = [
    (0.0, 9.0, 0, 50),
    (9.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 125.4, 151, 200),
    (125.5, 225.4, 201, 300),
    (225.5, 325.4, 301, 400),
    (325.5, 500.4, 401, 500),
]


def calculate_pm25_aqi(pm25):
    """Convert a 24-hour PM2.5 mean (µg/m³) to a 2024 US EPA AQI estimate.

    The EPA concentration is truncated to one decimal place before
    interpolation. This function does not turn an hourly reading into
    a 24-hour average; callers must provide an appropriate average.
    """
    if pm25 is None:
        return None

    try:
        pm25 = float(pm25)
    except (TypeError, ValueError):
        return None

    if pm25 != pm25 or pm25 < 0 or pm25 > 500.4:
        return None

    # Truncate concentration to one decimal place, as required by the method.
    pm25 = int((pm25 + 1e-10) * 10) / 10

    for c_low, c_high, i_low, i_high in PM25_BREAKPOINTS:
        if c_low <= pm25 <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
            return round(aqi)

    return None


def get_aqi_category(aqi):
    """Convert a numeric AQI into its human-readable category."""
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
    return "Hazardous"


def get_average_aqi(readings):
    """Calculate the average AQI across supplied PM2.5 averages."""
    aqi_values = []
    for row in readings:
        aqi = calculate_pm25_aqi(row["pm2_5"])
        if aqi is not None:
            aqi_values.append(aqi)
    if not aqi_values:
        return None
    return round(recursive_sum(aqi_values) / len(aqi_values))


def get_worst_reading(readings):
    """Return the reading with the highest calculated AQI and that AQI."""
    worst_row = None
    worst_aqi = None
    for row in readings:
        aqi = calculate_pm25_aqi(row["pm2_5"])
        if aqi is not None and (worst_aqi is None or aqi > worst_aqi):
            worst_row = row
            worst_aqi = aqi
    return worst_row, worst_aqi


HEALTH_ADVICE = {
    "Good": "Air quality is satisfactory. Enjoy your outdoor activities.",
    "Moderate": "Acceptable for most people. Unusually sensitive people should consider reducing long outdoor exertion.",
    "Unhealthy for Sensitive Groups": "Children, older adults and people with heart or lung conditions should limit long outdoor exertion.",
    "Unhealthy": "Everyone may start to feel health effects. Limit long outdoor exertion; sensitive groups should stay indoors.",
    "Very Unhealthy": "Health alert. Avoid outdoor exertion, and wear a well-fitted N95 mask if you must go outside.",
    "Hazardous": "Emergency conditions. Stay indoors with windows closed and avoid all outdoor activity.",
}


def get_health_advice(category):
    """Return the advice associated with an AQI category."""
    return HEALTH_ADVICE.get(category, "")
