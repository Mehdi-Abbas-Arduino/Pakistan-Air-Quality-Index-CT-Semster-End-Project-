import random

import pytest

from recursion_tools import total_score, recursive_sum
from quiz import (
    QUESTION_COUNT,
    TRIES_PER_QUESTION,
    TOLERANCE,
    build_questions,
    describe_clues,
    check_guess,
    points_for_try,
    narrow_range,
    get_rank
)
from validation import validate_guess
from data_loader import load_dataset
from aqi_calculator import get_average_aqi


# -----------------------------------------
# recursion: total_score
# -----------------------------------------

def test_total_score_of_empty_list_is_zero():
    assert total_score([]) == 0


def test_total_score_single_item():
    assert total_score([7]) == 7


def test_total_score_matches_sum():
    scores = [5, 0, 3, 1, 4]
    assert total_score(scores) == sum(scores) == 13


def test_total_score_does_not_change_the_list():
    scores = [1, 2, 3]
    total_score(scores)
    assert scores == [1, 2, 3]


# -----------------------------------------
# recursion: recursive_sum (works on big lists)
# -----------------------------------------

def test_recursive_sum_empty_and_single():
    assert recursive_sum([]) == 0
    assert recursive_sum([42]) == 42


def test_recursive_sum_matches_sum_on_small_lists():
    for size in range(0, 40):
        numbers = list(range(size))
        assert recursive_sum(numbers) == sum(numbers)


def test_recursive_sum_handles_a_whole_citys_readings():
    # 2,184 items: the simple one-item-at-a-time recursion would crash here.
    numbers = list(range(2184))
    assert recursive_sum(numbers) == sum(numbers)


def test_total_score_crashes_on_huge_lists_but_recursive_sum_does_not():
    numbers = list(range(5000))

    with pytest.raises(RecursionError):
        total_score(numbers)

    assert recursive_sum(numbers) == sum(numbers)


def test_average_aqi_uses_recursion_and_matches_real_data():
    records = load_dataset()
    multan = [row for row in records if row["city"] == "Multan"]

    assert get_average_aqi(multan) == 201


# -----------------------------------------
# quiz: build_questions
# -----------------------------------------

def test_real_dataset_gives_five_questions_from_different_cities():
    questions = build_questions(load_dataset(), generator=random.Random(1))

    assert len(questions) == QUESTION_COUNT

    cities = [q["reading"]["city"] for q in questions]
    assert len(set(cities)) == QUESTION_COUNT


def test_same_seed_gives_same_questions():
    records = load_dataset()

    first = build_questions(records, generator=random.Random(7))
    second = build_questions(records, generator=random.Random(7))

    assert first == second


def test_questions_skip_readings_without_pm25():
    records = [
        {"city": "A", "pm2_5": None},
        {"city": "A", "pm2_5": 20.0},
        {"city": "B", "pm2_5": None},
    ]

    questions = build_questions(records, generator=random.Random(1))

    # City B has no valid reading, so only city A can be asked about.
    assert len(questions) == 1
    assert questions[0]["reading"]["city"] == "A"
    assert questions[0]["answer"] == 68


def test_fewer_cities_than_questions_does_not_crash():
    records = [{"city": "A", "pm2_5": 20.0}, {"city": "B", "pm2_5": 30.0}]

    assert len(build_questions(records, count=5)) == 2


# -----------------------------------------
# quiz: clues must not reveal the answer
# -----------------------------------------

def test_clues_hide_pollution_values():
    reading = load_dataset()[0]
    clues = describe_clues(reading)

    assert reading["city"] in clues
    assert "PM2.5" not in clues and "PM10" not in clues and "AQI" not in clues
    assert reading["aqi_category"] not in clues


# -----------------------------------------
# quiz: check_guess
# -----------------------------------------

@pytest.mark.parametrize("guess, answer, expected", [
    (100, 100, "correct"),
    (110, 100, "correct"),          # exactly +tolerance
    (90, 100, "correct"),           # exactly -tolerance
    (111, 100, "lower"),
    (89, 100, "higher"),
    (0, 400, "higher"),
    (500, 3, "lower"),
])
def test_check_guess(guess, answer, expected):
    assert check_guess(guess, answer) == expected


# -----------------------------------------
# quiz: points and rank
# -----------------------------------------

@pytest.mark.parametrize("try_number, points", [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1), (0, 0), (6, 0)])
def test_points_for_try(try_number, points):
    assert points_for_try(try_number) == points


@pytest.mark.parametrize("total, rank", [
    (25, "AQI Expert"), (20, "AQI Expert"),
    (19, "Air Aware"), (13, "Air Aware"),
    (12, "Getting the hang of it"), (5, "Getting the hang of it"),
    (4, "Keep practising"), (0, "Keep practising"),
])
def test_get_rank(total, rank):
    assert get_rank(total, 25) == rank


# -----------------------------------------
# quiz: narrow_range
# -----------------------------------------

def test_narrow_range_after_higher_and_lower():
    low, high = narrow_range(0, 500, 100, "higher")
    assert (low, high) == (111, 500)

    low, high = narrow_range(low, high, 300, "lower")
    assert (low, high) == (111, 289)


def test_narrow_range_never_widens():
    assert narrow_range(200, 300, 50, "higher") == (200, 300)
    assert narrow_range(200, 300, 450, "lower") == (200, 300)


def test_true_answer_always_stays_inside_the_range():
    # Play 200 random games; the answer must never fall outside the range.
    generator = random.Random(3)

    for _ in range(200):
        answer = generator.randint(0, 500)
        low, high = 0, 500

        for _ in range(TRIES_PER_QUESTION):
            guess = generator.randint(0, 500)
            result = check_guess(guess, answer)

            if result == "correct":
                break

            low, high = narrow_range(low, high, guess, result)
            assert low <= answer <= high


def test_five_tries_can_always_win_with_binary_search():
    # Guess the middle of the range each time. Five tries is enough for every answer.
    for answer in range(0, 501):
        low, high = 0, 500
        won = False

        for _ in range(TRIES_PER_QUESTION):
            guess = (low + high) // 2
            result = check_guess(guess, answer)

            if result == "correct":
                won = True
                break

            low, high = narrow_range(low, high, guess, result)

        assert won, "binary search failed for answer " + str(answer)


# -----------------------------------------
# validate_guess
# -----------------------------------------

@pytest.mark.parametrize("text, expected", [("0", 0), ("250", 250), (" 500 ", 500)])
def test_guess_valid(text, expected):
    assert validate_guess(text) == expected


@pytest.mark.parametrize("bad", ["", "  ", "abc", "-5", "12.5", "501", "9999"])
def test_guess_invalid(bad):
    with pytest.raises(ValueError):
        validate_guess(bad)