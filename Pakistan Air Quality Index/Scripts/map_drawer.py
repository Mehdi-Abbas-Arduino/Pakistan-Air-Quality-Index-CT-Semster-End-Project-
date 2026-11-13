import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import LinearSegmentedColormap, Normalize
import matplotlib.cm as cm

'''

• embed_pakistan_aqi_map: Draws the dark-themed AQI map with colored dots, labels and a color bar. It is never imported anywhere. gui.py has its own draw_map with its own copy of the coordinates. Either delete this file or be ready to say it was the earlier version.
'''
# Latitude & Longitude coordinates for major Pakistani cities
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

# Standard EPA AQI Color Palette
AQI_COLORS = ["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97", "#7E0023"]
AQI_BOUNDS = [0, 50, 100, 150, 200, 300, 500]

def embed_pakistan_aqi_map(parent_frame, city_aqi_dict):
    """
    Renders a glossy dark-mode map of Pakistan displaying AQI values across cities,
    with custom color variations, a color key, and highlighting the maximum AQI location.
    """
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#1a1c23")
    ax.set_facecolor("#111318")

    lats, lons, aqis, names = [], [], [], []

    for city, aqi in city_aqi_dict.items():
        if city in PAK_CITIES_COORDS and aqi is not None:
            lat, lon = PAK_CITIES_COORDS[city]
            lats.append(lat)
            lons.append(lon)
            aqis.append(aqi)
            names.append(city)

    if not aqis:
        ax.text(0.5, 0.5, "No Map Data Available", color="white", ha="center", va="center")
        return None

    # Custom continuous colormap matching EPA categories
    cmap = LinearSegmentedColormap.from_list("aqi_cmap", AQI_COLORS, N=256)
    norm = Normalize(vmin=0, vmax=500)

    # Plot glowing scatter dots for city locations
    sc = ax.scatter(lons, lats, c=aqis, cmap=cmap, norm=norm, s=[min(a * 2.5 + 150, 900) for a in aqis],
                    alpha=0.85, edgecolors="#ffffff", linewidths=1.5, zorder=3)

    # Find location with the worst (highest) AQI
    max_idx = aqis.index(max(aqis))
    max_city, max_aqi = names[max_idx], aqis[max_idx]

    # Highlight highest AQI with glowing pulsating marker
    ax.scatter([lons[max_idx]], [lats[max_idx]], s=1400, facecolors="none",
               edgecolors="#ff0055", linewidths=3, linestyle="--", label="Highest AQI Hotspot", zorder=4)

    # Add labels with glowing black outline
    for lat, lon, name, aqi in zip(lats, lons, names, aqis):
        is_max = (name == max_city)
        text_color = "#ff3366" if is_max else "white"
        weight = "bold" if is_max else "normal"
        ax.annotate(f"{name}\nAQI {aqi}", (lon + 0.15, lat + 0.1), color=text_color,
                    fontsize=9 if not is_max else 11, fontweight=weight,
                    bbox=dict(boxstyle="round,pad=0.3", fc="#1f2430", ec="#3b4252", alpha=0.9))

    # Grid and Bounds Setup
    ax.set_xlim(65.0, 76.5)
    ax.set_ylim(23.5, 37.0)
    ax.grid(True, color="#2e3440", linestyle=":", alpha=0.6)
    ax.set_title(f"🔥 Pakistan Realtime AQI Heatmap (Peak: {max_city} - AQI {max_aqi})",
                 color="#e5e9f0", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Longitude (°E)", color="#88c0d0", fontsize=9)
    ax.set_ylabel("Latitude (°N)", color="#88c0d0", fontsize=9)
    ax.tick_params(colors="#d8dee9", labelsize=8)

    # Colorbar Key Setup
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, orientation="vertical", pad=0.03, shrink=0.85)
    cbar.set_label("Air Quality Index (AQI Scale)", color="#e5e9f0", fontsize=9, fontweight="bold")
    cbar.ax.tick_params(labelsize=8, colors="#d8dee9")
    cbar.set_ticks([0, 50, 100, 150, 200, 300, 500])
    cbar.set_ticklabels(["0 Good", "50", "100 Mod", "150 Sens", "200 Unh", "300 V.Unh", "500 Haz"])

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    return canvas.get_tk_widget()