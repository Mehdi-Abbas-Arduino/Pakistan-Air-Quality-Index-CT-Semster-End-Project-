# -----------------------------------------
# PROGRAM ENTRY POINT
# -----------------------------------------

# Run this file to start the Pakistan Air Quality Index app.
#
# Importing gui.py loads the dataset and builds the whole window
# (City Check, AQI Calculator, Compare Cities and AQI Quiz tabs).
# mainloop() then keeps the window open and listens for clicks.

import gui

if __name__ == "__main__":
    gui.window.mainloop()