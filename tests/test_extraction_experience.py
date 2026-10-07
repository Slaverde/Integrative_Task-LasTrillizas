from src.extraction.experience import extract_experience, extract_experience_years


def test_years_from_digits():
    assert extract_experience_years("3 years of experience developing web applications.") == 3


def test_years_variants():
    assert extract_experience_years("2+ years of professional experience") == 2
    assert extract_experience_years("5 yrs experience in Java") == 5
    assert extract_experience_years("4 años de experiencia") == 4
    assert extract_experience_years("Five years of relevant experience") == 5


def test_largest_years_wins():
    text = "5 years of experience in backend, 2 years of experience in ML"
    assert extract_experience_years(text) == 5


def test_no_years_when_not_experience():
    assert extract_experience_years("The company was founded 10 years ago") is None
    assert extract_experience_years("Python, Git") is None


def test_statement_ends_at_the_period():
    text = "3 years of experience developing web applications. Technical Skills: JS."
    assert extract_experience(text) == ["3 years of experience developing web applications"]


def test_statement_without_description():
    assert extract_experience("Over 7 years of experience") == ["7 years of experience"]


def test_job_entries_with_company_and_dates():
    text = (
        "Senior Backend Developer at Acme Corp (2020 - 2023)\n"
        "Data Analyst en Bancolombia, 2018-2020\n"
        "Software Engineer Intern - Present"
    )
    assert extract_experience(text) == [
        "Senior Backend Developer at Acme Corp (2020 - 2023)",
        "Data Analyst en Bancolombia, 2018-2020",
        "Software Engineer Intern",
    ]


def test_statement_and_jobs_keep_order_of_appearance():
    text = "Backend Developer at Acme (2021 - 2024)\n3 years of experience building APIs."
    assert extract_experience(text) == [
        "Backend Developer at Acme (2021 - 2024)",
        "3 years of experience building APIs",
    ]


def test_company_name_does_not_swallow_the_period():
    assert extract_experience("Machine Learning Engineer at Globant.") == [
        "Machine Learning Engineer at Globant"
    ]


def test_no_experience():
    assert extract_experience("Skills: Python") == []
