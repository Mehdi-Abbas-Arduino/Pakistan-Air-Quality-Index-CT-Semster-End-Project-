
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
