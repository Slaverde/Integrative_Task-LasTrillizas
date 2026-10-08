import pytest

from src.normalization.fst import (
    END_MARKER,
    build_transducer,
    is_deterministic,
    translate,
    translate_key,
)
from src.normalization.transducers import languages_transducer
from src.normalization.variants import LANGUAGE_VARIANTS, key_map, variant_key
from src.vocabulary import TOKENS, Category

LANGUAGES = languages_transducer()


def test_every_spelling_of_the_dictionary_is_translated():
    for token, spellings in LANGUAGE_VARIANTS.items():
        for spelling in spellings:
            assert translate(LANGUAGES, spelling) == token, spelling


@pytest.mark.parametrize(
    "raw, token",
    [
        ("JS", "JAVASCRIPT"),
        ("Javascript", "JAVASCRIPT"),
        ("JavaScript", "JAVASCRIPT"),
        ("Java Script", "JAVASCRIPT"),
        ("java-script", "JAVASCRIPT"),
        ("ECMAScript", "JAVASCRIPT"),
        ("ts", "TYPESCRIPT"),
        ("Type Script", "TYPESCRIPT"),
        ("TYPESCRIPT", "TYPESCRIPT"),
        ("python", "PYTHON"),
        ("Python3", "PYTHON"),
        ("Python 3", "PYTHON"),
        ("Java", "JAVA"),
        ("kotlin", "KOTLIN"),
        ("C++", "CPP"),
        ("c++", "CPP"),
    ],
)
def test_spellings_written_in_different_ways(raw, token):
    assert translate(LANGUAGES, raw) == token


@pytest.mark.parametrize(
    "raw",
    [
        "J",  # a prefix of JS, JAVA and JAVASCRIPT
        "JAV",
        "JAVASC",
        "Pyth",
        "Javascripts",  # a spelling plus an extra letter
        "JS2",
        "Rust",  # a language that is dropped by design
        "C#",
        "Go",
        "React",  # a framework, not a language
        "Git",
        "",
        "   ",
        "-",
        "J S S",  # the key is JSS
        f"JS{END_MARKER}",
    ],
)
def test_strings_that_are_not_a_known_language_are_rejected(raw):
    assert translate(LANGUAGES, raw) is None


def test_java_and_javascript_are_different_tokens():
    # JAVA is a prefix of JAVASCRIPT: this is why the end marker exists
    assert translate(LANGUAGES, "Java") == "JAVA"
    assert translate(LANGUAGES, "JavaScript") == "JAVASCRIPT"


def test_the_transducer_is_deterministic():
    assert is_deterministic(LANGUAGES)


def test_one_initial_state_and_one_final_state_per_token():
    assert len(LANGUAGES.start_states) == 1
    assert {str(s) for s in LANGUAGES.final_states} == {
        f"f:{token}" for token in LANGUAGE_VARIANTS
    }


def test_output_alphabet_is_the_set_of_language_tokens():
    assert {str(s) for s in LANGUAGES.output_symbols} == set(LANGUAGE_VARIANTS)
    for token in LANGUAGE_VARIANTS:
        assert TOKENS[token] == Category.LANGUAGE


def test_input_alphabet_is_the_key_alphabet_plus_the_end_marker():
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+") | {END_MARKER}
    assert {str(s) for s in LANGUAGES.input_symbols} <= allowed


def test_only_the_end_marker_writes_output():
    for (_, symbol), targets in LANGUAGES.transitions.items():
        for _, output in targets:
            if str(symbol) == END_MARKER:
                assert len(output) == 1
            else:
                assert output == []


def test_translate_key_works_on_keys_and_needs_the_exact_key():
    assert translate_key(LANGUAGES, "JAVASCRIPT") == "JAVASCRIPT"
    assert translate_key(LANGUAGES, "JS") == "JAVASCRIPT"
    assert translate_key(LANGUAGES, "js") is None  # keys are upper case
    assert translate_key(LANGUAGES, "JAVA SCRIPT") is None  # keys have no spaces


def test_the_transducer_has_one_path_per_key():
    keys = key_map(LANGUAGE_VARIANTS)
    total_end_edges = sum(
        1 for (_, symbol) in LANGUAGES.transitions if str(symbol) == END_MARKER
    )
    assert total_end_edges == len(keys)


def test_a_new_transducer_can_be_built_from_any_dictionary():
    tiny = build_transducer({"PYTHON": ("py", "Python")})
    assert translate(tiny, "Py") == "PYTHON"
    assert translate(tiny, "PYTHON") == "PYTHON"
    assert translate(tiny, "Java") is None
    assert variant_key("py") == "PY"
