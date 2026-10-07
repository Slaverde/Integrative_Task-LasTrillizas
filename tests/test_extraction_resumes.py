"""End-to-end tests of stage 1 over the example resumes and edge cases."""

from pathlib import Path

import pytest

from src.extraction import extract

RESUMES = Path(__file__).resolve().parent.parent / "examples" / "resumes"
SKILL_FIELDS = ("languages", "frameworks", "databases", "tools", "concepts")


def read_resume(name: str) -> str:
    return (RESUMES / f"{name}.txt").read_text(encoding="utf-8")


EXPECTED = {
    "wednesday_addams": {
        "name": "Wednesday Addams",
        "emails": [],
        "phones": [],
        "links": [],
        "languages": ["JS"],
        "frameworks": ["React.js", "NodeJS"],
        "databases": ["Postgres"],
        "tools": ["Git"],
        "concepts": [],
        "education": [],
        "experience_years": 3,
        "experience": ["3 years of experience developing web applications"],
    },
    "mary_jane_watson": {
        "name": "Mary Jane Watson",
        "emails": [],
        "phones": [],
        "links": [],
        "languages": ["Python"],
        "frameworks": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow"],
        "databases": ["SQL"],
        "tools": ["Git"],
        "concepts": ["predictive models", "data-processing pipelines"],
        "education": [],
        "experience_years": 2,
        "experience": [
            "2 years of experience developing predictive models and data-processing pipelines"
        ],
    },
    "ana_torres": {
        "name": "Ana María Torres",
        "emails": ["ana.torres@mail.example.org"],
        "phones": ["300-123-4567"],
        "links": [],
        "languages": ["Javascript", "TypeScript"],
        "frameworks": ["ReactJS", "Node js"],
        "databases": ["PostgreSQL", "Mongo DB"],
        "tools": ["Git", "GitHub", "Postman"],
        "concepts": ["REST API", "GraphQL"],
        "education": [
            "Tecnólogo en Desarrollo de Software",
            "Instituto Tecnológico de Cali",
        ],
        "experience_years": 3,
        "experience": ["3 years of experience in web development"],
    },
    "carlos_ruiz": {
        "name": "Carlos Ruiz",
        "emails": ["carlos.ruiz@example.com"],
        "phones": ["+1 (415) 555-2671"],
        "links": ["https://github.com/cruiz"],
        "languages": ["Java"],
        "frameworks": ["Spring Boot", "SPRING-BOOT"],
        "databases": ["MySQL", "Redis"],
        "tools": ["Docker", "Kubernetes", "CI/CD", "Jenkins", "GIT"],
        "concepts": ["microservices", "RESTful APIs", "REST APIs"],
        "education": ["B.Sc. in Computer Science", "University of Michigan"],
        "experience_years": 6,
        "experience": [
            "6+ years of professional experience building microservices",
            "Senior Backend Developer at Acme Corp (2019 - Present)",
        ],
    },
    "laura_gomez": {
        "name": "LAURA GÓMEZ RAMÍREZ",
        "emails": ["laura.gomez@gmail.com"],
        "phones": ["315 456 7890"],
        "links": ["linkedin.com/in/laura-gomez-r"],
        "languages": ["python"],
        "frameworks": ["Pandas", "numpy", "sklearn", "PyTorch"],
        "databases": ["Postgres", "mongo db"],
        "tools": ["Docker", "github", "Jupyter"],
        "concepts": ["modelos predictivos"],
        "education": [
            "Ingeniería de Sistemas",
            "Pontificia Universidad Javeriana",
            "Maestría en Analítica",
            "Universidad de los Andes",
        ],
        "experience_years": 4,
        "experience": [
            "4 años de experiencia en analítica y modelos predictivos",
            "Analista de Datos en Bancolombia (2021 - Actualidad)",
        ],
    },
    "sofia_nunez": {
        "name": "Sofía Núñez",
        "emails": ["sofia.nunez@correo.co"],
        "phones": [],
        "links": [],
        "languages": [],
        "frameworks": [],
        "databases": [],
        "tools": [],
        "concepts": [],
        "education": [],
        "experience_years": 5,
        "experience": ["5 years of experience in sales and social media"],
    },
}


@pytest.mark.parametrize("resume", sorted(EXPECTED))
def test_example_resume_matches_expected_extraction(resume):
    assert extract(read_resume(resume)).to_dict() == EXPECTED[resume]


def test_every_example_resume_has_an_expected_result():
    files = {p.stem for p in RESUMES.glob("*.txt")}
    assert files == set(EXPECTED)


# --- invariants that must hold for any resume ---------------------------------


@pytest.mark.parametrize("resume", sorted(EXPECTED))
def test_extracted_skills_appear_in_the_text(resume):
    text = read_resume(resume).casefold()
    result = extract(read_resume(resume))
    for field in SKILL_FIELDS:
        for item in getattr(result, field):
            assert item.casefold() in text, (field, item)


@pytest.mark.parametrize("resume", sorted(EXPECTED))
def test_a_skill_belongs_to_a_single_category(resume):
    result = extract(read_resume(resume))
    seen: dict[str, str] = {}
    for field in SKILL_FIELDS:
        for item in getattr(result, field):
            key = item.casefold()
            assert key not in seen, f"{item!r} is in {seen[key]} and {field}"
            seen[key] = field


@pytest.mark.parametrize("resume", sorted(EXPECTED))
def test_extraction_is_deterministic(resume):
    text = read_resume(resume)
    assert extract(text) == extract(text)


@pytest.mark.parametrize("resume", sorted(EXPECTED))
def test_windows_line_endings_give_the_same_result(resume):
    text = read_resume(resume)
    assert extract(text.replace("\n", "\r\n")) == extract(text)


@pytest.mark.parametrize("resume", sorted(EXPECTED))
def test_lists_have_no_duplicates(resume):
    result = extract(read_resume(resume)).to_dict()
    for field, value in result.items():
        if isinstance(value, list):
            assert len(value) == len({v.casefold() for v in value}), field


def test_skill_order_in_the_resume_does_not_change_what_is_found():
    a = extract("Skills: JS, React.js, NodeJS, Postgres, Git.")
    b = extract("Skills: Git, Postgres, NodeJS, React.js, JS.")
    for field in SKILL_FIELDS:
        assert sorted(getattr(a, field)) == sorted(getattr(b, field)), field


def test_skills_are_found_regardless_of_letter_case():
    lower = extract("skills: javascript, react.js, nodejs, postgres, git")
    upper = extract("SKILLS: JAVASCRIPT, REACT.JS, NODEJS, POSTGRES, GIT")
    for field in ("languages", "frameworks", "databases", "tools"):
        assert [x.casefold() for x in getattr(lower, field)] == [
            x.casefold() for x in getattr(upper, field)
        ], field


def test_extra_spaces_and_blank_lines_do_not_matter():
    clean = extract("Wednesday Addams\nSkills: JS, Git.")
    noisy = extract("\n\n  Wednesday Addams  \n\n\n   Skills:   JS ,\t Git .  \n\n")
    assert noisy.name == clean.name
    assert noisy.languages == clean.languages
    assert noisy.tools == clean.tools


# --- empty and hostile input -----------------------------------------------------


@pytest.mark.parametrize("text", ["", " ", "\n\n", "\t \r\n"])
def test_blank_text_gives_an_empty_result(text):
    result = extract(text)
    assert result.name is None
    assert result.experience_years is None
    for field in SKILL_FIELDS + ("emails", "phones", "links", "education", "experience"):
        assert getattr(result, field) == [], field


def test_prose_without_qualifications_gives_no_skills():
    text = (
        "I like to rest after work and read about the history of the web. "
        "My swift decisions and rust-colored sofa are not skills. "
        "The rest of the team will react to the news."
    )
    result = extract(text)
    assert result.databases == []
    assert result.languages == []
    assert result.concepts == []
    assert result.tools == []


def test_very_long_input_is_processed():
    text = ("Skills: Python, Git, SQL. " * 5000) + "\n"
    result = extract(text)
    assert result.languages == ["Python"]
    assert result.databases == ["SQL"]


def test_pathological_repetition_does_not_hang():
    text = "A" * 20000 + " " + "Universidad " * 2000 + "@" + "a." * 5000
    extract(text)
