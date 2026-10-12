import pytest

from src.classification.automata import (
    ALPHABET,
    MACHINE_LEARNING_ENGINEER_REQUIRED,
    build_machine_learning_engineer,
)
from src.vocabulary import Category


@pytest.fixture(scope="module")
def dfa():
    return build_machine_learning_engineer()


def test_is_deterministic(dfa):
    assert dfa.is_deterministic()


def test_alphabet_is_every_category():
    assert ALPHABET == {category.value for category in Category}


def test_states_and_final_state_match_required_length(dfa):
    assert len(dfa.states) == len(MACHINE_LEARNING_ENGINEER_REQUIRED) + 1
    assert dfa.final_states == {f"q{len(MACHINE_LEARNING_ENGINEER_REQUIRED)}"}


def test_accepts_the_assignment_example(dfa):
    # Mary Jane Watson: Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git
    # -> PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT
    # -> LANGUAGE, DATA_LIBRARY, DATA_LIBRARY, ML_LIBRARY, ML_LIBRARY,
    #    DATABASE, VERSION_CONTROL (ML Engineer order)
    sequence = [
        "LANGUAGE",
        "DATA_LIBRARY",
        "DATA_LIBRARY",
        "ML_LIBRARY",
        "ML_LIBRARY",
        "DATABASE",
        "VERSION_CONTROL",
    ]
    assert dfa.accepts(sequence)


def test_accepts_with_only_the_required_categories(dfa):
    sequence = [c.value for c in MACHINE_LEARNING_ENGINEER_REQUIRED]
    assert dfa.accepts(sequence)


@pytest.mark.parametrize(
    "missing",
    ["LANGUAGE", "DATA_LIBRARY", "ML_LIBRARY"],
)
def test_rejects_when_one_required_category_is_missing(dfa, missing):
    sequence = [
        c.value for c in MACHINE_LEARNING_ENGINEER_REQUIRED if c.value != missing
    ]
    assert not dfa.accepts(sequence)


def test_accepts_with_the_optional_categories_interleaved(dfa):
    sequence = [
        "LANGUAGE",
        "CONCEPT",
        "DATA_LIBRARY",
        "DATABASE",
        "ML_LIBRARY",
        "VERSION_CONTROL",
    ]
    assert dfa.accepts(sequence)


def test_rejects_the_empty_sequence(dfa):
    assert not dfa.accepts([])


def test_rejects_only_optional_categories(dfa):
    assert not dfa.accepts(["DATABASE", "VERSION_CONTROL", "CONCEPT"])
