import itertools
import random

import pytest

from src.normalization import sort_by_vocabulary, sort_for_profile
from src.vocabulary import PROFILE_ORDER, TOKENS, Profile

FULL_STACK = Profile.FULL_STACK_DEVELOPER
ML = Profile.MACHINE_LEARNING_ENGINEER


def test_example_of_the_assignment():
    # Git, NodeJS, JS, Postgres, React.js  ->  JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
    tokens = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]
    assert sort_for_profile(tokens, FULL_STACK) == [
        "JAVASCRIPT",
        "REACT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
    ]


def test_example_of_the_assignment_machine_learning():
    tokens = ["GIT", "SQL", "TENSORFLOW", "NUMPY", "SCIKIT_LEARN", "PANDAS", "PYTHON"]
    assert sort_for_profile(tokens, ML) == [
        "PYTHON",
        "PANDAS",
        "NUMPY",
        "SCIKIT_LEARN",
        "TENSORFLOW",
        "SQL",
        "GIT",
    ]


def test_the_same_tokens_give_a_different_order_per_profile():
    tokens = ["GIT", "SQL", "PYTHON", "MACHINE_LEARNING", "PANDAS"]
    assert sort_for_profile(tokens, FULL_STACK) == [
        "PYTHON",
        "SQL",
        "GIT",
        "MACHINE_LEARNING",
        "PANDAS",  # DATA_LIBRARY is not in the Full Stack order: it goes last
    ]
    assert sort_for_profile(tokens, ML) == [
        "PYTHON",
        "PANDAS",
        "MACHINE_LEARNING",
        "SQL",
        "GIT",
    ]


def test_tokens_of_a_category_outside_the_profile_go_last_in_vocabulary_order():
    tokens = ["DOCKER", "PYTORCH", "KERAS", "JAVA", "TENSORFLOW", "GIT"]
    result = sort_for_profile(tokens, FULL_STACK)
    # JAVA and GIT belong to the profile; the ML libraries and DOCKER do not
    assert result == ["JAVA", "GIT", "TENSORFLOW", "PYTORCH", "KERAS", "DOCKER"]


def test_ties_inside_a_category_follow_the_vocabulary():
    tokens = ["PYTHON", "JAVA", "TYPESCRIPT", "JAVASCRIPT"]
    assert sort_for_profile(tokens, FULL_STACK) == [
        "JAVASCRIPT",
        "TYPESCRIPT",
        "PYTHON",
        "JAVA",
    ]


def test_empty_and_single_inputs():
    for profile in Profile:
        assert sort_for_profile([], profile) == []
        assert sort_for_profile(["GIT"], profile) == ["GIT"]


def test_the_input_list_is_not_changed():
    tokens = ["GIT", "JAVASCRIPT"]
    sort_for_profile(tokens, FULL_STACK)
    assert tokens == ["GIT", "JAVASCRIPT"]


def test_unknown_tokens_are_an_error():
    with pytest.raises(ValueError, match="RUST"):
        sort_for_profile(["JAVASCRIPT", "RUST"], FULL_STACK)
    with pytest.raises(ValueError, match="javascript"):
        sort_for_profile(["javascript"], FULL_STACK)  # not canonical (lower case)
    with pytest.raises(ValueError):
        sort_by_vocabulary(["NOPE"])


@pytest.mark.parametrize("profile", list(Profile))
def test_every_profile_goes_through_the_same_function(profile):
    tokens = list(TOKENS)
    result = sort_for_profile(tokens, profile)
    assert sorted(result) == sorted(tokens)  # same tokens, nothing lost
    order = PROFILE_ORDER[profile]
    ranks = [
        order.index(TOKENS[t]) if TOKENS[t] in order else len(order) for t in result
    ]
    assert ranks == sorted(ranks)  # categories appear in the profile order


@pytest.mark.parametrize("profile", list(Profile))
def test_the_result_does_not_depend_on_the_input_order(profile):
    tokens = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT", "DOCKER"]
    expected = sort_for_profile(tokens, profile)
    for permutation in itertools.permutations(tokens):
        assert sort_for_profile(list(permutation), profile) == expected


@pytest.mark.parametrize("profile", list(Profile))
def test_sorting_twice_changes_nothing(profile):
    rng = random.Random(7)
    for _ in range(25):
        tokens = rng.sample(list(TOKENS), rng.randint(0, len(TOKENS)))
        once = sort_for_profile(tokens, profile)
        assert sort_for_profile(once, profile) == once


def test_repeated_tokens_are_kept_next_to_each_other():
    # normalize never repeats a token, but the function must not lose any
    result = sort_for_profile(["GIT", "JAVA", "GIT"], FULL_STACK)
    assert result == ["JAVA", "GIT", "GIT"]


def test_sort_by_vocabulary_follows_the_order_of_tokens():
    tokens = ["GIT", "PANDAS", "JAVASCRIPT", "REACT"]
    assert sort_by_vocabulary(tokens) == ["JAVASCRIPT", "REACT", "GIT", "PANDAS"]
    assert sort_by_vocabulary(list(reversed(list(TOKENS)))) == list(TOKENS)
