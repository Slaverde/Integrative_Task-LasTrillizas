"""Stage 2 on the example resumes and on every spelling that stage 1 reports."""

from pathlib import Path

import pytest

from src.extraction import extract
from src.normalization import normalize, normalize_skill

RESUMES = Path(__file__).resolve().parents[1] / "examples" / "resumes"


def read(name: str) -> str:
    return (RESUMES / f"{name}.txt").read_text(encoding="utf-8")


# resume -> (tokens that normalize must give, raw strings that are dropped)
EXPECTED = {
    # A. Full Stack from the assignment
    "wednesday_addams": (
        ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
        [],
    ),
    # B. ML Engineer from the assignment: predictive models count as ML (D4),
    # data-processing pipelines do not
    "mary_jane_watson": (
        [
            "PYTHON",
            "PANDAS",
            "NUMPY",
            "SCIKIT_LEARN",
            "TENSORFLOW",
            "SQL",
            "GIT",
            "MACHINE_LEARNING",
        ],
        ["data-processing pipelines"],
    ),
    # C. Many spellings: GitHub is Git (D3), Postman is dropped (D2)
    "ana_torres": (
        [
            "JAVASCRIPT",
            "TYPESCRIPT",
            "REACT",
            "NODE_JS",
            "POSTGRESQL",
            "MONGODB",
            "GIT",
            "REST_API",
            "GRAPHQL",
        ],
        ["Postman"],
    ),
    # D. Backend: Spring Boot and SPRING-BOOT are one token, so are REST APIs
    # and RESTful APIs
    "carlos_ruiz": (
        [
            "JAVA",
            "SPRING_BOOT",
            "MYSQL",
            "REDIS",
            "DOCKER",
            "KUBERNETES",
            "GIT",
            "REST_API",
        ],
        ["CI/CD", "Jenkins", "microservices"],
    ),
    # E. Data profile in Spanish and lower case
    "laura_gomez": (
        [
            "PYTHON",
            "PANDAS",
            "NUMPY",
            "SCIKIT_LEARN",
            "PYTORCH",
            "POSTGRESQL",
            "MONGODB",
            "DOCKER",
            "GIT",
            "JUPYTER",
            "MACHINE_LEARNING",
        ],
        [],
    ),
    # F. No technical skills
    "sofia_nunez": ([], []),
}


@pytest.mark.parametrize("name", list(EXPECTED))
def test_normalize_on_the_example_resumes(name):
    tokens, _ = EXPECTED[name]
    assert normalize(extract(read(name))) == tokens


@pytest.mark.parametrize("name", list(EXPECTED))
def test_the_dropped_strings_are_the_expected_ones(name):
    _, dropped = EXPECTED[name]
    raw = extract(read(name)).raw_skills()
    assert [r for r in raw if normalize_skill(r) is None] == dropped


def test_every_example_resume_has_an_expected_result():
    assert {p.stem for p in RESUMES.glob("*.txt")} == set(EXPECTED)


# --- every spelling that stage 1 can report ---------------------------------
# (field of ExtractionResult, spelling, token or None when it is dropped)

SPELLINGS = [
    # languages
    ("languages", "JS", "JAVASCRIPT"),
    ("languages", "Javascript", "JAVASCRIPT"),
    ("languages", "Java Script", "JAVASCRIPT"),
    ("languages", "ECMAScript", "JAVASCRIPT"),
    ("languages", "TS", "TYPESCRIPT"),
    ("languages", "TypeScript", "TYPESCRIPT"),
    ("languages", "Type Script", "TYPESCRIPT"),
    ("languages", "Python", "PYTHON"),
    ("languages", "Python3", "PYTHON"),
    ("languages", "Java", "JAVA"),
    ("languages", "Kotlin", "KOTLIN"),
    ("languages", "C++", "CPP"),
    ("languages", "C#", None),
    ("languages", "PHP", None),
    ("languages", "Golang", None),
    ("languages", "Swift", None),
    ("languages", "Rust", None),
    ("languages", "Ruby", None),
    ("languages", "Scala", None),
    # frameworks and libraries
    ("frameworks", "React", "REACT"),
    ("frameworks", "React.js", "REACT"),
    ("frameworks", "ReactJS", "REACT"),
    ("frameworks", "React JS", "REACT"),
    ("frameworks", "Angular", "ANGULAR"),
    ("frameworks", "AngularJS", "ANGULAR"),
    ("frameworks", "Vue", "VUE"),
    ("frameworks", "Vue.js", "VUE"),
    ("frameworks", "VueJS", "VUE"),
    ("frameworks", "Next.js", "NEXT_JS"),
    ("frameworks", "NextJS", "NEXT_JS"),
    ("frameworks", "Node.js", "NODE_JS"),
    ("frameworks", "NodeJS", "NODE_JS"),
    ("frameworks", "Node JS", "NODE_JS"),
    ("frameworks", "Express.js", "EXPRESS_JS"),
    ("frameworks", "Django", "DJANGO"),
    ("frameworks", "Flask", "FLASK"),
    ("frameworks", "FastAPI", "FASTAPI"),
    ("frameworks", "Fast API", "FASTAPI"),
    ("frameworks", "Spring Boot", "SPRING_BOOT"),
    ("frameworks", "SpringBoot", "SPRING_BOOT"),
    ("frameworks", "SPRING-BOOT", "SPRING_BOOT"),
    ("frameworks", "Pandas", "PANDAS"),
    ("frameworks", "NumPy", "NUMPY"),
    ("frameworks", "Num Py", "NUMPY"),
    ("frameworks", "SciPy", None),
    ("frameworks", "scikit learn", "SCIKIT_LEARN"),
    ("frameworks", "Scikit-learn", "SCIKIT_LEARN"),
    ("frameworks", "sklearn", "SCIKIT_LEARN"),
    ("frameworks", "TensorFlow", "TENSORFLOW"),
    ("frameworks", "Tensor Flow", "TENSORFLOW"),
    ("frameworks", "PyTorch", "PYTORCH"),
    ("frameworks", "Py Torch", "PYTORCH"),
    ("frameworks", "Keras", "KERAS"),
    ("frameworks", "Matplotlib", None),
    # databases
    ("databases", "PostgreSQL", "POSTGRESQL"),
    ("databases", "Postgre SQL", "POSTGRESQL"),
    ("databases", "Postgres", "POSTGRESQL"),
    ("databases", "MySQL", "MYSQL"),
    ("databases", "My SQL", "MYSQL"),
    ("databases", "MariaDB", "MARIADB"),
    ("databases", "MongoDB", "MONGODB"),
    ("databases", "Mongo DB", "MONGODB"),
    ("databases", "Mongo", "MONGODB"),
    ("databases", "SQL Server", "SQL_SERVER"),
    ("databases", "SQLite", "SQLITE"),
    ("databases", "NoSQL", "NOSQL"),
    ("databases", "No-SQL", "NOSQL"),
    ("databases", "Redis", "REDIS"),
    ("databases", "Firebase", "FIREBASE"),
    ("databases", "SQL", "SQL"),
    # tools
    ("tools", "GitHub", "GIT"),
    ("tools", "Git Hub", "GIT"),
    ("tools", "GitLab", "GIT"),
    ("tools", "Bitbucket", "GIT"),
    ("tools", "Git", "GIT"),
    ("tools", "Docker", "DOCKER"),
    ("tools", "Kubernetes", "KUBERNETES"),
    ("tools", "K8s", "KUBERNETES"),
    ("tools", "Jupyter", "JUPYTER"),
    ("tools", "Jupyter Notebook", "JUPYTER"),
    ("tools", "JupyterLab", "JUPYTER"),
    ("tools", "Jenkins", None),
    ("tools", "Jira", None),
    ("tools", "Postman", None),
    ("tools", "Linux", None),
    ("tools", "AWS", None),
    ("tools", "Azure", None),
    ("tools", "GCP", None),
    ("tools", "npm", None),
    ("tools", "webpack", None),
    ("tools", "Maven", None),
    ("tools", "Gradle", None),
    ("tools", "CI/CD", None),
    # concepts
    ("concepts", "REST API", "REST_API"),
    ("concepts", "REST APIs", "REST_API"),
    ("concepts", "RESTful API", "REST_API"),
    ("concepts", "RESTful", "REST_API"),
    ("concepts", "RESTful services", "REST_API"),
    ("concepts", "RESTful web services", "REST_API"),
    ("concepts", "API REST", "REST_API"),
    ("concepts", "GraphQL", "GRAPHQL"),
    ("concepts", "microservices", None),
    ("concepts", "machine learning", "MACHINE_LEARNING"),
    ("concepts", "Machine-learning model development", "MACHINE_LEARNING"),
    ("concepts", "aprendizaje automático", "MACHINE_LEARNING"),
    ("concepts", "aprendizaje de máquina", "MACHINE_LEARNING"),
    ("concepts", "aprendizaje profundo", "MACHINE_LEARNING"),
    ("concepts", "deep learning", "MACHINE_LEARNING"),
    ("concepts", "predictive models", "MACHINE_LEARNING"),
    ("concepts", "predictive modeling", "MACHINE_LEARNING"),
    ("concepts", "modelos predictivos", "MACHINE_LEARNING"),
    ("concepts", "data-processing pipelines", None),
    ("concepts", "ML", "MACHINE_LEARNING"),
]


@pytest.mark.parametrize("field, spelling, token", SPELLINGS)
def test_every_spelling_that_stage_1_reports_has_a_decision(field, spelling, token):
    # stage 1 really reports this spelling in this field...
    reported = getattr(extract(f"Skills: {spelling}."), field)
    assert spelling in reported, f"stage 1 gave {reported} for {spelling!r}"
    # ...and stage 2 either maps it to a token or drops it on purpose
    assert normalize_skill(spelling) == token


def test_the_table_has_one_row_per_spelling():
    rows = [(field, spelling) for field, spelling, _ in SPELLINGS]
    assert len(rows) == len(set(rows))
