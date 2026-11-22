# ============================================================
# RECURSION TOOLS MODULE
# ============================================================
# Contains two recursive functions used in the project:
#   1. total_score   → simple recursion (used for quiz score)
#   2. recursive_sum → divide-and-conquer recursion (used for average AQI)
# ============================================================


# ----------------------------------------------------------
# SIMPLE RECURSION: SUM OF A SMALL LIST
# ----------------------------------------------------------
# Idea: total of a list = first item + total of the rest
# Base case: empty list returns 0
#
# Used in the quiz to calculate the player's current score.
# The list is always very small (max 5 items), so recursion depth is safe.

def total_score(scores):
    """
    Recursively calculate the sum of a list of numbers.
    """
    # Base case: nothing left to add
    if len(scores) == 0:
        return 0

    # Recursive case: first item + sum of the remaining items
    return scores[0] + total_score(scores[1:])


# ----------------------------------------------------------
# DIVIDE-AND-CONQUER RECURSION: SUM OF A LARGE LIST
# ----------------------------------------------------------
# total_score() would crash on a long list because Python has a
# recursion depth limit (~1000).
#
# This version splits the list in half every time, so the depth
# is only about log₂(n). Safe even for thousands of readings.
#
# Used inside get_average_aqi() in aqi_calculator.py.

def recursive_sum(numbers, start=0, end=None):
    """
    Efficiently calculate the sum of a list using divide-and-conquer recursion.
    """
    # By default work on the whole list
    if end is None:
        end = len(numbers)

    # Base case 1: empty range
    if end - start <= 0:
        return 0

    # Base case 2: only one element left
    if end - start == 1:
        return numbers[start]

    # Recursive case: split into two halves and add the results
    middle = (start + end) // 2
    return recursive_sum(numbers, start, middle) + recursive_sum(numbers, middle, end)
