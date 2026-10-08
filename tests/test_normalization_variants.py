import pytest

from src.normalization.variants import (
    DATABASE_TOOL_VARIANTS,
    FRAMEWORK_VARIANTS,
    GROUPS,
    LANGUAGE_VARIANTS,
    key_map,
    variant_key,
)
from src.vocabulary import TOKENS, Category

# --- variant_key: the reference definition of the cleaner --------------------


@pytest.mark.parametrize(
    "spelling, key",
    [
        ("JS", "JS"),
        ("Javascript", "JAVASCRIPT"),
        ("Java Script", "JAVASCRIPT"),
        ("React.js", "REACTJS"),
        ("react-js", "REACTJS"),
        ("Node JS", "NODEJS"),
        ("SPRING-BOOT", "SPRINGBOOT"),
        ("Scikit-learn", "SCIKITLEARN"),
        ("scikit learn", "SCIKITLEARN"),
        ("Tensor Flow", "TENSORFLOW"),
        ("C++", "C++"),
        ("aprendizaje automático", "APRENDIZAJEAUTOMATICO"),
        ("APRENDIZAJE AUTOMÁTICO", "APRENDIZAJEAUTOMATICO"),
        ("  Git  ", "GIT"),
        ("snake_case", "SNAKECASE"),
    ],
)
def test_variant_key_ignores_case_accents_and_separators(spelling, key):
    assert variant_key(spelling) == key


@pytest.mark.parametrize("spelling", ["C#", "CI/CD", "node@12", "a•b", "R&D"])
def test_variant_key_rejects_unknown_characters(spelling):
    with pytest.raises(ValueError):
        variant_key(spelling)


def test_variant_key_of_empty_text_is_empty():
    assert variant_key("") == ""
    assert variant_key(" - . ") == ""


# --- The dictionary ----------------------------------------------------------


def test_every_canonical_token_is_in_the_vocabulary():
    for group in GROUPS.values():
        for token in group:
            assert token in TOKENS, token


def test_every_vocabulary_token_can_be_produced():
    produced = {token for group in GROUPS.values() for token in group}
    assert produced == set(TOKENS)


def test_a_token_belongs_to_one_group_only():
    seen: dict[str, str] = {}
    for name, group in GROUPS.items():
        for token in group:
            assert token not in seen, f"{token} in {seen.get(token)} and {name}"
            seen[token] = name


def test_every_token_has_at_least_one_spelling():
    for group in GROUPS.values():
        for token, spellings in group.items():
            assert spellings, token


def test_groups_follow_the_categories_of_the_vocabulary():
    assert {TOKENS[t] for t in LANGUAGE_VARIANTS} == {Category.LANGUAGE}
    assert {TOKENS[t] for t in FRAMEWORK_VARIANTS} == {
        Category.FRONTEND,
        Category.BACKEND,
        Category.DATA_LIBRARY,
        Category.ML_LIBRARY,
    }
    assert {TOKENS[t] for t in DATABASE_TOOL_VARIANTS} == {
        Category.DATABASE,
        Category.VERSION_CONTROL,
        Category.TOOL,
        Category.CONCEPT,
    }


def test_no_key_is_repeated_inside_a_group():
    # key_map raises ValueError on a repeated key
    for group in GROUPS.values():
        key_map(group)


def test_no_key_is_shared_between_groups():
    all_keys: dict[str, str] = {}
    for name, group in GROUPS.items():
        for key in key_map(group):
            assert key not in all_keys, f"{key} in {all_keys.get(key)} and {name}"
            all_keys[key] = name


def test_key_map_rejects_two_spellings_with_the_same_key():
    with pytest.raises(ValueError, match="already used"):
        key_map({"JAVASCRIPT": ("JavaScript", "Java Script")})
    with pytest.raises(ValueError, match="already used"):
        key_map({"A": ("Node.js",), "B": ("node js",)})


def test_every_spelling_is_a_valid_input_for_the_cleaner():
    for group in GROUPS.values():
        for spellings in group.values():
            for spelling in spellings:
                assert variant_key(spelling)


# --- Examples of the assignment ---------------------------------------------


@pytest.mark.parametrize(
    "spelling, token",
    [
        ("JS", "JAVASCRIPT"),
        ("Javascript", "JAVASCRIPT"),
        ("React.js", "REACT"),
        ("ReactJS", "REACT"),
        ("NodeJS", "NODE_JS"),
        ("Node.js", "NODE_JS"),
        ("Postgres", "POSTGRESQL"),
        ("PostgreSQL", "POSTGRESQL"),
        ("pandas", "PANDAS"),
        ("sklearn", "SCIKIT_LEARN"),
        ("scikit learn", "SCIKIT_LEARN"),
        ("Scikit-learn", "SCIKIT_LEARN"),
        ("Tensor Flow", "TENSORFLOW"),
        ("TensorFlow", "TENSORFLOW"),
        ("Py Torch", "PYTORCH"),
        ("PyTorch", "PYTORCH"),
    ],
)
def test_the_assignment_examples_are_in_the_dictionary(spelling, token):
    # Note: React.js and ReactJS share the key REACTJS, so only the key counts.
    keys = {}
    for group in GROUPS.values():
        keys.update(key_map(group))
    assert keys[variant_key(spelling)] == token
