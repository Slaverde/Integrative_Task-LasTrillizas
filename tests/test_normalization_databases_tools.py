import pytest

from src.normalization.fst import END_MARKER, is_deterministic, translate
from src.normalization.transducers import (
    databases_tools_transducer,
    frameworks_transducer,
    languages_transducer,
)
from src.normalization.variants import DATABASE_TOOL_VARIANTS, key_map
from src.vocabulary import TOKENS, Category

DB_TOOLS = databases_tools_transducer()

DB_TOOL_CATEGORIES = {
    Category.DATABASE,
    Category.VERSION_CONTROL,
    Category.TOOL,
    Category.CONCEPT,
}


def test_every_spelling_of_the_dictionary_is_translated():
    for token, spellings in DATABASE_TOOL_VARIANTS.items():
        for spelling in spellings:
            assert translate(DB_TOOLS, spelling) == token, spelling


@pytest.mark.parametrize(
    "raw, token",
    [
        # databases
        ("Postgres", "POSTGRESQL"),
        ("PostgreSQL", "POSTGRESQL"),
        ("Postgre SQL", "POSTGRESQL"),
        ("SQL", "SQL"),
        ("sql", "SQL"),
        ("MySQL", "MYSQL"),
        ("My SQL", "MYSQL"),
        ("Mongo", "MONGODB"),
        ("MongoDB", "MONGODB"),
        ("Mongo DB", "MONGODB"),
        ("MariaDB", "MARIADB"),
        ("Maria DB", "MARIADB"),
        ("SQL Server", "SQL_SERVER"),
        ("SQLServer", "SQL_SERVER"),
        ("SQLite", "SQLITE"),
        ("NoSQL", "NOSQL"),
        ("No-SQL", "NOSQL"),
        ("Redis", "REDIS"),
        ("Firebase", "FIREBASE"),
        # version control: hosting services count as Git
        ("Git", "GIT"),
        ("GitHub", "GIT"),
        ("Git Hub", "GIT"),
        ("github", "GIT"),
        ("GitLab", "GIT"),
        ("Bitbucket", "GIT"),
        ("Bit Bucket", "GIT"),
        # tools
        ("Docker", "DOCKER"),
        ("Kubernetes", "KUBERNETES"),
        ("K8s", "KUBERNETES"),
        ("Jupyter", "JUPYTER"),
        ("Jupyter Notebook", "JUPYTER"),
        ("Jupyter Notebooks", "JUPYTER"),
        ("JupyterLab", "JUPYTER"),
        ("Jupyter Lab", "JUPYTER"),
        # concepts
        ("REST API", "REST_API"),
        ("REST APIs", "REST_API"),
        ("REST-API", "REST_API"),
        ("RESTful API", "REST_API"),
        ("RESTful", "REST_API"),
        ("RESTful services", "REST_API"),
        ("RESTful web services", "REST_API"),
        ("API REST", "REST_API"),
        ("GraphQL", "GRAPHQL"),
        ("machine learning", "MACHINE_LEARNING"),
        ("Machine-learning model development", "MACHINE_LEARNING"),
        ("machine learning models", "MACHINE_LEARNING"),
        ("ML", "MACHINE_LEARNING"),
        ("aprendizaje automático", "MACHINE_LEARNING"),
        ("aprendizaje automatico", "MACHINE_LEARNING"),
        ("Aprendizaje de máquinas", "MACHINE_LEARNING"),
        ("aprendizaje profundo", "MACHINE_LEARNING"),
        ("Deep learning", "MACHINE_LEARNING"),
        ("deep-learning", "MACHINE_LEARNING"),
        ("predictive models", "MACHINE_LEARNING"),
        ("predictive modeling", "MACHINE_LEARNING"),
        ("modelos predictivos", "MACHINE_LEARNING"),
    ],
)
def test_spellings_written_in_different_ways(raw, token):
    assert translate(DB_TOOLS, raw) == token


@pytest.mark.parametrize(
    "raw",
    [
        "Postgre",  # a prefix of POSTGRESQL
        "Mon",
        "REST",  # an ordinary word; stage 1 does not report it either
        "API",
        "machine",
        "learning",
        "deep",
        "Jupyter Notebookz",
        "SQLs",
        "Gitt",
        # technologies that are dropped by design (decision D2)
        "Jenkins",
        "Jira",
        "AWS",
        "Linux",
        "CI/CD",
        "microservices",
        "data-processing pipelines",
        # other kinds of qualification
        "JS",
        "React",
        "",
        " - ",
        f"Git{END_MARKER}",
    ],
)
def test_strings_that_are_not_a_known_database_tool_or_concept_are_rejected(raw):
    assert translate(DB_TOOLS, raw) is None


def test_the_transducer_is_deterministic():
    assert is_deterministic(DB_TOOLS)


def test_one_initial_state_and_one_final_state_per_token():
    assert len(DB_TOOLS.start_states) == 1
    assert {str(s) for s in DB_TOOLS.final_states} == {
        f"f:{token}" for token in DATABASE_TOOL_VARIANTS
    }


def test_output_alphabet_is_the_set_of_database_tool_and_concept_tokens():
    assert {str(s) for s in DB_TOOLS.output_symbols} == set(DATABASE_TOOL_VARIANTS)
    for token in DATABASE_TOOL_VARIANTS:
        assert TOKENS[token] in DB_TOOL_CATEGORIES, token


def test_several_spellings_share_one_final_state():
    finals = {str(s) for s in DB_TOOLS.final_states}
    assert "f:GIT" in finals
    into_git = [
        (source, symbol)
        for (source, symbol), targets in DB_TOOLS.transitions.items()
        if str(symbol) == END_MARKER and any(str(t) == "f:GIT" for t, _ in targets)
    ]
    # Git, GitHub, GitLab and Bitbucket: four different keys, one final state
    assert len(into_git) == 4


def test_a_spelling_is_translated_by_one_transducer_only():
    others = [languages_transducer(), frameworks_transducer()]
    for spellings in DATABASE_TOOL_VARIANTS.values():
        for spelling in spellings:
            for other in others:
                assert translate(other, spelling) is None, spelling


def test_the_transducer_has_one_path_per_key():
    keys = key_map(DATABASE_TOOL_VARIANTS)
    end_edges = [s for (_, s) in DB_TOOLS.transitions if str(s) == END_MARKER]
    assert len(end_edges) == len(keys)
