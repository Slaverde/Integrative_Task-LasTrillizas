import pytest

from src.classification.automata import (
    ALPHABET,
    DATA_SCIENTIST_REQUIRED,
    build_data_scientist,
)
from src.vocabulary import Category


@pytest.fixture(scope="module")
def dfa():
    return build_data_scientist()


def test_is_deterministic(dfa):
    assert dfa.is_deterministic()


def test_alphabet_is_every_category():
    assert ALPHABET == {category.value for category in Category}


def test_states_and_final_state_match_required_length(dfa):
    assert len(dfa.states) == len(DATA_SCIENTIST_REQUIRED) + 1
    assert dfa.final_states == {f"q{len(DATA_SCIENTIST_REQUIRED)}"}


def test_accepts_a_data_analysis_resume(dfa):
    # Python, Pandas, PostgreSQL, Jupyter
    # -> LANGUAGE, DATA_LIBRARY, DATABASE, TOOL
    sequence = [c.value for c in DATA_SCIENTIST_REQUIRED]
    assert dfa.accepts(sequence)


@pytest.mark.parametrize(
    "missing",
    ["LANGUAGE", "DATA_LIBRARY", "DATABASE", "TOOL"],
)
def test_rejects_when_one_required_category_is_missing(dfa, missing):
    sequence = [c.value for c in DATA_SCIENTIST_REQUIRED if c.value != missing]
    assert not dfa.accepts(sequence)


def test_rejects_a_typical_machine_learning_engineer_resume(dfa):
    # LANGUAGE, DATA_LIBRARY, ML_LIBRARY satisfies MACHINE_LEARNING_ENGINEER
    # but has neither DATABASE nor TOOL, so it must not satisfy DATA_SCIENTIST.
    sequence = ["LANGUAGE", "DATA_LIBRARY", "ML_LIBRARY"]
    assert not dfa.accepts(sequence)


def test_accepts_with_the_optional_ml_library_and_version_control(dfa):
    sequence = [
        "LANGUAGE",
        "DATA_LIBRARY",
        "ML_LIBRARY",
        "DATABASE",
        "TOOL",
        "VERSION_CONTROL",
    ]
    assert dfa.accepts(sequence)


def test_rejects_the_empty_sequence(dfa):
    assert not dfa.accepts([])
