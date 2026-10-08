import pytest

from src.contracts import ExtractionResult
from src.extraction import extract
from src.normalization import normalize, normalize_skill
from src.normalization.transducers import all_transducers, canonical_token
from src.normalization.variants import GROUPS
from src.vocabulary import TOKENS


def test_example_of_the_assignment_full_stack():
    # stage 1 gives: JS, React.js, NodeJS, Postgres, Git
    extracted = ExtractionResult(
        languages=["JS"],
        frameworks=["React.js", "NodeJS"],
        databases=["Postgres"],
        tools=["Git"],
    )
    assert normalize(extracted) == [
        "JAVASCRIPT",
        "REACT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
    ]


def test_example_of_the_assignment_machine_learning():
    extracted = ExtractionResult(
        languages=["Python"],
        frameworks=["Pandas", "NumPy", "Scikit-learn", "TensorFlow"],
        databases=["SQL"],
        tools=["Git"],
        concepts=["predictive models", "data-processing pipelines"],
    )
    assert normalize(extracted) == [
        "PYTHON",
        "PANDAS",
        "NUMPY",
        "SCIKIT_LEARN",
        "TENSORFLOW",
        "SQL",
        "GIT",
        "MACHINE_LEARNING",  # predictive models (decision D4)
        # "data-processing pipelines" has no canonical form and is dropped
    ]


def test_normalize_runs_on_the_output_of_stage_1():
    text = (
        "Wednesday Addams\n"
        "3 years of experience developing web applications.\n"
        "Technical Skills: JS, React.js, NodeJS, Postgres, Git.\n"
    )
    assert normalize(extract(text)) == [
        "JAVASCRIPT",
        "REACT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
    ]


def test_an_empty_extraction_gives_no_tokens():
    assert normalize(ExtractionResult()) == []


def test_unknown_strings_are_dropped():
    extracted = ExtractionResult(languages=["Rust", "JS"], tools=["Jenkins", "AWS"])
    assert normalize(extracted) == ["JAVASCRIPT"]


def test_two_spellings_of_one_technology_give_one_token():
    extracted = ExtractionResult(
        languages=["JS", "Javascript"],
        databases=["Postgres", "PostgreSQL"],
        tools=["Git", "GitHub"],
    )
    assert normalize(extracted) == ["JAVASCRIPT", "POSTGRESQL", "GIT"]


def test_order_is_first_appearance_by_field():
    extracted = ExtractionResult(
        languages=["TS", "JS"],
        frameworks=["Vue", "React"],
        databases=["Mongo"],
        tools=["Docker"],
        concepts=["GraphQL"],
    )
    assert normalize(extracted) == [
        "TYPESCRIPT",
        "JAVASCRIPT",
        "VUE",
        "REACT",
        "MONGODB",
        "DOCKER",
        "GRAPHQL",
    ]


def test_every_output_is_a_token_of_the_vocabulary():
    extracted = ExtractionResult(
        languages=["JS", "C++"],
        frameworks=["Next.js", "sklearn"],
        databases=["SQL Server"],
        tools=["K8s"],
        concepts=["ML"],
    )
    for token in normalize(extracted):
        assert token in TOKENS


def test_normalize_does_not_change_its_input():
    extracted = ExtractionResult(languages=["JS"], tools=["Git"])
    before = extracted.to_dict()
    normalize(extracted)
    assert extracted.to_dict() == before


def test_normalize_skill_is_the_function_that_normalize_applies():
    assert normalize_skill is canonical_token
    assert normalize_skill("Node.js") == "NODE_JS"
    assert normalize_skill("Rust") is None
    assert normalize_skill("") is None


@pytest.mark.parametrize("group", list(GROUPS))
def test_all_transducers_are_registered_in_order(group):
    assert group in all_transducers()
    assert list(all_transducers()) == list(GROUPS)
