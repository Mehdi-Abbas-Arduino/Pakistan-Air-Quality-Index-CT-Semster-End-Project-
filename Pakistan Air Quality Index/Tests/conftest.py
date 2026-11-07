
import os
import sys

# Add the Scripts folder to Python's search path,
# so the tests can import data_loader, aqi_calculator, etc.
SCRIPTS_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Scripts"
)

sys.path.insert(0, SCRIPTS_FOLDER)
