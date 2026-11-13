'''total_score(scores)
Simple recursion: the total is the first item plus the total of the rest, and an empty list returns 0 (the base case). It is a good teaching example, but it only works on small lists. Python's recursion limit is about 1000, and the function goes one level deeper per item.
Where it is used (gui.py): imported on line 33 and called in two places.
• Line 337, in update_status(), to show the live quiz score.
• Line 414, in next_question(), to get the final total for the rank.
The list has at most 5 scores, so the depth limit is never a problem.
recursive_sum(numbers, start, end)
Divide-and-conquer recursion. It splits the list in half, sums each half and adds the results. There are two base cases (empty range returns 0, one item returns that item). The depth is about log₂(n), roughly 12 calls for 2,184 readings, instead of 2,184. Using indexes instead of slices also avoids copying the list at each step.
Where it is used (aqi_calculator.py): imported on line 1 and called on line 99 inside get_average_aqi().
The problem: gui.py imports get_average_aqi but never calls it, as does get_worst_reading. So during a normal run recursive_sum never executes. If the professor asks to see it run, there is no button for it.
The fix: call get_average_aqi(get_city_readings(records, c)) in check_time and add it to the card's details text, for example "Dataset average: 142". That way the large-list recursion is used on real data.'''

# -----------------------------------------
# RECURSION 1: SUM OF A SMALL LIST
# -----------------------------------------

# Idea: the total of a list = first item + total of the rest of the list.
# Every recursive function needs a base case, where it stops calling itself.

def total_score(scores):

    # Base case: an empty list adds up to 0.
    if len(scores) == 0:
        return 0

    # Recursive case: first item + total of everything after it.
    return scores[0] + total_score(scores[1:])


# -----------------------------------------
# RECURSION 2: SUM OF A LARGE LIST
# -----------------------------------------

# total_score() calls itself once per item. Python stops any function that
# calls itself about 1000 times deep, so a city's 2,184 readings would crash it.
#
# The fix: split the list in half each time, and add the two halves.
# Now the depth is only about 12 calls, even for 2,184 items.

def recursive_sum(numbers, start=0, end=None):

    # By default, work on the whole list.
    if end is None:
        end = len(numbers)

    # Base case 1: nothing left in this part of the list.
    if end - start <= 0:
        return 0

    # Base case 2: exactly one item left, so it is the answer.
    if end - start == 1:
        return numbers[start]

    # Recursive case: split the part in half and add the two halves.
    middle = (start + end) // 2

    return recursive_sum(numbers, start, middle) + recursive_sum(numbers, middle, end)
