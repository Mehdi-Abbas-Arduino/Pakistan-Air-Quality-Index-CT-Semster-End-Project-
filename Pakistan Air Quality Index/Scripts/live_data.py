import json
import urllib.request
import urllib.error

'''
• fetch_live_city_reading: Calls the Open-Meteo API for a city's current PM2.5, PM10 and dust, and returns a dict shaped like a dataset record so the rest of the code treats it the same way. It raises a clear error on a bad city or no internet.
'''

# Coordinates for major Pakistani cities
CITY_COORDINATES = {
    "Karachi": (24.8607, 67.0011),
    "Lahore": (31.5204, 74.3587),
    "Islamabad": (33.6844, 73.0479),
    "Peshawar": (34.0151, 71.5249),
    "Quetta": (30.1798, 66.9750),
    "Multan": (30.1575, 71.5249),
    "Faisalabad": (31.4504, 73.1350),
    "Rawalpindi": (33.5651, 73.0169),
    "Hyderabad": (25.3960, 68.3578),
    "Gujranwala": (32.1877, 74.1945),
    "Sialkot": (32.4945, 74.5229),
    "Abbottabad": (34.1688, 73.2215)
}

def fetch_live_city_reading(city_name):
    """
    Fetches real-time PM2.5, PM10, and dust data from Open-Meteo API.
    Returns a dictionary structured like a dataset record.
    """
    # Match city name regardless of casing
    matched_city = None
    for name in CITY_COORDINATES:
        if name.lower() == city_name.strip().lower():
            matched_city = name
            break

    if not matched_city:
        raise ValueError(f"Live data is not available for '{city_name}'. Available live cities: " + ", ".join(sorted(CITY_COORDINATES.keys())))

    lat, lon = CITY_COORDINATES[matched_city]
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5,pm10,dust"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                current = data.get("current", {})

                # Construct a dataset-compatible reading dictionary
                return {
                    "city": matched_city,
                    "timestamp": current.get("time", "Live Now").replace("T", " "),
                    "date": current.get("time", "Live").split("T")[0],
                    "hour": current.get("time", "00:00").split("T")[-1].split(":")[0],
                    "pm2_5": current.get("pm2_5"),
                    "pm10": current.get("pm10"),
                    "dust": current.get("dust"),
                    "temperature": None,
                    "humidity": None,
                    "is_live": True
                }
    except urllib.error.URLError as e:
        raise ValueError("Could not connect to live air quality service. Please check your internet connection.")
    except Exception as e:
        raise ValueError(f"Error retrieving live data: {str(e)}")