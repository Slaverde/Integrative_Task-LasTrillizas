import pytest

from src.normalization.fst import END_MARKER, is_deterministic, translate
from src.normalization.transducers import (
    frameworks_transducer,
    languages_transducer,
)
from src.normalization.variants import FRAMEWORK_VARIANTS, key_map
from src.vocabulary import TOKENS, Category

FRAMEWORKS = frameworks_transducer()

FRAMEWORK_CATEGORIES = {
    Category.FRONTEND,
    Category.BACKEND,
    Category.DATA_LIBRARY,
    Category.ML_LIBRARY,
}


def test_every_spelling_of_the_dictionary_is_translated():
    for token, spellings in FRAMEWORK_VARIANTS.items():
        for spelling in spellings:
            assert translate(FRAMEWORKS, spelling) == token, spelling


@pytest.mark.parametrize(
    "raw, token",
    [
        # examples of the assignment
        ("React.js", "REACT"),
        ("ReactJS", "REACT"),
        ("NodeJS", "NODE_JS"),
        ("Node.js", "NODE_JS"),
        ("pandas", "PANDAS"),
        ("sklearn", "SCIKIT_LEARN"),
        ("scikit learn", "SCIKIT_LEARN"),
        ("Scikit-learn", "SCIKIT_LEARN"),
        ("Tensor Flow", "TENSORFLOW"),
        ("TensorFlow", "TENSORFLOW"),
        ("Py Torch", "PYTORCH"),
        ("PyTorch", "PYTORCH"),
        # more spellings
        ("React", "REACT"),
        ("react js", "REACT"),
        ("REACT-JS", "REACT"),
        ("Angular", "ANGULAR"),
        ("AngularJS", "ANGULAR"),
        ("Angular.js", "ANGULAR"),
        ("Vue", "VUE"),
        ("Vue.js", "VUE"),
        ("vuejs", "VUE"),
        ("Next.js", "NEXT_JS"),
        ("Next JS", "NEXT_JS"),
        ("Node JS", "NODE_JS"),
        ("Node js", "NODE_JS"),
        ("NODE-JS", "NODE_JS"),
        ("Express.js", "EXPRESS_JS"),
        ("Django", "DJANGO"),
        ("FLASK", "FLASK"),
        ("FastAPI", "FASTAPI"),
        ("Fast API", "FASTAPI"),
        ("Spring Boot", "SPRING_BOOT"),
        ("SpringBoot", "SPRING_BOOT"),
        ("SPRING-BOOT", "SPRING_BOOT"),
        ("NumPy", "NUMPY"),
        ("Num Py", "NUMPY"),
        ("numpy", "NUMPY"),
        ("scikit_learn", "SCIKIT_LEARN"),
        ("Keras", "KERAS"),
    ],
)
def test_spellings_written_in_different_ways(raw, token):
    assert translate(FRAMEWORKS, raw) == token


@pytest.mark.parametrize(
    "raw",
    [
        "Rea",  # a prefix of REACT
        "Node",  # stage 1 never reports it alone, and it is not a spelling
        "Spring",
        "Scikit",
        "Tensor",
        "Reactive",  # a spelling plus extra letters
        "Angular2",
        "SciPy",  # dropped by design
        "Matplotlib",
        "JS",  # a language, not a framework
        "Python",
        "Postgres",
        "Git",
        "",
        " . ",
        f"React{END_MARKER}",
    ],
)
def test_strings_that_are_not_a_known_framework_are_rejected(raw):
    assert translate(FRAMEWORKS, raw) is None


def test_the_transducer_is_deterministic():
    assert is_deterministic(FRAMEWORKS)


def test_one_initial_state_and_one_final_state_per_token():
    assert len(FRAMEWORKS.start_states) == 1
    assert {str(s) for s in FRAMEWORKS.final_states} == {
        f"f:{token}" for token in FRAMEWORK_VARIANTS
    }


def test_output_alphabet_is_the_set_of_framework_tokens():
    assert {str(s) for s in FRAMEWORKS.output_symbols} == set(FRAMEWORK_VARIANTS)
    for token in FRAMEWORK_VARIANTS:
        assert TOKENS[token] in FRAMEWORK_CATEGORIES, token


def test_a_spelling_is_translated_by_one_transducer_only():
    languages = languages_transducer()
    for token, spellings in FRAMEWORK_VARIANTS.items():
        for spelling in spellings:
            assert translate(languages, spelling) is None, spelling


def test_the_js_inside_a_framework_name_is_not_a_language():
    # stage 1 never reports the "JS" of "Node JS" as a language; the
    # transducers also keep them apart
    languages = languages_transducer()
    assert translate(languages, "JS") == "JAVASCRIPT"
    assert translate(FRAMEWORKS, "JS") is None
    assert translate(FRAMEWORKS, "Node JS") == "NODE_JS"
    assert translate(languages, "Node JS") is None


def test_the_transducer_has_one_path_per_key():
    keys = key_map(FRAMEWORK_VARIANTS)
    end_edges = [s for (_, s) in FRAMEWORKS.transitions if str(s) == END_MARKER]
    assert len(end_edges) == len(keys)
