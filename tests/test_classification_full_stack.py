import pytest

from src.classification.automata import (
    ALPHABET,
    FULL_STACK_REQUIRED,
    build_full_stack_developer,
)
from src.vocabulary import Category


@pytest.fixture(scope="module")
def dfa():
    return build_full_stack_developer()


def test_is_deterministic(dfa):
    assert dfa.is_deterministic()


def test_alphabet_is_every_category():
    assert ALPHABET == {category.value for category in Category}


def test_states_and_final_state_match_required_length(dfa):
    assert len(dfa.states) == len(FULL_STACK_REQUIRED) + 1
    assert dfa.final_states == {f"q{len(FULL_STACK_REQUIRED)}"}


def test_accepts_the_assignment_example(dfa):
    # Wednesday Addams: JS, React.js, NodeJS, Postgres, Git
    # -> JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT (stage 2, Full Stack order)
    # -> LANGUAGE, FRONTEND, BACKEND, DATABASE, VERSION_CONTROL
    sequence = ["LANGUAGE", "FRONTEND", "BACKEND", "DATABASE", "VERSION_CONTROL"]
    assert dfa.accepts(sequence)


@pytest.mark.parametrize(
    "missing",
    ["LANGUAGE", "FRONTEND", "BACKEND", "DATABASE", "VERSION_CONTROL"],
)
def test_rejects_when_one_required_category_is_missing(dfa, missing):
    sequence = [c.value for c in FULL_STACK_REQUIRED if c.value != missing]
    assert not dfa.accepts(sequence)


def test_accepts_with_the_optional_concept_category_interleaved(dfa):
    sequence = [
        "LANGUAGE",
        "CONCEPT",
        "FRONTEND",
        "BACKEND",
        "DATABASE",
        "VERSION_CONTROL",
    ]
    assert dfa.accepts(sequence)


def test_accepts_with_a_repeated_required_category(dfa):
    sequence = ["LANGUAGE", "LANGUAGE", "FRONTEND", "BACKEND", "DATABASE", "VERSION_CONTROL"]
    assert dfa.accepts(sequence)


def test_rejects_the_empty_sequence(dfa):
    assert not dfa.accepts([])


def test_rejects_only_optional_categories(dfa):
    assert not dfa.accepts(["CONCEPT", "TOOL"])
