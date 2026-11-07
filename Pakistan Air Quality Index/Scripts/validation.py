from data_loader import load_dataset
from aqi_calculator import calculate_pm25_aqi, get_aqi_category


# -----------------------------------------
# CHECK 1: MISSING PM2.5 VALUES
# -----------------------------------------

def find_missing_pm25(records):

    missing = []

    for row in records:
        if row["pm2_5"] is None:
            missing.append(row)

    return missing


# -----------------------------------------
# CHECK 2: PM2.5 VALUES OUTSIDE THE AQI TABLE
# -----------------------------------------

def find_out_of_range_pm25(records):

    out_of_range = []

    for row in records:
        value = row["pm2_5"]

        # The EPA table only covers 0 to 500.4.
        if value is not None and (value < 0 or value > 500.4):
            out_of_range.append(row)

    return out_of_range


# -----------------------------------------
# CHECK 3: OUR CATEGORY vs THE DATASET'S CATEGORY
# -----------------------------------------

def find_category_mismatches(records):

    mismatches = []

    for row in records:
        aqi = calculate_pm25_aqi(row["pm2_5"])
        our_category = get_aqi_category(aqi)

        # Compare our result with the dataset's own aqi_category column.
        if our_category != row["aqi_category"]:
            mismatches.append(row)

    return mismatches


# -----------------------------------------
# RUN ALL CHECKS
# -----------------------------------------

def run_validation():

    records = load_dataset()

    print("Validating", len(records), "records...\n")

    missing = find_missing_pm25(records)
    out_of_range = find_out_of_range_pm25(records)
    mismatches = find_category_mismatches(records)

    print("Missing PM2.5 values:        ", len(missing))
    print("PM2.5 outside AQI table:     ", len(out_of_range))
    print("Category mismatches:         ", len(mismatches))

    # Show a few examples if anything went wrong.
    for row in mismatches[:5]:
        print("  Mismatch:", row["city"], row["timestamp"],
              "PM2.5 =", row["pm2_5"],
              "dataset says", row["aqi_category"])

    # Validation passes only if every check found zero problems.
    passed = len(missing) == 0 and len(out_of_range) == 0 and len(mismatches) == 0

    if passed:
        print("\nAll checks passed.")
    else:
        print("\nSome checks failed.")

    return passed


# Run the checks when this file is executed directly.
if __name__ == "__main__":
    run_validation()