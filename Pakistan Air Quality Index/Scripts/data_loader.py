
import csv


# -----------------------------------------
# NUMERIC COLUMNS
# -----------------------------------------

# These columns contain numerical air-quality or weather readings.
# We will convert their values from strings into floats.

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


# -----------------------------------------
# LOAD DATASET
# -----------------------------------------

def load_dataset(file_path="Dataset/pakistan_air_quality_final_clean_v2.csv"):

    # Create an empty list to store all dataset records.
    records = []

    # Open the CSV file in read mode.
    with open(file_path, "r", encoding="utf-8", newline="") as file:

        # DictReader converts every row into a dictionary.
        reader = csv.DictReader(file)

        # Check whether the required columns exist.
        required_columns = ["city", "timestamp", "pm2_5", "pm10"]

        for column in required_columns:
            if column not in reader.fieldnames:
                raise ValueError(f"Missing required column: {column}")

        # Go through every row in the dataset.
        for row in reader:

            # Remove extra spaces from the city name.
            row["city"] = row["city"].strip()

            # Convert numerical readings from strings into floats.
            for column in NUMERIC_COLUMNS:

                # Get the value from the current row.
                value = row[column].strip()

                # Handle missing numerical values.
                if value == "":
                    row[column] = None

                else:
                    # Convert the value into a floating-point number.
                    row[column] = float(value)

            # Add the processed row to our records list.
            records.append(row)

    # Return all the dataset records.
    return records


# -----------------------------------------
# GET AVAILABLE CITIES
# -----------------------------------------

def get_available_cities(records):

    # Create an empty list for storing city names.
    cities = []

    # Go through every record.
    for row in records:

        # Get the city name from the current record.
        city = row["city"]

        # Only add the city if it is not already in the list.
        if city not in cities:
            cities.append(city)

    # Sort the city names alphabetically.
    cities.sort()

    # Return the list of unique cities.
    return cities


# -----------------------------------------
# GET READINGS FOR A SELECTED CITY
# -----------------------------------------

def get_city_readings(records, selected_city):

    # Create an empty list for the selected city's readings.
    city_readings = []

    # Go through every record in the dataset.
    for row in records:

        # Compare the current city with the selected city.
        if row["city"].lower() == selected_city.strip().lower():

            # Add the matching record to the list.
            city_readings.append(row)

    # Return all matching records.
    return city_readings


# -----------------------------------------
# GET LATEST READING FOR A CITY
# -----------------------------------------

def get_latest_city_reading(records, selected_city):

    # Retrieve all readings belonging to the selected city.
    city_readings = get_city_readings(records, selected_city)

    # Check whether the city exists in the dataset.
    if len(city_readings) == 0:
        return None

    # Find the record with the latest timestamp.
    latest_reading = max(
        city_readings,
        key=lambda row: row["timestamp"]
    )

    # Return the latest record.
    return latest_reading
