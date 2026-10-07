import json

from src.extraction import extract
from src.extraction.skills import extract_concepts, extract_tools
from src.extraction.storage import load_json, save_json


def test_tool_variants():
    text = "Git, GitHub, GitLab, Docker, Kubernetes, Jenkins, Jira, Jupyter Notebook, Linux, AWS, CI/CD"
    assert extract_tools(text) == [
        "Git",
        "GitHub",
        "GitLab",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "Jira",
        "Jupyter Notebook",
        "Linux",
        "AWS",
        "CI/CD",
    ]


def test_git_is_not_found_inside_github_or_digit():
    assert extract_tools("GitHub") == ["GitHub"]
    assert extract_tools("digital agile") == []


def test_concepts_rest_api_variants():
    text = "REST APIs, RESTful API, Restful web services, GraphQL, microservices"
    assert extract_concepts(text) == [
        "REST APIs",
        "RESTful API",
        "Restful web services",
        "GraphQL",
        "microservices",
    ]


def test_tool_inside_a_link_or_email_is_not_a_skill():
    assert extract_tools("github.com/ana, ana@gitlab.com, https://github.com/ana") == []


def test_plain_rest_is_not_a_concept():
    assert extract_concepts("take a rest during the rest of the day") == []


def test_concepts_machine_learning_variants():
    text = "Machine-learning model development, machine learning, deep learning, predictive models, ML"
    assert extract_concepts(text) == [
        "Machine-learning model development",
        "machine learning",
        "deep learning",
        "predictive models",
        "ML",
    ]


def test_ml_abbreviation_is_case_sensitive():
    assert extract_concepts("html xml ml") == []


def test_full_resume_fills_every_field():
    text = (
        "María José Pérez\n"
        "maria@icesi.edu.co | +57 300 123 4567 | github.com/mjperez\n"
        "Backend Developer at Acme Corp (2021 - 2024)\n"
        "4 years of experience building REST APIs.\n"
        "Education: Ingeniería de Sistemas, Universidad Icesi\n"
        "Skills: Java, Spring Boot, MySQL, Docker, Git."
    )
    result = extract(text)
    assert result.name == "María José Pérez"
    assert result.emails == ["maria@icesi.edu.co"]
    assert result.phones == ["+57 300 123 4567"]
    assert result.links == ["github.com/mjperez"]
    assert result.languages == ["Java"]
    assert result.frameworks == ["Spring Boot"]
    assert result.databases == ["MySQL"]
    assert result.tools == ["Docker", "Git"]
    assert result.concepts == ["REST APIs"]
    assert result.experience_years == 4
    assert result.experience[0] == "Backend Developer at Acme Corp (2021 - 2024)"
    assert result.education == ["Ingeniería de Sistemas", "Universidad Icesi"]


def test_json_round_trip(tmp_path):
    result = extract("Wednesday Addams\n3 years of experience developing web applications.\nSkills: JS, Git.")
    path = save_json(result, tmp_path / "out" / "resume.json")
    assert json.loads(path.read_text(encoding="utf-8"))["languages"] == ["JS"]
    assert load_json(path) == result
