import tkinter as tk  # importing important libraries
from tkinter import ttk

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


# -----------------------------------------
# CATEGORY COLORS (standard AQI colors)
# -----------------------------------------

# Each category maps to (background color, text color).
CATEGORY_COLORS = {
    "Good":                           ("#00E400", "black"),
    "Moderate":                       ("#FFFF00", "black"),
    "Unhealthy for Sensitive Groups": ("#FF7E00", "black"),
    "Unhealthy":                      ("#FF0000", "white"),
    "Very Unhealthy":                 ("#8F3F97", "white"),
    "Hazardous":                      ("#7E0023", "white"),
}


# -----------------------------------------
# LOAD DATA ONCE WHEN THE PROGRAM STARTS
# -----------------------------------------

records = load_dataset()
cities = get_available_cities(records)


# -----------------------------------------
# WINDOW SETUP
# -----------------------------------------

window = tk.Tk()
window.title("Pakistan Air Quality Index")
window.geometry("420x420")

# Variables that the labels display. Changing them updates the screen.
city_text = tk.StringVar()
time_text = tk.StringVar()
pm25_text = tk.StringVar()
pm10_text = tk.StringVar()
average_text = tk.StringVar()
worst_text = tk.StringVar()


# -----------------------------------------
# UPDATE THE SCREEN FOR A SELECTED CITY
# -----------------------------------------

def show_city(event=None):

    # Read the city currently selected in the dropdown.
    city = city_text.get()

    # Get the data for that city.
    readings = get_city_readings(records, city)
    latest = get_latest_city_reading(records, city)

    # Calculate the AQI values.
    latest_aqi = calculate_pm25_aqi(latest["pm2_5"])
    category = get_aqi_category(latest_aqi)
    average_aqi = get_average_aqi(readings)
    worst_row, worst_aqi = get_worst_reading(readings)

    # Big AQI box: show the number and color it by category.
    background, text_color = CATEGORY_COLORS[category]
    aqi_label.config(text=str(latest_aqi), bg=background, fg=text_color)
    category_label.config(text=category, bg=background, fg=text_color)

    # Smaller details below it.
    time_text.set("Latest reading: " + latest["timestamp"])
    pm25_text.set("PM2.5: " + str(latest["pm2_5"]) + " µg/m³")
    pm10_text.set("PM10: " + str(latest["pm10"]) + " µg/m³")
    average_text.set("Average AQI: " + str(average_aqi)
                     + " (" + get_aqi_category(average_aqi) + ")")
    worst_text.set("Worst AQI: " + str(worst_aqi)
                   + " on " + worst_row["timestamp"])


# -----------------------------------------
# WIDGETS
# -----------------------------------------

tk.Label(window, text="Select a city:", font=("Arial", 12)).pack(pady=(15, 5))

# Dropdown list of cities.
city_menu = ttk.Combobox(
    window,
    textvariable=city_text,
    values=cities,
    state="readonly",
    width=25
)
city_menu.pack()

# When the user picks a city, update the screen.
city_menu.bind("<<ComboboxSelected>>", show_city)

# Large AQI number.
aqi_label = tk.Label(window, text="--", font=("Arial", 48, "bold"),
                     width=8, bg="lightgray")
aqi_label.pack(pady=(20, 0))

# Category name under the number.
category_label = tk.Label(window, text="Choose a city", font=("Arial", 14),
                          width=30, bg="lightgray")
category_label.pack()

# Detail lines.
for variable in (time_text, pm25_text, pm10_text, average_text, worst_text):
    tk.Label(window, textvariable=variable, font=("Arial", 11)).pack(pady=2)

# Start with the first city selected.
city_menu.current(0)
show_city()


# -----------------------------------------
# START THE PROGRAM
# -----------------------------------------

if __name__ == "__main__":
    window.mainloop()