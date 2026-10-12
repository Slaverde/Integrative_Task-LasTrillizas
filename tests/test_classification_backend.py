import pytest

from src.classification.automata import (
    ALPHABET,
    BACKEND_DEVELOPER_REQUIRED,
    build_backend_developer,
)
from src.vocabulary import Category


@pytest.fixture(scope="module")
def dfa():
    return build_backend_developer()


def test_is_deterministic(dfa):
    assert dfa.is_deterministic()


def test_alphabet_is_every_category():
    assert ALPHABET == {category.value for category in Category}


def test_states_and_final_state_match_required_length(dfa):
    assert len(dfa.states) == len(BACKEND_DEVELOPER_REQUIRED) + 1
    assert dfa.final_states == {f"q{len(BACKEND_DEVELOPER_REQUIRED)}"}


def test_accepts_a_server_side_resume():
    # Java, Spring Boot, PostgreSQL, Git -> JAVA, SPRING_BOOT, POSTGRESQL, GIT
    # -> LANGUAGE, BACKEND, DATABASE, VERSION_CONTROL
    sequence = [c.value for c in BACKEND_DEVELOPER_REQUIRED]
    assert build_backend_developer().accepts(sequence)


@pytest.mark.parametrize(
    "missing",
    ["LANGUAGE", "BACKEND", "DATABASE", "VERSION_CONTROL"],
)
def test_rejects_when_one_required_category_is_missing(dfa, missing):
    sequence = [c.value for c in BACKEND_DEVELOPER_REQUIRED if c.value != missing]
    assert not dfa.accepts(sequence)


def test_rejects_a_frontend_only_resume_in_place_of_backend(dfa):
    # FRONTEND is not BACKEND: a Full Stack-style resume that never lists a
    # backend framework must not satisfy BACKEND_DEVELOPER.
    sequence = ["LANGUAGE", "FRONTEND", "DATABASE", "VERSION_CONTROL"]
    assert not dfa.accepts(sequence)


def test_accepts_with_the_optional_concept_and_tool_categories(dfa):
    sequence = [
        "LANGUAGE",
        "BACKEND",
        "TOOL",
        "DATABASE",
        "CONCEPT",
        "VERSION_CONTROL",
    ]
    assert dfa.accepts(sequence)


def test_rejects_the_empty_sequence(dfa):
    assert not dfa.accepts([])
