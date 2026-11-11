# -----------------------------------------
# PROGRAM ENTRY POINT
# -----------------------------------------

import gui

if __name__ == "__main__":
    # Checks whether CustomTkinter (app) or Tkinter (window) is defined
    main_window = getattr(gui, "app", getattr(gui, "window", None))

    if main_window is not None:
        main_window.mainloop()
    else:
        raise AttributeError("Could not find 'app' or 'window' in gui.py")