import re
from pathlib import Path

import pytest

from src.contracts import CandidateProfile
from src.dsl import (
    DSLError,
    DSLSemanticError,
    DSLSyntaxError,
    parse,
    to_dsl_text,
    validate,
)
from src.vocabulary import Profile

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "dsl"
VALID = sorted((EXAMPLES / "valid").glob("*.rl"))
INVALID = sorted((EXAMPLES / "invalid").glob("*.rl"))
SYNTAX_ERRORS = [p for p in INVALID if not p.name.startswith("semantic_")]
SEMANTIC_ERRORS = [p for p in INVALID if p.name.startswith("semantic_")]

ALL_REJECTED = {p: False for p in Profile}
RESULTS = (
    "results { FULL_STACK_DEVELOPER: REJECTED MACHINE_LEARNING_ENGINEER: REJECTED "
    "BACKEND_DEVELOPER: REJECTED DATA_SCIENTIST: REJECTED }"
)


def ids(paths):
    return [p.stem for p in paths]


def sentence(body: str, results: str = RESULTS) -> str:
    return f'candidate "Ana" {{ {body} {results} }}'


def semantic_rule(path: Path) -> str:
    """Rule id (S1..S6) announced in the first line of the example file."""
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    return re.search(r"SEMANTIC (S\d)", first_line).group(1)


# --- the example files -----------------------------------------------------------


def test_example_folders_are_not_empty():
    assert len(VALID) == 4
    assert len(SYNTAX_ERRORS) == 9
    assert len(SEMANTIC_ERRORS) == 8


@pytest.mark.parametrize("path", VALID, ids=ids(VALID))
def test_valid_examples_are_accepted(path):
    assert validate(path.read_text(encoding="utf-8")) is not None


@pytest.mark.parametrize("path", SYNTAX_ERRORS, ids=ids(SYNTAX_ERRORS))
def test_lexical_and_syntactic_errors_are_rejected_by_the_grammar(path):
    with pytest.raises(DSLSyntaxError):
        parse(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", SEMANTIC_ERRORS, ids=ids(SEMANTIC_ERRORS))
def test_semantic_errors_pass_the_grammar_but_fail_validation(path):
    text = path.read_text(encoding="utf-8")
    parse(text)
    with pytest.raises(DSLSemanticError) as error:
        validate(text)
    assert any(semantic_rule(path) in message for message in error.value.errors)


def test_all_errors_share_a_base_class():
    with pytest.raises(DSLError):
        validate("not a candidate")
    with pytest.raises(ValueError):
        validate(sentence("skills { COBOL }"))


# --- the model that validate() returns --------------------------------------------


def test_model_of_the_full_example():
    model = validate((EXAMPLES / "valid" / "laura_gomez.rl").read_text(encoding="utf-8"))
    assert model.name == "Laura Gómez Ramírez"
    kinds = [type(item).__name__ for item in model.contact.items]
    assert kinds == ["Email", "Phone", "Link"]
    assert model.contact.items[0].value == "laura.gomez@gmail.com"
    assert model.experience.years == 4
    assert len(model.experience.jobs) == 2
    assert [s.text for s in model.education.studies][0] == "Ingeniería de Sistemas"
    assert model.skills.items[:3] == ["PYTHON", "PANDAS", "NUMPY"]
    status = {r.profile: r.status for r in model.results.items}
    assert status["MACHINE_LEARNING_ENGINEER"] == "ACCEPTED"
    assert status["FULL_STACK_DEVELOPER"] == "REJECTED"


def test_model_of_the_smallest_example():
    model = validate((EXAMPLES / "valid" / "sofia_nunez.rl").read_text(encoding="utf-8"))
    assert model.skills.items == []
    assert model.experience is None
    assert model.education is None


def test_experience_with_only_jobs_is_valid():
    model = validate(sentence('experience { job: "Intern at Acme" } skills { GIT }'))
    assert model.experience.years is None
    assert [j.text for j in model.experience.jobs] == ["Intern at Acme"]


def test_comments_and_layout_do_not_matter():
    compact = sentence("skills{GIT,PYTHON}")
    spaced = (
        '// comment\ncandidate   "Ana"\n{\n\n  skills {\n    GIT , // tool\n    PYTHON\n  }\n'
        f"  {RESULTS}\n}}"
    )
    assert validate(compact).skills.items == validate(spaced).skills.items == ["GIT", "PYTHON"]


# --- syntax errors carry their position -----------------------------------------------


def test_syntax_error_reports_line_and_column():
    with pytest.raises(DSLSyntaxError) as error:
        parse('candidate "Ana" {\n  skills { GIT, }\n}')
    assert error.value.line == 2
    assert error.value.column is not None


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "candidate",
        'candidate "Ana"',
        'candidate "Ana" {}',
        'candidate "Ana" { skills { } }',
        'candidate "A" { skills { } results { FULL_STACK_DEVELOPER ACCEPTED } }',
        'candidate "A" { skills { GIT } results { FULL_STACK_DEVELOPER: ACCEPTED } } extra',
        'candidate "A" { skills { git } ' + RESULTS + " }",
        'candidate "A" { skills { 9GIT } ' + RESULTS + " }",
        'candidate "A" { skills { GIT__X } ' + RESULTS + " }",
        'candidate "A" { experience { years: -1 } skills { } ' + RESULTS + " }",
        'candidate "A" { experience { job: "x" years: 2 } skills { } ' + RESULTS + " }",
        'candidate "A" { contact { } skills { } ' + RESULTS + " }",
        'candidate "A" { education { } skills { } ' + RESULTS + " }",
        "candidate 'A' { skills { } " + RESULTS + " }",
    ],
)
def test_malformed_sentences_are_rejected(text):
    with pytest.raises(DSLSyntaxError):
        parse(text)


# --- semantic rules -----------------------------------------------------------------


def test_semantic_errors_are_reported_together():
    text = sentence('contact { email: "bad" } experience { years: 99 } skills { COBOL, COBOL }')
    with pytest.raises(DSLSemanticError) as error:
        validate(text)
    joined = " ".join(error.value.errors)
    for rule in ("S1", "S2", "S4", "S5"):
        assert rule in joined


@pytest.mark.parametrize("years", [0, 1, 60])
def test_years_inside_the_range_are_valid(years):
    validate(sentence(f"experience {{ years: {years} }} skills {{ GIT }}"))


@pytest.mark.parametrize("years", [61, 100])
def test_years_outside_the_range_are_invalid(years):
    with pytest.raises(DSLSemanticError):
        validate(sentence(f"experience {{ years: {years} }} skills {{ GIT }}"))


@pytest.mark.parametrize(
    "email", ["ana@icesi.edu.co", "john.doe+cv@mail.example.com"]
)
def test_valid_emails(email):
    validate(sentence(f'contact {{ email: "{email}" }} skills {{ GIT }}'))


@pytest.mark.parametrize("email", ["ana", "ana@", "@icesi.edu.co", "ana@localhost", "a b@c.com"])
def test_invalid_emails(email):
    with pytest.raises(DSLSemanticError):
        validate(sentence(f'contact {{ email: "{email}" }} skills {{ GIT }}'))


@pytest.mark.parametrize("phone", ["+57 300 123 4567", "300-123-4567", "+1 (415) 555-2671"])
def test_valid_phones(phone):
    validate(sentence(f'contact {{ phone: "{phone}" }} skills {{ GIT }}'))


@pytest.mark.parametrize("phone", ["12345", "call me", "2019-2023"])
def test_invalid_phones(phone):
    with pytest.raises(DSLSemanticError):
        validate(sentence(f'contact {{ phone: "{phone}" }} skills {{ GIT }}'))


def test_every_vocabulary_token_is_an_accepted_skill():
    from src.vocabulary import TOKENS

    validate(sentence("skills { " + ", ".join(TOKENS) + " }"))


def test_whitespace_only_name_is_rejected():
    with pytest.raises(DSLSemanticError):
        validate(f'candidate "   " {{ skills {{ }} {RESULTS} }}')


# --- to_dsl_text -------------------------------------------------------------------


def candidate(**changes) -> CandidateProfile:
    base = dict(
        name="Wednesday Addams",
        emails=[],
        phones=[],
        experience_years=3,
        education=[],
        skills=["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
        classifications={
            Profile.FULL_STACK_DEVELOPER: True,
            Profile.MACHINE_LEARNING_ENGINEER: False,
            Profile.BACKEND_DEVELOPER: False,
            Profile.DATA_SCIENTIST: False,
        },
        links=[],
        experience=["3 years of experience developing web applications"],
    )
    base.update(changes)
    return CandidateProfile(**base)


def test_generated_text_is_valid_and_keeps_the_data():
    model = validate(to_dsl_text(candidate()))
    assert model.name == "Wednesday Addams"
    assert model.experience.years == 3
    assert model.skills.items == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    status = {r.profile: r.status for r in model.results.items}
    assert status["FULL_STACK_DEVELOPER"] == "ACCEPTED"
    assert list(status.values()).count("REJECTED") == 3


def test_generated_text_matches_the_hand_written_example():
    generated = to_dsl_text(candidate())
    written = (EXAMPLES / "valid" / "wednesday_addams.rl").read_text(encoding="utf-8")
    body = written.split("\n", 1)[1]  # drop the comment line
    assert generated.split() == body.split()


def test_generated_text_with_every_section():
    c = candidate(
        emails=["wa@example.com", "wednesday@mail.example.com"],
        phones=["+57 300 123 4567"],
        links=["github.com/wa"],
        education=["Ingeniería de Sistemas", "Universidad Icesi"],
        experience=["Backend Developer at Acme (2020 - 2023)", "Intern"],
    )
    model = validate(to_dsl_text(c))
    assert [i.value for i in model.contact.items] == [
        "wa@example.com",
        "wednesday@mail.example.com",
        "+57 300 123 4567",
        "github.com/wa",
    ]
    assert [s.text for s in model.education.studies] == c.education
    assert [j.text for j in model.experience.jobs] == c.experience


def test_empty_sections_are_left_out():
    text = to_dsl_text(candidate(experience_years=None, experience=[], skills=[]))
    assert "contact" not in text
    assert "experience" not in text
    assert "education" not in text
    assert validate(text).skills.items == []


def test_missing_profiles_are_written_as_rejected():
    text = to_dsl_text(candidate(classifications={Profile.FULL_STACK_DEVELOPER: True}))
    status = {r.profile: r.status for r in validate(text).results.items}
    assert status["DATA_SCIENTIST"] == "REJECTED"
    assert len(status) == len(Profile)


def test_quotes_and_line_breaks_in_text_are_made_safe():
    c = candidate(
        name='Ana "Anita"\nTorres',
        experience=['Led the "core" team\n  for 2 years'],
    )
    model = validate(to_dsl_text(c))
    assert model.name == "Ana 'Anita' Torres"
    assert model.experience.jobs[0].text == "Led the 'core' team for 2 years"


def test_text_with_accents_survives():
    model = validate(to_dsl_text(candidate(name="María José Pérez-Núñez")))
    assert model.name == "María José Pérez-Núñez"


def test_a_candidate_without_name_is_rejected():
    with pytest.raises(DSLSemanticError):
        validate(to_dsl_text(candidate(name="")))


def test_unknown_skill_in_generated_text_is_rejected():
    with pytest.raises(DSLSemanticError):
        validate(to_dsl_text(candidate(skills=["JAVASCRIPT", "COBOL"])))


def test_lowercase_skill_in_generated_text_is_a_syntax_error():
    with pytest.raises(DSLSyntaxError):
        validate(to_dsl_text(candidate(skills=["javascript"])))
