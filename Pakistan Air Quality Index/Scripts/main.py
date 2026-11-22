# ============================================================
# MAIN ENTRY POINT
# Pakistan Air Quality Index (AQI) Dashboard
# ============================================================
# This is the starting point of the entire application.
# It imports the GUI module and launches the main window.
# ============================================================

import gui

if __name__ == "__main__":
    # Support both naming styles:
    # - 'app'   → common when using CustomTkinter
    # - 'window' → common when using standard Tkinter
    main_window = getattr(gui, "app", getattr(gui, "window", None))

    if main_window is not None:
        # Start the Tkinter event loop.
        # This keeps the window open and handles all user interactions.
        main_window.mainloop()
    else:
        raise AttributeError(
            "Could not find 'app' or 'window' in gui.py. "
            "Make sure the main window is properly defined."
        )
