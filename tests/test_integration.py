"""All stages together, on the example resumes and the four profiles."""

import itertools
import random
from pathlib import Path

import pytest

import src.main as main
from src.dsl import validate
from src.main import analyze, run_stages
from src.vocabulary import PROFILE_ORDER, TOKENS, Profile

RESUMES = Path(__file__).resolve().parents[1] / "examples" / "resumes"
NAMES = sorted(p.stem for p in RESUMES.glob("*.txt"))

FS = Profile.FULL_STACK_DEVELOPER
ML = Profile.MACHINE_LEARNING_ENGINEER


def read(name: str) -> str:
    return (RESUMES / f"{name}.txt").read_text(encoding="utf-8")


# --- stages 1 and 2: expected sequences per profile -------------------------

EXPECTED = {
    "wednesday_addams": {
        FS: ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
        ML: ["JAVASCRIPT", "POSTGRESQL", "GIT", "REACT", "NODE_JS"],
    },
    "mary_jane_watson": {
        FS: ["PYTHON", "SQL", "GIT", "MACHINE_LEARNING", "PANDAS", "NUMPY",
             "SCIKIT_LEARN", "TENSORFLOW"],
        ML: ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW",
             "MACHINE_LEARNING", "SQL", "GIT"],
    },
}


# Only the two profiles given by the assignment have exact sequences here. The
# two team profiles are provisional, so they are covered by the properties
# below (which read PROFILE_ORDER) and not by hard-coded lists.
@pytest.mark.parametrize("name", list(EXPECTED))
@pytest.mark.parametrize("profile", [FS, ML])
def test_sorted_sequences_of_the_assignment_examples(name, profile):
    assert analyze(read(name)).sorted_tokens[profile] == EXPECTED[name][profile]


def test_full_stack_sequence_of_a_resume_with_many_spellings():
    assert analyze(read("ana_torres")).sorted_tokens[FS] == [
        "JAVASCRIPT", "TYPESCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "MONGODB",
        "GIT", "REST_API", "GRAPHQL",
    ]


@pytest.mark.parametrize("name", NAMES)
def test_every_profile_sequence_is_a_reordering_of_the_same_tokens(name):
    analysis = analyze(read(name))
    for profile, sequence in analysis.sorted_tokens.items():
        assert sorted(sequence) == sorted(analysis.tokens)
        assert len(sequence) == len(set(sequence))
        order = PROFILE_ORDER[profile]
        ranks = [
            order.index(TOKENS[t]) if TOKENS[t] in order else len(order)
            for t in sequence
        ]
        assert ranks == sorted(ranks)


def test_the_four_profiles_go_through_the_same_sorting_function(monkeypatch):
    calls = []
    real = main.sort_for_profile

    def spy(tokens, profile):
        calls.append((spy, profile))
        return real(tokens, profile)

    monkeypatch.setattr(main, "sort_for_profile", spy)
    analyze(read("wednesday_addams"))
    assert {profile for _, profile in calls} == set(Profile)
    assert len({function for function, _ in calls}) == 1


@pytest.mark.parametrize("name", NAMES)
def test_the_order_of_the_skills_does_not_change_any_profile_sequence(name):
    # shuffle the comma-separated skills of the line that lists them
    text = read(name)
    lines = text.splitlines()
    index = next(
        (i for i, line in enumerate(lines) if line.count(",") >= 3 and ":" in line), None
    )
    if index is None:
        pytest.skip("this resume has no line with a list of skills")
    head, _, tail = lines[index].partition(":")
    items = [item.strip() for item in tail.split(",")]
    reference = analyze(text).sorted_tokens
    rng = random.Random(5)
    for _ in range(15):
        rng.shuffle(items)
        shuffled = lines[:index] + [f"{head}: {', '.join(items)}"] + lines[index + 1 :]
        assert analyze("\n".join(shuffled)).sorted_tokens == reference


def test_all_permutations_of_the_assignment_example_give_one_sequence_per_profile():
    skills = ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    seen = {profile: set() for profile in Profile}
    for permutation in itertools.permutations(skills):
        text = "Wednesday Addams\nTechnical Skills: " + ", ".join(permutation) + ".\n"
        for profile, sequence in analyze(text).sorted_tokens.items():
            seen[profile].add(tuple(sequence))
    assert all(len(sequences) == 1 for sequences in seen.values())


# --- stages 1 to 4 with a stand-in for stage 3 -----------------------------


@pytest.mark.parametrize("name", NAMES)
def test_every_example_resume_goes_through_the_pipeline(name, stub_classifier):
    result = run_stages(read(name), stub_classifier)
    model = validate(result.dsl_text)  # the DSL text is valid on its own
    assert list(model.skills.items) == result.candidate.skills
    assert {r.profile for r in model.results.items} == {p.value for p in Profile}
    assert result.html.startswith("<!DOCTYPE html>")


def test_the_dsl_lists_the_canonical_tokens_of_the_candidate(stub_classifier):
    result = run_stages(read("laura_gomez"), stub_classifier)
    assert "skills { PYTHON, POSTGRESQL, MONGODB, GIT" in result.dsl_text
    assert "GIT" in result.candidate.skills  # from "github" (decision D3)
    assert "MACHINE_LEARNING" in result.candidate.skills  # from "modelos predictivos"


def test_hand_written_variants_end_in_the_same_html(stub_classifier):
    first = run_stages("Ana Ruiz\nSkills: JS, React.js, NodeJS, Postgres, Git.", stub_classifier)
    second = run_stages(
        "Ana Ruiz\nSkills: Javascript, ReactJS, Node js, PostgreSQL, github.", stub_classifier
    )
    assert first.html == second.html


# --- stages 1 to 4 with the real stage 3 (active once it exists) ------------


def accepted(name: str) -> set[Profile]:
    return set(run_stages(read(name)).candidate.accepted_profiles())


def test_the_assignment_examples_with_the_real_classifier(stage_3_ready):
    if not stage_3_ready:
        pytest.skip("stage 3 is not implemented yet")
    assert FS in accepted("wednesday_addams")
    assert ML in accepted("mary_jane_watson")
    assert FS in accepted("ana_torres")
    assert accepted("sofia_nunez") == set()


def test_the_same_tokens_in_any_order_give_the_same_classification(stage_3_ready):
    if not stage_3_ready:
        pytest.skip("stage 3 is not implemented yet")
    from src.classification import classify_all

    tokens = analyze(read("wednesday_addams")).tokens
    expected = classify_all(tokens)
    for permutation in itertools.permutations(tokens):
        assert classify_all(list(permutation)) == expected
