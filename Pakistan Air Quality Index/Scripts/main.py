
from data_loader import (
    load_dataset,
    get_available_cities,
    get_city_readings,
    get_latest_city_reading
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
