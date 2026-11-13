# -----------------------------------------
# PROGRAM ENTRY POINT
# -----------------------------------------
'''
It has no functions. It imports gui and calls mainloop() on the window to start the program. It looks for app or window in gui.py so it works with either Tkinter or CustomTkinter.
'''
import gui

if __name__ == "__main__":
    # Checks whether CustomTkinter (app) or Tkinter (window) is defined
    main_window = getattr(gui, "app", getattr(gui, "window", None))

    if main_window is not None:
        main_window.mainloop()
    else:
        raise AttributeError("Could not find 'app' or 'window' in gui.py")