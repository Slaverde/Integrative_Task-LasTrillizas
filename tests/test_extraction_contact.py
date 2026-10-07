from src.extraction.contact import (
    extract_emails,
    extract_links,
    extract_name,
    extract_phones,
)


def test_emails_are_found_and_deduplicated():
    text = "Mail: john.doe+cv@mail.example.com, or john.doe+cv@mail.example.com. Alt: a_b@uni.edu.co"
    assert extract_emails(text) == ["john.doe+cv@mail.example.com", "a_b@uni.edu.co"]


def test_email_does_not_swallow_trailing_period():
    assert extract_emails("write to ana@icesi.edu.co.") == ["ana@icesi.edu.co"]


def test_text_without_at_sign_has_no_emails():
    assert extract_emails("Skills: Python, Git") == []


def test_phone_formats():
    text = (
        "+57 300 123 4567 | 300-123-4567 | 3001234567 | +573001234567 | "
        "+1 (415) 555-2671 | (601) 555 1234"
    )
    assert extract_phones(text) == [
        "+57 300 123 4567",
        "300-123-4567",
        "3001234567",
        "+573001234567",
        "+1 (415) 555-2671",
        "(601) 555 1234",
    ]


def test_years_and_experience_are_not_phones():
    text = "2019-2023 | 3 years of experience | 12345 | 12345678901234"
    assert extract_phones(text) == []


def test_links_strip_trailing_punctuation():
    text = (
        "Portfolio (https://ana.dev/projects), linkedin.com/in/ana-perez; "
        "github.com/anaperez. www.ana.dev"
    )
    assert extract_links(text) == [
        "https://ana.dev/projects",
        "linkedin.com/in/ana-perez",
        "github.com/anaperez",
        "www.ana.dev",
    ]


def test_email_domain_is_not_a_link():
    assert extract_links("ana@github.com") == []


def test_name_from_first_line():
    assert extract_name("Wednesday Addams\n3 years of experience") == "Wednesday Addams"


def test_name_with_accents_and_uppercase():
    assert extract_name("MARÍA JOSÉ Pérez-Núñez\nPython") == "MARÍA JOSÉ Pérez-Núñez"


def test_name_from_label_wins():
    text = "Curriculum Vitae\nTechnical Skills: Python\nNombre: Juan Pérez\n"
    assert extract_name(text) == "Juan Pérez"


def test_heading_is_not_a_name():
    assert extract_name("Curriculum Vitae\nAna Pérez\nPython") == "Ana Pérez"


def test_no_name_when_first_lines_are_not_names():
    assert extract_name("3 years of experience\nskills: python") is None
