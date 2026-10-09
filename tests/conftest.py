import pytest

from src.classification import classify_all
from src.vocabulary import Profile


@pytest.fixture
def stub_classifier():
    """A classifier that accepts only Full Stack, and remembers what it received.

    Stage 3 may not be implemented yet; this stands in for ``classify_all`` so
    the pipeline and the UI can be tested on their own.
    """

    def classifier(tokens):
        classifier.calls.append(list(tokens))
        return {profile: profile is Profile.FULL_STACK_DEVELOPER for profile in Profile}

    classifier.calls = []
    return classifier


@pytest.fixture(scope="session")
def stage_3_ready() -> bool:
    """True once ``classify_all`` is implemented (tests that need it skip before)."""
    try:
        classify_all([])
    except NotImplementedError:
        return False
    return True
