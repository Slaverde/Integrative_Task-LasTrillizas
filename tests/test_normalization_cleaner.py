import string

import pytest

from src.normalization.fst import build_cleaner, clean, is_deterministic
from src.normalization.variants import ACCENTS, SEPARATORS, variant_key


def test_cleaner_has_one_state_that_is_initial_and_final():
    cleaner = build_cleaner()
    assert len(cleaner.states) == 1
    assert cleaner.start_states == cleaner.final_states == cleaner.states


def test_cleaner_is_deterministic():
    assert is_deterministic(build_cleaner())


def test_cleaner_output_alphabet_is_upper_case_digits_and_plus():
    expected = set(string.ascii_uppercase + string.digits + "+")
    assert {str(s) for s in build_cleaner().output_symbols} == expected


@pytest.mark.parametrize(
    "text, key",
    [
        ("JS", "JS"),
        ("Javascript", "JAVASCRIPT"),
        ("Node.js", "NODEJS"),
        ("Node JS", "NODEJS"),
        ("SPRING-BOOT", "SPRINGBOOT"),
        ("scikit learn", "SCIKITLEARN"),
        ("Scikit-learn", "SCIKITLEARN"),
        ("Py Torch", "PYTORCH"),
        ("C++", "C++"),
        ("Python3", "PYTHON3"),
        ("aprendizaje automático", "APRENDIZAJEAUTOMATICO"),
        ("APRENDIZAJE DE MÁQUINA", "APRENDIZAJEDEMAQUINA"),
        ("modelos predictivos", "MODELOSPREDICTIVOS"),
        ("a\tb  c", "ABC"),
    ],
)
def test_cleaner_writes_the_key(text, key):
    assert clean(text) == key


def test_cleaner_accepts_the_empty_string_and_only_separators():
    assert clean("") == ""
    assert clean(" - . _ ") == ""


@pytest.mark.parametrize(
    "text", ["C#", "CI/CD", "node@12", "a•b", "R&D", "🙂", "tab\nnewline", "(React)"]
)
def test_cleaner_rejects_characters_it_does_not_know(text):
    assert clean(text) is None


def test_cleaner_matches_the_reference_function_on_every_single_character():
    # variant_key is the reference definition: same answer, or both reject.
    for code in range(0, 0x250):
        char = chr(code)
        try:
            expected = variant_key(char)
        except ValueError:
            expected = None
        assert clean(char) == expected, repr(char)


def test_cleaner_matches_the_reference_function_on_words():
    words = [
        "Machine-learning model development",
        "Mongo DB",
        "React.js, NodeJS",  # the comma is not a separator
        "ÁÉÍÓÚ ñ ü",
        "snake_case_name",
        "x" * 500,
    ]
    for word in words:
        try:
            expected = variant_key(word)
        except ValueError:
            expected = None
        assert clean(word) == expected, word


def test_separators_and_accents_are_all_covered():
    for char in SEPARATORS:
        assert clean(char) == ""
    for char, plain in ACCENTS.items():
        assert clean(char) == plain


def test_case_does_not_change_the_key():
    for word in ["Python", "react.js", "NodeJS", "scikit-learn"]:
        assert clean(word.lower()) == clean(word.upper()) == clean(word.title())
