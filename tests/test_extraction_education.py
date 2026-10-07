from src.extraction.education import extract_education


def test_english_degree_and_institution():
    text = "Bachelor of Science in Computer Science from Stanford University, 2022"
    assert extract_education(text) == [
        "Bachelor of Science in Computer Science",
        "Stanford University",
    ]


def test_spanish_degree_and_institution():
    text = "Ingeniería de Sistemas y Computación, Universidad Icesi (2019 - 2024)"
    assert extract_education(text) == [
        "Ingeniería de Sistemas y Computación",
        "Universidad Icesi",
    ]


def test_abbreviated_degrees():
    assert extract_education("B.Sc. in Physics; M.Sc. in Data Science.") == [
        "B.Sc. in Physics",
        "M.Sc. in Data Science",
    ]


def test_institution_with_of():
    assert extract_education("University of Michigan\nMassachusetts Institute of Technology") == [
        "University of Michigan",
        "Massachusetts Institute of Technology",
    ]


def test_pontificia_universidad():
    assert extract_education("Pontificia Universidad Javeriana") == [
        "Pontificia Universidad Javeriana"
    ]


def test_match_does_not_cross_lines():
    text = "Universidad Icesi\nPython, Git"
    assert extract_education(text) == ["Universidad Icesi"]


def test_scrum_master_is_not_a_degree():
    assert extract_education("Certified Scrum Master") == []


def test_duplicates_are_removed_and_order_is_kept():
    text = "Universidad Icesi. Maestría en Analítica. Universidad Icesi."
    assert extract_education(text) == ["Universidad Icesi", "Maestría en Analítica"]


def test_resume_without_education():
    assert extract_education("Technical Skills: JS, React.js, Git.") == []
