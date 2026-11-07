from data_loader import (
    load_dataset,
    get_available_cities,
    get_city_readings,
    get_latest_city_reading
)

from aqi_calculator import (
    calculate_pm25_aqi,
    get_aqi_category,
    get_average_aqi,
    get_worst_reading
)

# Load the complete dataset.
records = load_dataset()

# Display the total number of records.
print("Total Records:", len(records))

# Get all available cities.
cities = get_available_cities(records)

print("\nAvailable Cities:")
print(cities)

# Select a city.
selected_city = "Multan"

# Retrieve all readings for that city.
readings = get_city_readings(records, selected_city)

print("\nTotal Readings:", len(readings))

# Retrieve its latest reading.
latest = get_latest_city_reading(records, selected_city)

print("\nLatest Reading:")
print(latest)

# Calculate the AQI of the latest reading.
latest_aqi = calculate_pm25_aqi(latest["pm2_5"])

print("\nLatest AQI:", latest_aqi, "-", get_aqi_category(latest_aqi))

# Average AQI across every reading for this city.
average_aqi = get_average_aqi(readings)

print("Average AQI:", average_aqi, "-", get_aqi_category(average_aqi))

# Worst hour recorded for this city.
worst_row, worst_aqi = get_worst_reading(readings)

print("Worst AQI:", worst_aqi, "-", get_aqi_category(worst_aqi),
      "at", worst_row["timestamp"])