import pytest

from src.classification import classify, classify_all
from src.extraction import extract
from src.normalization import normalize, sort_for_profile
from src.vocabulary import Profile


def _tokens(path: str) -> list[str]:
    text = open(path, encoding="utf-8").read()
    return normalize(extract(text))


def test_classify_matches_classify_all_for_every_profile():
    tokens = _tokens("examples/resumes/wednesday_addams.txt")
    all_results = classify_all(tokens)
    for profile in Profile:
        sorted_tokens = sort_for_profile(tokens, profile)
        assert classify(sorted_tokens, profile) == all_results[profile]


def test_wednesday_addams_satisfies_full_stack_developer():
    # Wednesday Addams: JS, React.js, NodeJS, Postgres, Git (assignment example)
    tokens = _tokens("examples/resumes/wednesday_addams.txt")
    result = classify_all(tokens)
    assert result[Profile.FULL_STACK_DEVELOPER] is True


def test_mary_jane_watson_satisfies_machine_learning_engineer():
    # Mary Jane Watson: Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git
    tokens = _tokens("examples/resumes/mary_jane_watson.txt")
    result = classify_all(tokens)
    assert result[Profile.MACHINE_LEARNING_ENGINEER] is True


def test_classify_all_returns_every_profile():
    tokens = _tokens("examples/resumes/wednesday_addams.txt")
    result = classify_all(tokens)
    assert set(result.keys()) == set(Profile)


def test_no_tokens_satisfies_no_profile():
    result = classify_all([])
    assert all(accepted is False for accepted in result.values())


def test_classify_all_rejects_a_token_outside_the_vocabulary():
    # classify_all sorts with sort_for_profile (stage 2), which already
    # enforces that every token comes from vocabulary.TOKENS; a stray value
    # here means a bug upstream, not something stage 3 should mask.
    with pytest.raises(ValueError):
        classify_all(["NOT_A_REAL_TOKEN"])
