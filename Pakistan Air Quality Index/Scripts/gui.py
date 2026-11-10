import tkinter as tk
from tkinter import ttk

from data_loader import (
    load_dataset,
    get_available_cities,
    get_city_readings,
    get_latest_city_reading,
    get_city_reading_at,
    get_date_range
)

from aqi_calculator import (
    calculate_pm25_aqi,
    get_aqi_category,
    get_average_aqi,
    get_worst_reading,
    get_health_advice
)

from validation import (
    validate_city,
    validate_date,
    validate_hour,
    validate_pm25,
    validate_guess
)

from recursion_tools import total_score

from quiz import (
    QUESTION_COUNT,
    TRIES_PER_QUESTION,
    TOLERANCE,
    MAX_AQI,
    build_questions,
    describe_clues,
    check_guess,
    points_for_try,
    narrow_range,
    get_rank
)

from live_data import fetch_live_city_reading


# -----------------------------------------
# LOOK AND FEEL
# -----------------------------------------

FONT = "Segoe UI"

DARK = "#1f2937"        # header and main text
MUTED = "#6b7280"       # small grey text
PAGE_BG = "#f3f4f6"     # window background
CARD_BG = "white"
BORDER = "#d1d5db"
EMPTY_BG = "#e5e7eb"    # result banner before any result
ERROR_RED = "#b91c1c"
BUTTON_BLUE = "#2563eb"
LIVE_GREEN = "#16a34a"

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
first_date, last_date = get_date_range(records)


# -----------------------------------------
# WINDOW SETUP
# -----------------------------------------

window = tk.Tk()
window.title("Pakistan Air Quality Index")
window.geometry("800x820")
window.minsize(760, 760)
window.configure(bg=PAGE_BG)

# Style the tabs.
style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=PAGE_BG, borderwidth=0)
style.configure("TNotebook.Tab", font=(FONT, 11), padding=(18, 8))

# Header bar at the top.
header = tk.Frame(window, bg=DARK)
header.pack(fill="x")

tk.Label(header, text="Pakistan Air Quality Index", font=(FONT, 20, "bold"),
         bg=DARK, fg="white").pack(anchor="w", padx=20, pady=(14, 0))

tk.Label(header,
         text=str(len(cities)) + " cities  ·  historical dataset (" + first_date
              + " to " + last_date + ") + Realtime API",
         font=(FONT, 10), bg=DARK, fg="#9ca3af").pack(anchor="w", padx=20, pady=(0, 14))

# Tabs.
tabs = ttk.Notebook(window)
tabs.pack(fill="both", expand=True, padx=10, pady=10)

city_tab = tk.Frame(tabs, bg=PAGE_BG)
calculator_tab = tk.Frame(tabs, bg=PAGE_BG)
compare_tab = tk.Frame(tabs, bg=PAGE_BG)
quiz_tab = tk.Frame(tabs, bg=PAGE_BG)

tabs.add(city_tab, text="  City Check  ")
tabs.add(calculator_tab, text="  AQI Calculator  ")
tabs.add(compare_tab, text="  Compare Cities  ")
tabs.add(quiz_tab, text="  AQI Quiz  ")


# -----------------------------------------
# SMALL HELPER FUNCTIONS
# -----------------------------------------

def fmt(value):
    if value is None:
        return "n/a"
    return str(value)


def make_button(parent, text, command, bg_color=BUTTON_BLUE):
    return tk.Button(parent, text=text, command=command,
                     font=(FONT, 10, "bold"), bg=bg_color, fg="white",
                     activebackground="#1d4ed8", activeforeground="white",
                     relief="flat", padx=14, pady=6, cursor="hand2")


def make_label(parent, text):
    return tk.Label(parent, text=text, font=(FONT, 10, "bold"),
                    bg=CARD_BG, fg=MUTED)


# -----------------------------------------
# RESULT CARD
# -----------------------------------------

def make_result_card(parent):
    frame = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER,
                     highlightthickness=1)

    banner = tk.Frame(frame, bg=EMPTY_BG)
    banner.pack(fill="x")

    aqi_label = tk.Label(banner, text="--", font=(FONT, 52, "bold"),
                         bg=EMPTY_BG, fg=DARK)
    aqi_label.pack(pady=(14, 0))

    category_label = tk.Label(banner, text="No result yet", font=(FONT, 15),
                              bg=EMPTY_BG, fg=DARK)
    category_label.pack(pady=(0, 14))

    advice_label = tk.Label(frame, text="", font=(FONT, 11, "italic"),
                            bg=CARD_BG, fg=DARK, wraplength=680,
                            justify="center")
    advice_label.pack(pady=(12, 4), padx=16)

    details_label = tk.Label(frame, text="", font=(FONT, 10),
                             bg=CARD_BG, fg=MUTED, justify="center")
    details_label.pack(pady=(0, 12))

    return {"frame": frame, "banner": banner, "aqi": aqi_label, "category": category_label,
            "advice": advice_label, "details": details_label}


def show_result(card, aqi, details):
    category = get_aqi_category(aqi)
    background, text_color = CATEGORY_COLORS[category]

    card["banner"].config(bg=background)
    card["aqi"].config(text=str(aqi), bg=background, fg=text_color)
    card["category"].config(text=category, bg=background, fg=text_color)
    card["advice"].config(text=get_health_advice(category))
    card["details"].config(text=details)


def clear_result(card):
    card["banner"].config(bg=EMPTY_BG)
    card["aqi"].config(text="--", bg=EMPTY_BG, fg=DARK)
    card["category"].config(text="No result yet", bg=EMPTY_BG, fg=DARK)
    card["advice"].config(text="")
    card["details"].config(text="")


# -----------------------------------------
# TAB 1: CITY CHECK
# -----------------------------------------

city_text = tk.StringVar(value="Lahore")
date_text = tk.StringVar(value=last_date)
hour_text = tk.StringVar(value="12")

inputs = tk.Frame(city_tab, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
inputs.pack(fill="x", padx=10, pady=(10, 6))

make_label(inputs, "City").grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))
make_label(inputs, "Date (YYYY-MM-DD)").grid(row=0, column=1, sticky="w", padx=14, pady=(12, 2))
make_label(inputs, "Hour (0-23)").grid(row=0, column=2, sticky="w", padx=14, pady=(12, 2))

city_box = ttk.Combobox(inputs, textvariable=city_text, values=cities, width=18, font=(FONT, 11))
city_box.grid(row=1, column=0, padx=14, pady=(0, 14))

date_box = ttk.Entry(inputs, textvariable=date_text, width=14, font=(FONT, 11))
date_box.grid(row=1, column=1, padx=14, pady=(0, 14))

hour_box = ttk.Spinbox(inputs, from_=0, to=23, textvariable=hour_text, width=6, font=(FONT, 11))
hour_box.grid(row=1, column=2, padx=14, pady=(0, 14))

city_error = tk.Label(city_tab, text="", font=(FONT, 10, "bold"), bg=PAGE_BG, fg=ERROR_RED, wraplength=720, justify="left")
city_result = make_result_card(city_tab)


def show_reading(city, reading):
    aqi = calculate_pm25_aqi(reading["pm2_5"])

    if aqi is None:
        clear_result(city_result)
        city_error.config(text="This reading has no valid PM2.5 value, so its AQI cannot be calculated.")
        return

    # Handle display differences between historical dataset and live data
    if reading.get("is_live"):
        details = (
            f"⚡ REALTIME LIVE API DATA · {city} · {reading['timestamp']}\n"
            + f"PM2.5 {fmt(reading['pm2_5'])} µg/m³     "
            + f"PM10 {fmt(reading['pm10'])} µg/m³     "
            + f"Dust {fmt(reading['dust'])} µg/m³"
        )
    else:
        readings = get_city_readings(records, city)
        average_aqi = get_average_aqi(readings)
        worst_row, worst_aqi = get_worst_reading(readings)

        details = (
            city + "  ·  " + reading["timestamp"] + "\n"
            + "PM2.5 " + fmt(reading["pm2_5"]) + " µg/m³     "
            + "PM10 " + fmt(reading["pm10"]) + " µg/m³     "
            + "Temp " + fmt(reading["temperature"]) + " °C     "
            + "Humidity " + fmt(reading["humidity"]) + " %\n"
            + city + " overall dataset: average AQI " + str(average_aqi)
            + " (" + get_aqi_category(average_aqi) + "), worst "
            + str(worst_aqi) + " on " + worst_row["timestamp"]
        )

    show_result(city_result, aqi, details)


def check_time(event=None):
    city_error.config(text="")
    try:
        city = validate_city(city_text.get(), cities)
        date = validate_date(date_text.get(), first_date, last_date)
        hour = validate_hour(hour_text.get())
    except ValueError as problem:
        city_error.config(text="⚠  " + str(problem))
        clear_result(city_result)
        return

    city_text.set(city)
    date_text.set(date)
    hour_text.set(str(hour))

    reading = get_city_reading_at(records, city, date, hour)
    if reading is None:
        city_error.config(text=f"⚠  No reading found for {city} on {date} at hour {hour}.")
        clear_result(city_result)
        return

    show_reading(city, reading)


def show_latest(event=None):
    city_error.config(text="")
    try:
        city = validate_city(city_text.get(), cities)
    except ValueError as problem:
        city_error.config(text="⚠  " + str(problem))
        clear_result(city_result)
        return

    latest = get_latest_city_reading(records, city)
    city_text.set(city)
    date_text.set(latest["date"])
    hour_text.set(str(int(latest["hour"])))

    show_reading(city, latest)


def show_live_api(event=None):
    city_error.config(text="")
    raw_city = city_text.get().strip()

    try:
        live_reading = fetch_live_city_reading(raw_city)
        city_text.set(live_reading["city"])
        show_reading(live_reading["city"], live_reading)
    except ValueError as problem:
        city_error.config(text="⚠  " + str(problem))
        clear_result(city_result)


button_row = tk.Frame(inputs, bg=CARD_BG)
button_row.grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=(0, 14))

make_button(button_row, "Check Date/Hour", check_time).pack(side="left", padx=(0, 8))
make_button(button_row, "Latest in Dataset", show_latest).pack(side="left", padx=(0, 8))
make_button(button_row, "⚡ Fetch Live Data (API)", show_live_api, bg_color=LIVE_GREEN).pack(side="left")

city_error.pack(anchor="w", padx=12, pady=(0, 2))
city_result["frame"].pack(fill="x", padx=10, pady=6)

for box in (city_box, date_box, hour_box):
    box.bind("<Return>", check_time)


# -----------------------------------------
# TAB 2: AQI CALCULATOR
# -----------------------------------------

pm25_text = tk.StringVar()

calc_inputs = tk.Frame(calculator_tab, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
calc_inputs.pack(fill="x", padx=10, pady=(10, 6))

make_label(calc_inputs, "PM2.5 value (µg/m³)").grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))

pm25_box = ttk.Entry(calc_inputs, textvariable=pm25_text, width=18, font=(FONT, 11))
pm25_box.grid(row=1, column=0, padx=14, pady=(0, 14))

calc_error = tk.Label(calculator_tab, text="", font=(FONT, 10, "bold"), bg=PAGE_BG, fg=ERROR_RED, wraplength=720, justify="left")
calc_result = make_result_card(calculator_tab)


def calculate_from_input(event=None):
    calc_error.config(text="")
    try:
        pm25 = validate_pm25(pm25_text.get())
    except ValueError as problem:
        calc_error.config(text="⚠  " + str(problem))
        clear_result(calc_result)
        return

    aqi = calculate_pm25_aqi(pm25)
    show_result(calc_result, aqi, "PM2.5 = " + str(pm25) + " µg/m³")


make_button(calc_inputs, "Calculate", calculate_from_input).grid(row=1, column=1, padx=(0, 14), pady=(0, 14))

tk.Label(calculator_tab, text="Type any PM2.5 reading (0 to 500.4) to see its AQI and health advice.",
         font=(FONT, 10), bg=PAGE_BG, fg=MUTED).pack(anchor="w", padx=12)

calc_error.pack(anchor="w", padx=12, pady=(2, 2))
calc_result["frame"].pack(fill="x", padx=10, pady=6)

pm25_box.bind("<Return>", calculate_from_input)


# -----------------------------------------
# TAB 3: COMPARE CITIES (bar chart)
# -----------------------------------------

tk.Label(compare_tab, text="Average AQI by city (every reading in the dataset)",
         font=(FONT, 13, "bold"), bg=PAGE_BG, fg=DARK).pack(anchor="w", padx=14, pady=(14, 4))

chart = tk.Canvas(compare_tab, width=720, height=430, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
chart.pack(padx=10, pady=6)


def draw_city_chart():
    chart.delete("all")
    rows = []

    for city in cities:
        average = get_average_aqi(get_city_readings(records, city))
        rows.append((city, average))

    rows.sort(key=lambda item: item[1], reverse=True)

    biggest = rows[0][1]
    label_space = 145
    value_space = 60
    row_height = 36
    chart_width = int(chart["width"])

    for position, (city, average) in enumerate(rows):
        top = 14 + position * row_height
        bar_length = (chart_width - label_space - value_space) * average / biggest
        background, text_color = CATEGORY_COLORS[get_aqi_category(average)]

        chart.create_text(label_space - 10, top + 12, text=city, anchor="e", font=(FONT, 11), fill=DARK)
        chart.create_rectangle(label_space, top, label_space + bar_length, top + 26, fill=background, outline="")
        chart.create_text(label_space + bar_length + 8, top + 12, text=str(average), anchor="w", font=(FONT, 11, "bold"), fill=DARK)

    legend_y = 14 + len(rows) * row_height + 12
    legend_x = 14

    for category, (background, text_color) in CATEGORY_COLORS.items():
        chart.create_rectangle(legend_x, legend_y, legend_x + 14, legend_y + 14, fill=background, outline="")
        short_name = category.replace("Unhealthy for Sensitive Groups", "Sensitive")
        chart.create_text(legend_x + 20, legend_y + 7, text=short_name, anchor="w", font=(FONT, 9), fill=MUTED)
        legend_x += 28 + len(short_name) * 7


draw_city_chart()


# -----------------------------------------
# TAB 4: AQI QUIZ (FIXED INPUT & FLOW)
# -----------------------------------------

quiz_state = {
    "questions": [],
    "number": 0,
    "tries_used": 0,
    "low": 0,
    "high": MAX_AQI,
    "scores": [],
    "guesses": [],
    "summary": [],
    "active": False,
}

guess_text = tk.StringVar()

HIGHER_BLUE = "#1d4ed8"
LOWER_ORANGE = "#c2410c"
CORRECT_GREEN = "#15803d"

quiz_status = tk.Label(quiz_tab, text="", font=(FONT, 12, "bold"), bg=PAGE_BG, fg=DARK)
quiz_status.pack(anchor="w", padx=14, pady=(12, 2))

clue_panel = tk.Label(quiz_tab, text="", font=(FONT, 12), bg=DARK, fg="white", justify="left", anchor="nw", padx=20, pady=14, height=9)
clue_panel.pack(fill="x", padx=10, pady=6)

range_label = tk.Label(quiz_tab, text="", font=(FONT, 11), bg=PAGE_BG, fg=MUTED)
range_label.pack(anchor="w", padx=14)

guess_row = tk.Frame(quiz_tab, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
guess_row.pack(fill="x", padx=10, pady=8)

make_label(guess_row, "Your guess (AQI 0-500)").grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))

guess_box = ttk.Entry(guess_row, textvariable=guess_text, width=12, font=(FONT, 12))
guess_box.grid(row=1, column=0, padx=14, pady=(0, 12))

feedback_label = tk.Label(quiz_tab, text="", font=(FONT, 16, "bold"), bg=PAGE_BG, fg=MUTED, wraplength=720)
feedback_label.pack(pady=(2, 0))

history_label = tk.Label(quiz_tab, text="", font=(FONT, 11), bg=PAGE_BG, fg=MUTED)
history_label.pack()

reveal_label = tk.Label(quiz_tab, text="", font=(FONT, 13, "bold"), bg=PAGE_BG, height=2)
reveal_label.pack(fill="x", padx=10, pady=6)


def points_text(points):
    return "1 point" if points == 1 else f"{points} points"


def current_question():
    return quiz_state["questions"][quiz_state["number"]]


def update_status():
    tries_left = TRIES_PER_QUESTION - quiz_state["tries_used"]
    dots = "●" * tries_left + "○" * quiz_state["tries_used"]
    score = total_score(quiz_state["scores"])

    quiz_status.config(
        text=f"Question {quiz_state['number'] + 1} of {len(quiz_state['questions'])}     Score {score}     Tries  {dots}"
    )


def show_question():
    question = current_question()

    quiz_state["tries_used"] = 0
    quiz_state["low"] = 0
    quiz_state["high"] = MAX_AQI
    quiz_state["guesses"] = []
    quiz_state["active"] = True

    clue_panel.config(text=describe_clues(question["reading"]))
    range_label.config(text=f"The answer is between 0 and {MAX_AQI}")
    feedback_label.config(text="Make your first guess", fg=MUTED)
    history_label.config(text="")
    reveal_label.config(text="", bg=PAGE_BG)

    guess_text.set("")
    guess_box.config(state="normal")
    guess_button.config(state="normal")
    guess_box.focus_set()

    action_button.config(text="Next question", state="disabled")
    update_status()


def end_question(points, headline, color):
    question = current_question()
    answer = question["answer"]
    category = get_aqi_category(answer)
    background, text_color = CATEGORY_COLORS[category]

    quiz_state["scores"].append(points)
    quiz_state["active"] = False
    quiz_state["summary"].append(f"{question['reading']['city']}: AQI {answer} ({category}) → {points_text(points)}")

    feedback_label.config(text=headline, fg=color)
    reveal_label.config(text=f"Actual AQI: {answer}   ·   {category}", bg=background, fg=text_color)

    guess_box.config(state="disabled")
    guess_button.config(state="disabled")

    if quiz_state["number"] == len(quiz_state["questions"]) - 1:
        action_button.config(text="See results", command=finish_quiz, state="normal")
    else:
        action_button.config(text="Next question", command=next_question, state="normal")

    update_status()


def submit_guess(event=None):
    if not quiz_state["active"]:
        return

    try:
        guess = validate_guess(guess_text.get())
    except ValueError as problem:
        feedback_label.config(text="⚠  " + str(problem), fg=ERROR_RED)
        return

    answer = current_question()["answer"]
    quiz_state["tries_used"] += 1
    result = check_guess(guess, answer)

    if result == "correct":
        quiz_state["guesses"].append(f"{guess} ✓")
        history_label.config(text="Guesses:  " + "   →   ".join(quiz_state["guesses"]))
        points = points_for_try(quiz_state["tries_used"])
        end_question(points, f"✓  Correct!  +{points_text(points)}", CORRECT_GREEN)
        return

    low, high = narrow_range(quiz_state["low"], quiz_state["high"], guess, result)
    quiz_state["low"] = low
    quiz_state["high"] = high

    if result == "higher":
        headline, color = f"▲  HIGHER  than {guess}", HIGHER_BLUE
        arrow = "▲"
    else:
        headline, color = f"▼  LOWER  than {guess}", LOWER_ORANGE
        arrow = "▼"

    quiz_state["guesses"].append(f"{guess} {arrow}")
    history_label.config(text="Guesses:  " + "   →   ".join(quiz_state["guesses"]))
    range_label.config(text=f"The answer is between {low} and {high}")
    feedback_label.config(text=headline, fg=color)
    guess_text.set("")

    if quiz_state["tries_used"] >= TRIES_PER_QUESTION:
        end_question(0, "Out of tries!  +0 points", ERROR_RED)
    else:
        update_status()


def next_question():
    quiz_state["number"] += 1
    show_question()


def finish_quiz():
    total = total_score(quiz_state["scores"])
    maximum = len(quiz_state["questions"]) * TRIES_PER_QUESTION

    lines = ["Quiz complete!", ""] + quiz_state["summary"]
    lines.append("")
    lines.append(f"Total:  {total} / {maximum}")

    quiz_status.config(text=f"Quiz complete     Score {total} / {maximum}")

    clue_panel.config(text="\n".join(lines))
    range_label.config(text="")
    history_label.config(text="")
    guess_text.set("")
    feedback_label.config(text="Rank:  " + get_rank(total, maximum), fg=DARK)
    reveal_label.config(text="", bg=PAGE_BG)

    action_button.config(text="Play again", command=start_quiz, state="normal")


def start_quiz():
    quiz_state["questions"] = build_questions(records)
    quiz_state["number"] = 0
    quiz_state["scores"] = []
    quiz_state["summary"] = []

    show_question()


guess_button = make_button(guess_row, "Guess", submit_guess)
guess_button.grid(row=1, column=1, padx=(0, 14), pady=(0, 12))

action_button = make_button(quiz_tab, "Start quiz", start_quiz)
action_button.pack(pady=4)

guess_box.bind("<Return>", submit_guess)

# Explanation panel when starting
clue_panel.config(
    text="Guess the AQI!\n\n"
         f"•  {QUESTION_COUNT} random questions, each from a different city\n"
         f"•  {TRIES_PER_QUESTION} tries per question\n"
         "•  After each wrong guess you are told: HIGHER or LOWER\n"
         f"•  A guess within ±{TOLERANCE} counts as correct\n"
         f"•  Points: {TRIES_PER_QUESTION} for a first-try win, down to 1 for the last try"
)
quiz_status.config(text="AQI Quiz")
guess_box.config(state="disabled")
guess_button.config(state="disabled")


# -----------------------------------------
# START THE PROGRAM
# -----------------------------------------

show_latest()

if __name__ == "__main__":
    window.mainloop()