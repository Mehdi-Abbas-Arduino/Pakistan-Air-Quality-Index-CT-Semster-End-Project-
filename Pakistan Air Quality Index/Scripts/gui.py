import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import LinearSegmentedColormap, Normalize
import matplotlib.cm as cm

'''
• make_card: Builds the result card (big AQI number, category, advice, details).
• update_card: Fills the card and colors it by category.
• check_time: The "Check Dataset" button. It validates the inputs, looks up the record, calculates the AQI and shows it.
• check_live: The "Realtime API" button, which does the same using live data.
• draw_map: Gets each city's AQI (live first, dataset as fallback) and draws the heatmap, circling the worst city.
• do_calc: The manual PM2.5 calculator button.
• update_status: Refreshes the quiz header (question number, score, tries left).
• start_quiz: Resets the state and builds new questions.
• show_question: Resets the per-question state and shows the new clues.
• submit_guess: Validates the guess, checks it, awards points or narrows the range, and ends the question after 5 tries.
• next_question: Moves on, or at the end shows the final rank and a "Play Again" button.'''

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
# DARK THEME COLOR PALETTE
# -----------------------------------------
FONT = "Segoe UI"
DARK_BG = "#0f172a"
CARD_BG = "#1e293b"
INPUT_BG = "#334155"
TEXT_COLOR = "#f8fafc"
MUTED_TEXT = "#94a3b8"
ACCENT_BLUE = "#0284c7"
LIVE_GREEN = "#16a34a"
ERROR_RED = "#ef4444"

PAK_CITIES_COORDS = {
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

CATEGORY_COLORS = {
    "Good":                           ("#00E400", "black"),
    "Moderate":                       ("#FFFF00", "black"),
    "Unhealthy for Sensitive Groups": ("#FF7E00", "black"),
    "Unhealthy":                      ("#FF0000", "white"),
    "Very Unhealthy":                 ("#8F3F97", "white"),
    "Hazardous":                      ("#7E0023", "white"),
}

records = load_dataset()
cities = get_available_cities(records)
first_date, last_date = get_date_range(records)

# -----------------------------------------
# WINDOW SETUP
# -----------------------------------------
window = tk.Tk()
window.title("Pakistan Air Quality Index - Dark Cyber Hub")
window.geometry("900x850")
window.configure(bg=DARK_BG)

# Expose 'app' alias so main.py never crashes
app = window

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=DARK_BG, borderwidth=0)
style.configure("TNotebook.Tab", font=(FONT, 11, "bold"), background=CARD_BG, foreground=TEXT_COLOR, padding=(16, 8))
style.map("TNotebook.Tab", background=[("selected", ACCENT_BLUE)], foreground=[("selected", "white")])

# Header
header = tk.Frame(window, bg="#0284c7")
header.pack(fill="x")
tk.Label(header, text="⚡ PAKISTAN AIR QUALITY DASHBOARD", font=(FONT, 18, "bold"), bg="#0284c7", fg="white").pack(anchor="w", padx=20, pady=(10, 2))
tk.Label(header, text=f"{len(cities)} Cities Tracked · Historical Dataset + Realtime Open-Meteo API", font=(FONT, 10), bg="#0284c7", fg="#e0f2fe").pack(anchor="w", padx=20, pady=(0, 10))

tabs = ttk.Notebook(window)
tabs.pack(fill="both", expand=True, padx=10, pady=10)

city_tab = tk.Frame(tabs, bg=DARK_BG)
map_tab = tk.Frame(tabs, bg=DARK_BG)
calc_tab = tk.Frame(tabs, bg=DARK_BG)
quiz_tab = tk.Frame(tabs, bg=DARK_BG)

tabs.add(city_tab, text=" 🔍 City Check ")
tabs.add(map_tab, text=" 🗺️ Heatmap & Key ")
tabs.add(calc_tab, text=" 🧮 AQI Calculator ")
tabs.add(quiz_tab, text=" 🎮 Arcade Quiz Game ")

# Helper Result Card
def make_card(parent):
    frame = tk.Frame(parent, bg=CARD_BG, highlightbackground="#334155", highlightthickness=1)
    banner = tk.Frame(frame, bg="#334155")
    banner.pack(fill="x", padx=10, pady=10)

    aqi_lbl = tk.Label(banner, text="--", font=(FONT, 48, "bold"), bg="#334155", fg="white")
    aqi_lbl.pack(pady=(10, 0))

    cat_lbl = tk.Label(banner, text="Select City / Input PM2.5", font=(FONT, 14, "bold"), bg="#334155", fg=MUTED_TEXT)
    cat_lbl.pack(pady=(0, 10))

    advice_lbl = tk.Label(frame, text="", font=(FONT, 11, "italic"), bg=CARD_BG, fg=TEXT_COLOR, wraplength=650)
    advice_lbl.pack(pady=8, padx=14)

    details_lbl = tk.Label(frame, text="", font=(FONT, 10), bg=CARD_BG, fg=MUTED_TEXT)
    details_lbl.pack(pady=(0, 10))

    return {"frame": frame, "banner": banner, "aqi": aqi_lbl, "category": cat_lbl, "advice": advice_lbl, "details": details_lbl}

def update_card(card, aqi, details):
    cat = get_aqi_category(aqi)
    bg, fg = CATEGORY_COLORS[cat]
    card["banner"].config(bg=bg)
    card["aqi"].config(text=str(aqi), bg=bg, fg=fg)
    card["category"].config(text=cat, bg=bg, fg=fg)
    card["advice"].config(text=get_health_advice(cat))
    card["details"].config(text=details)

# -----------------------------------------
# TAB 1: CITY CHECK
# -----------------------------------------
city_text = tk.StringVar(value="Lahore")
date_text = tk.StringVar(value=last_date)
hour_text = tk.StringVar(value="12")

inputs = tk.Frame(city_tab, bg=CARD_BG, padx=14, pady=14)
inputs.pack(fill="x", padx=10, pady=10)

tk.Label(inputs, text="City", font=(FONT, 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w")
tk.Label(inputs, text="Date (YYYY-MM-DD)", font=(FONT, 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=1, sticky="w", padx=10)
tk.Label(inputs, text="Hour (0-23)", font=(FONT, 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=2, sticky="w")

city_box = ttk.Combobox(inputs, textvariable=city_text, values=cities, width=16, font=(FONT, 11))
city_box.grid(row=1, column=0, pady=(4, 10), sticky="w")

date_box = tk.Entry(inputs, textvariable=date_text, width=14, font=(FONT, 11), bg=INPUT_BG, fg=TEXT_COLOR, insertbackground="white")
date_box.grid(row=1, column=1, padx=10, pady=(4, 10), sticky="w")

hour_box = tk.Spinbox(inputs, from_=0, to=23, textvariable=hour_text, width=6, font=(FONT, 11), bg=INPUT_BG, fg=TEXT_COLOR, insertbackground="white")
hour_box.grid(row=1, column=2, pady=(4, 10), sticky="w")

city_err = tk.Label(city_tab, text="", font=(FONT, 10, "bold"), bg=DARK_BG, fg=ERROR_RED)
city_err.pack(anchor="w", padx=14)

city_card = make_card(city_tab)

def check_time():
    city_err.config(text="")
    try:
        c = validate_city(city_text.get(), cities)
        d = validate_date(date_text.get(), first_date, last_date)
        h = validate_hour(hour_text.get())
        r = get_city_reading_at(records, c, d, h)
        if not r:
            city_err.config(text=f"No dataset record for {c} on {d} at hour {h}.")
            return
        aqi = calculate_pm25_aqi(r["pm2_5"])
        update_card(city_card, aqi, f"{c} · {r['timestamp']} | PM2.5: {r['pm2_5']} µg/m³")
    except ValueError as e:
        city_err.config(text=f"⚠ {str(e)}")

def check_live():
    city_err.config(text="")
    try:
        live = fetch_live_city_reading(city_text.get())
        aqi = calculate_pm25_aqi(live["pm2_5"])
        city_text.set(live["city"])
        update_card(city_card, aqi, f"⚡ REALTIME LIVE API · {live['city']} · PM2.5: {live['pm2_5']} µg/m³")
    except ValueError as e:
        city_err.config(text=f"⚠ {str(e)}")

btn_row = tk.Frame(inputs, bg=CARD_BG)
btn_row.grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 0))

tk.Button(btn_row, text="Check Dataset", command=check_time, font=(FONT, 10, "bold"), bg=ACCENT_BLUE, fg="white", relief="flat", padx=10, pady=4).pack(side="left", padx=(0, 8))
tk.Button(btn_row, text="⚡ Realtime API Data", command=check_live, font=(FONT, 10, "bold"), bg=LIVE_GREEN, fg="white", relief="flat", padx=10, pady=4).pack(side="left")

city_card["frame"].pack(fill="x", padx=10, pady=10)

# -----------------------------------------
# TAB 2: PAKISTAN HEATMAP & KEY
# -----------------------------------------
map_frame = tk.Frame(map_tab, bg=CARD_BG)
map_frame.pack(fill="both", expand=True, padx=10, pady=10)

def draw_map():
    for w in map_frame.winfo_children():
        w.destroy()

    city_aqis = {}
    for c in cities:
        try:
            live = fetch_live_city_reading(c)
            city_aqis[c] = calculate_pm25_aqi(live["pm2_5"])
        except Exception:
            r = get_latest_city_reading(records, c)
            if r:
                city_aqis[c] = calculate_pm25_aqi(r["pm2_5"])

    fig, ax = plt.subplots(figsize=(6.5, 4.5), facecolor=DARK_BG)
    ax.set_facecolor("#1e293b")

    lats, lons, aqis, names = [], [], [], []
    for city, aqi in city_aqis.items():
        if city in PAK_CITIES_COORDS and aqi is not None:
            lat, lon = PAK_CITIES_COORDS[city]
            lats.append(lat)
            lons.append(lon)
            aqis.append(aqi)
            names.append(city)

    cmap = LinearSegmentedColormap.from_list("aqi_cmap", ["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97", "#7E0023"], N=256)
    norm = Normalize(vmin=0, vmax=500)

    ax.scatter(lons, lats, c=aqis, cmap=cmap, norm=norm, s=[min(a * 2 + 120, 700) for a in aqis], alpha=0.9, edgecolors="white", zorder=3)

    max_idx = aqis.index(max(aqis))
    ax.scatter([lons[max_idx]], [lats[max_idx]], s=1100, facecolors="none", edgecolors="#ef4444", linewidths=3, linestyle="--", zorder=4)

    for lat, lon, name, aqi in zip(lats, lons, names, aqis):
        is_max = (aqi == max(aqis))
        ax.annotate(f"{name}\n{aqi}", (lon + 0.1, lat + 0.1), color="#ef4444" if is_max else "white", fontsize=8 if not is_max else 10, fontweight="bold")

    ax.set_xlim(65.0, 76.5)
    ax.set_ylim(23.5, 37.0)
    ax.grid(True, color="#334155", linestyle=":", alpha=0.6)
    ax.set_title(f"🔥 Pakistan Realtime AQI Heatmap (Peak: {names[max_idx]} - AQI {max(aqis)})", color="white", fontsize=11, fontweight="bold")
    ax.tick_params(colors=MUTED_TEXT, labelsize=8)

    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, orientation="vertical", pad=0.02, shrink=0.8)
    cbar.ax.tick_params(labelsize=8, colors="white")

    canvas = FigureCanvasTkAgg(fig, master=map_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

tk.Button(map_tab, text="🔄 Refresh Realtime Map", command=draw_map, font=(FONT, 10, "bold"), bg=ACCENT_BLUE, fg="white", relief="flat", pady=4).pack(pady=4)
window.after(300, draw_map)

# -----------------------------------------
# TAB 3: AQI CALCULATOR
# -----------------------------------------
calc_frame = tk.Frame(calc_tab, bg=CARD_BG, padx=14, pady=14)
calc_frame.pack(fill="x", padx=10, pady=10)

tk.Label(calc_frame, text="PM2.5 value (µg/m³)", font=(FONT, 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w")
pm25_text = tk.StringVar()
pm25_entry = tk.Entry(calc_frame, textvariable=pm25_text, width=18, font=(FONT, 11), bg=INPUT_BG, fg=TEXT_COLOR, insertbackground="white")
pm25_entry.pack(anchor="w", pady=(4, 10))

calc_err = tk.Label(calc_tab, text="", font=(FONT, 10, "bold"), bg=DARK_BG, fg=ERROR_RED)
calc_err.pack(anchor="w", padx=14)

calc_card = make_card(calc_tab)

def do_calc():
    calc_err.config(text="")
    try:
        val = validate_pm25(pm25_text.get())
        aqi = calculate_pm25_aqi(val)
        update_card(calc_card, aqi, f"PM2.5 = {val} µg/m³")
    except ValueError as e:
        calc_err.config(text=f"⚠ {str(e)}")

tk.Button(calc_frame, text="Calculate AQI", command=do_calc, font=(FONT, 10, "bold"), bg=ACCENT_BLUE, fg="white", relief="flat", padx=10, pady=4).pack(anchor="w")
calc_card["frame"].pack(fill="x", padx=10, pady=10)

# -----------------------------------------
# TAB 4: AQI QUIZ GAME
# -----------------------------------------
quiz_state = {"questions": [], "number": 0, "tries_used": 0, "low": 0, "high": MAX_AQI, "scores": [], "guesses": [], "active": False}

quiz_status = tk.Label(quiz_tab, text="🎮 AQI Quiz Game", font=(FONT, 12, "bold"), bg=DARK_BG, fg=TEXT_COLOR)
quiz_status.pack(anchor="w", padx=14, pady=(10, 2))

clue_panel = tk.Text(quiz_tab, height=8, font=("Consolas", 11), bg=CARD_BG, fg=TEXT_COLOR, relief="flat", padx=10, pady=10)
clue_panel.pack(fill="x", padx=10, pady=6)

range_label = tk.Label(quiz_tab, text="", font=(FONT, 11), bg=DARK_BG, fg=MUTED_TEXT)
range_label.pack(anchor="w", padx=14)

guess_row = tk.Frame(quiz_tab, bg=CARD_BG, padx=14, pady=10)
guess_row.pack(fill="x", padx=10, pady=6)

tk.Label(guess_row, text="Your guess (AQI 0-500)", font=(FONT, 10, "bold"), bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w")

guess_text = tk.StringVar()
guess_box = tk.Entry(guess_row, textvariable=guess_text, width=12, font=(FONT, 11), bg=INPUT_BG, fg=TEXT_COLOR, insertbackground="white")
guess_box.grid(row=1, column=0, pady=4, sticky="w")

feedback_label = tk.Label(quiz_tab, text="", font=(FONT, 14, "bold"), bg=DARK_BG, fg=TEXT_COLOR)
feedback_label.pack(pady=4)

history_label = tk.Label(quiz_tab, text="", font=(FONT, 10), bg=DARK_BG, fg=MUTED_TEXT)
history_label.pack()

def update_status():
    left = TRIES_PER_QUESTION - quiz_state["tries_used"]
    dots = "●" * left + "○" * quiz_state["tries_used"]
    score = total_score(quiz_state["scores"])
    quiz_status.config(text=f"Question {quiz_state['number'] + 1} of {len(quiz_state['questions'])}   |   Score: {score}   |   Tries: {dots}")

def start_quiz():
    quiz_state["questions"] = build_questions(records)
    quiz_state["number"] = 0
    quiz_state["scores"] = []
    show_question()

def show_question():
    q = quiz_state["questions"][quiz_state["number"]]
    quiz_state["tries_used"] = 0
    quiz_state["low"] = 0
    quiz_state["high"] = MAX_AQI
    quiz_state["guesses"] = []
    quiz_state["active"] = True

    clue_panel.delete("1.0", "end")
    clue_panel.insert("1.0", describe_clues(q["reading"]))
    range_label.config(text=f"Answer is between 0 and {MAX_AQI}")
    feedback_label.config(text="Make your guess!", fg=MUTED_TEXT)
    history_label.config(text="")
    guess_text.set("")
    guess_box.config(state="normal")
    guess_button.config(state="normal")
    guess_box.focus_set()
    action_button.config(text="Next Question", state="disabled")
    update_status()

def submit_guess(event=None):
    if not quiz_state["active"]:
        return
    try:
        g = validate_guess(guess_text.get())
    except ValueError as p:
        feedback_label.config(text=f"⚠ {str(p)}", fg=ERROR_RED)
        return

    ans = quiz_state["questions"][quiz_state["number"]]["answer"]
    quiz_state["tries_used"] += 1
    res = check_guess(g, ans)

    if res == "correct":
        pts = points_for_try(quiz_state["tries_used"])
        quiz_state["scores"].append(pts)
        quiz_state["active"] = False
        feedback_label.config(text=f"✓ Correct! +{pts} pts (AQI was {ans})", fg=LIVE_GREEN)
        guess_box.config(state="disabled")
        guess_button.config(state="disabled")
        action_button.config(text="Next Question", command=next_question, state="normal")
        return

    low, high = narrow_range(quiz_state["low"], quiz_state["high"], g, res)
    quiz_state["low"], quiz_state["high"] = low, high

    arrow = "▲ HIGHER" if res == "higher" else "▼ LOWER"
    quiz_state["guesses"].append(f"{g} {arrow}")
    history_label.config(text="Guesses: " + " → ".join(quiz_state["guesses"]))
    range_label.config(text=f"Answer is between {low} and {high}")
    feedback_label.config(text=f"{arrow} than {g}", fg="#38bdf8" if res == "higher" else "#f97316")
    guess_text.set("")

    if quiz_state["tries_used"] >= TRIES_PER_QUESTION:
        quiz_state["scores"].append(0)
        quiz_state["active"] = False
        feedback_label.config(text=f"Out of tries! Answer was {ans}", fg=ERROR_RED)
        guess_box.config(state="disabled")
        guess_button.config(state="disabled")
        action_button.config(text="Next Question", command=next_question, state="normal")
    
    update_status()

def next_question():
    if quiz_state["number"] + 1 < len(quiz_state["questions"]):
        quiz_state["number"] += 1
        show_question()
    else:
        tot = total_score(quiz_state["scores"])
        rank = get_rank(tot, len(quiz_state["questions"]) * TRIES_PER_QUESTION)
        feedback_label.config(text=f"Quiz Complete! Rank: {rank}", fg="white")
        action_button.config(text="Play Again", command=start_quiz, state="normal")

guess_button = tk.Button(guess_row, text="Submit Guess", command=submit_guess, font=(FONT, 10, "bold"), bg=ACCENT_BLUE, fg="white", relief="flat", padx=10, pady=2)
guess_button.grid(row=1, column=1, padx=10)

action_button = tk.Button(quiz_tab, text="Start Quiz Game", command=start_quiz, font=(FONT, 11, "bold"), bg=LIVE_GREEN, fg="white", relief="flat", padx=14, pady=4)
action_button.pack(pady=6)

guess_box.bind("<Return>", submit_guess)

if __name__ == "__main__":
    window.mainloop()