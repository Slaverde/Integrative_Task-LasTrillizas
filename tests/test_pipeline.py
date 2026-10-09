from pathlib import Path

import pytest

from src.contracts import CandidateProfile
from src.main import UNKNOWN_NAME, Analysis, analyze, complete, run_pipeline, run_stages
from src.normalization import sort_for_profile
from src.vocabulary import Profile

RESUMES = Path(__file__).resolve().parents[1] / "examples" / "resumes"
WEDNESDAY = (RESUMES / "wednesday_addams.txt").read_text(encoding="utf-8")


def read(name: str) -> str:
    return (RESUMES / f"{name}.txt").read_text(encoding="utf-8")


# --- stages 1 and 2 ----------------------------------------------------------


def test_analyze_gives_the_example_of_the_assignment():
    analysis = analyze(WEDNESDAY)
    assert analysis.extracted.name == "Wednesday Addams"
    assert analysis.tokens == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert analysis.sorted_tokens[Profile.FULL_STACK_DEVELOPER] == [
        "JAVASCRIPT",
        "REACT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
    ]


def test_analyze_sorts_for_the_four_profiles_with_the_same_function():
    analysis = analyze(read("mary_jane_watson"))
    assert set(analysis.sorted_tokens) == set(Profile)
    for profile, sequence in analysis.sorted_tokens.items():
        assert sequence == sort_for_profile(analysis.tokens, profile)
        assert sorted(sequence) == sorted(analysis.tokens)


def test_the_skill_trace_shows_what_was_dropped():
    analysis = analyze(read("carlos_ruiz"))
    dropped = [raw for raw, token in analysis.skill_trace if token is None]
    assert dropped == ["CI/CD", "Jenkins", "microservices"]
    assert ("SPRING-BOOT", "SPRING_BOOT") in analysis.skill_trace
    assert ("Spring Boot", "SPRING_BOOT") in analysis.skill_trace


def test_analyze_does_not_need_stage_3():
    # stages 1 and 2 never call the classifier
    analysis = analyze(WEDNESDAY)
    assert isinstance(analysis, Analysis)


def test_a_resume_with_no_skills_gives_empty_sequences():
    analysis = analyze(read("sofia_nunez"))
    assert analysis.tokens == []
    assert all(sequence == [] for sequence in analysis.sorted_tokens.values())


# --- candidate without a name (decision D7) ----------------------------------

NO_NAME = "3 years of experience in web development.\nSkills: Python, Git.\n"


def test_a_resume_without_a_name_gets_a_default_name():
    analysis = analyze(NO_NAME)
    assert analysis.extracted.name is None
    assert analysis.name_detected is False
    assert analysis.name == UNKNOWN_NAME


def test_a_detected_name_is_used_as_it_is():
    analysis = analyze(WEDNESDAY)
    assert analysis.name_detected is True
    assert analysis.name == "Wednesday Addams"


def test_the_default_name_passes_the_dsl_validation(stub_classifier):
    result = run_stages(NO_NAME, stub_classifier)
    assert result.candidate.name == UNKNOWN_NAME
    assert f'candidate "{UNKNOWN_NAME}"' in result.dsl_text
    assert UNKNOWN_NAME in result.html  # the rule S6 (non-empty name) is met


# --- stages 3 and 4 with a stand-in classifier ------------------------------


def test_run_pipeline_returns_the_html_of_the_candidate(stub_classifier):
    html = run_pipeline(WEDNESDAY, stub_classifier)
    assert html.startswith("<!DOCTYPE html>")
    assert "Wednesday Addams" in html
    assert "NODE_JS" in html
    assert "Accepted profiles: Full Stack Developer" in html


def test_the_classifier_receives_the_canonical_tokens(stub_classifier):
    run_pipeline(WEDNESDAY, stub_classifier)
    assert stub_classifier.calls == [
        ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    ]


def test_run_stages_keeps_every_intermediate_result(stub_classifier):
    result = run_stages(WEDNESDAY, stub_classifier)
    assert result.analysis.tokens == result.candidate.skills
    assert result.classifications[Profile.FULL_STACK_DEVELOPER] is True
    assert result.classifications[Profile.MACHINE_LEARNING_ENGINEER] is False
    assert isinstance(result.candidate, CandidateProfile)
    assert result.dsl_text.startswith('candidate "Wednesday Addams" {')
    assert result.html.endswith("</html>\n")


def test_the_skills_of_the_dsl_follow_the_vocabulary_order(stub_classifier):
    result = run_stages("Ana Ruiz\nSkills: Git, Postgres, NodeJS, JS, Docker.", stub_classifier)
    assert result.candidate.skills == [
        "JAVASCRIPT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
        "DOCKER",
    ]
    assert "skills { JAVASCRIPT, NODE_JS, POSTGRESQL, GIT, DOCKER }" in result.dsl_text


def test_complete_works_on_an_analysis_already_made(stub_classifier):
    analysis = analyze(WEDNESDAY)
    result = complete(analysis, stub_classifier)
    assert result.analysis is analysis


@pytest.mark.parametrize(
    "name",
    [
        "wednesday_addams",
        "mary_jane_watson",
        "ana_torres",
        "carlos_ruiz",
        "laura_gomez",
        "sofia_nunez",
    ],
)
def test_every_example_resume_gives_a_valid_candidate_profile(name, stub_classifier):
    # the DSL validation (rules S1 to S6) accepts what stages 1 and 2 produce
    result = run_stages(read(name), stub_classifier)
    assert "<h1>" in result.html
    assert all(token in result.dsl_text for token in result.analysis.tokens)


def test_the_pipeline_uses_classify_all_by_default(monkeypatch):
    calls = []

    def fake(tokens):
        calls.append(tokens)
        return {profile: False for profile in Profile}

    monkeypatch.setattr("src.main.classify_all", fake)
    html = run_pipeline(WEDNESDAY)
    assert len(calls) == 1
    assert "No qualification pattern was satisfied." in html


def test_a_missing_profile_in_the_classification_is_written_as_rejected():
    only_full_stack = {Profile.FULL_STACK_DEVELOPER: True}
    result = run_stages(WEDNESDAY, lambda tokens: only_full_stack)
    assert "MACHINE_LEARNING_ENGINEER: REJECTED" in result.dsl_text


def test_while_stage_3_is_missing_the_error_is_clear(stage_3_ready):
    if stage_3_ready:
        pytest.skip("stage 3 is implemented")
    with pytest.raises(NotImplementedError):
        run_pipeline(WEDNESDAY)
    # stages 1 and 2 still work
    assert analyze(WEDNESDAY).tokens
