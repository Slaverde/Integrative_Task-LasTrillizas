"""Properties that must hold for any input of stage 2."""

import itertools
import random
import time

import pytest

from src.contracts import ExtractionResult
from src.extraction import extract
from src.normalization import normalize, normalize_skill, sort_for_profile
from src.normalization.variants import GROUPS, SEPARATORS
from src.vocabulary import TOKENS, Profile

SPELLINGS = [
    (token, spelling)
    for group in GROUPS.values()
    for token, spellings in group.items()
    for spelling in spellings
]


def test_a_token_is_a_spelling_of_itself():
    # normalizing the output of normalize changes nothing (idempotence)
    for token in TOKENS:
        assert normalize_skill(token) == token, token


@pytest.mark.parametrize("token, spelling", SPELLINGS)
def test_letter_case_does_not_matter(token, spelling):
    for variant in (spelling.lower(), spelling.upper(), spelling.swapcase()):
        assert normalize_skill(variant) == token, variant


@pytest.mark.parametrize("token, spelling", SPELLINGS)
def test_separators_do_not_matter(token, spelling):
    for separator in SEPARATORS:
        spread = separator.join(spelling)  # a separator between every character
        assert normalize_skill(spread) == token, repr(spread)
        assert normalize_skill(separator + spelling + separator) == token


def test_accents_do_not_matter():
    assert normalize_skill("aprendizaje automatico") == "MACHINE_LEARNING"
    assert normalize_skill("aprendizaje automático") == "MACHINE_LEARNING"
    assert normalize_skill("APRENDIZAJE AUTOMÁTICO") == "MACHINE_LEARNING"
    assert normalize_skill("aprendizaje de maquina") == "MACHINE_LEARNING"


@pytest.mark.parametrize("token, spelling", SPELLINGS)
def test_no_proper_prefix_of_a_spelling_is_accepted_by_mistake(token, spelling):
    # "Postgre", "Scikit", "Machine learning m", ... are not spellings, unless
    # they happen to be another spelling of the dictionary
    known = {s.replace(" ", "").upper() for _, s in SPELLINGS}
    key = spelling.replace(" ", "").upper()
    for end in range(1, len(key)):
        prefix = key[:end]
        if prefix not in known:
            assert normalize_skill(prefix) is None, prefix


@pytest.mark.parametrize("token, spelling", SPELLINGS)
def test_a_spelling_with_extra_letters_is_not_accepted(token, spelling):
    assert normalize_skill(spelling + "X") is None
    assert normalize_skill("X" + spelling) is None


def test_the_order_of_the_resume_does_not_change_the_sorted_result():
    skills = ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    reference: dict[Profile, list[str]] = {}
    for permutation in itertools.permutations(skills):  # 120 orders
        text = "Wednesday Addams\nTechnical Skills: " + ", ".join(permutation) + ".\n"
        tokens = normalize(extract(text))
        for profile in Profile:
            result = sort_for_profile(tokens, profile)
            assert result == reference.setdefault(profile, result), permutation
    assert reference[Profile.FULL_STACK_DEVELOPER] == [
        "JAVASCRIPT",
        "REACT",
        "NODE_JS",
        "POSTGRESQL",
        "GIT",
    ]


def test_the_same_tokens_in_any_field_give_the_same_result():
    # fields are only a hint of stage 1: a string is normalized by what it says
    as_framework = ExtractionResult(frameworks=["JS", "Git", "Postgres"])
    as_language = ExtractionResult(languages=["JS", "Git", "Postgres"])
    assert normalize(as_framework) == normalize(as_language)
    assert normalize(as_framework) == ["JAVASCRIPT", "GIT", "POSTGRESQL"]


def test_normalize_output_is_made_of_known_tokens_without_duplicates():
    rng = random.Random(2026)
    pool = [spelling for _, spelling in SPELLINGS] + ["Rust", "C#", "???", ""]
    for _ in range(200):
        extracted = ExtractionResult(
            languages=rng.sample(pool, 4),
            frameworks=rng.sample(pool, 4),
            databases=rng.sample(pool, 4),
            tools=rng.sample(pool, 4),
            concepts=rng.sample(pool, 4),
        )
        tokens = normalize(extracted)
        assert len(tokens) == len(set(tokens))
        assert set(tokens) <= set(TOKENS)
        assert len(tokens) <= len(extracted.raw_skills())


def test_random_text_never_raises():
    rng = random.Random(11)
    alphabet = "abcXYZ019 .-_+#/@áÑ\t\n🙂()[]{}'\"\\"
    for _ in range(3000):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 40)))
        token = normalize_skill(text)
        assert token is None or token in TOKENS


def test_a_very_long_string_is_dropped_quickly():
    started = time.perf_counter()
    assert normalize_skill("A" * 20_000) is None
    assert normalize_skill("JS" + " " * 20_000) is None
    assert time.perf_counter() - started < 1.0


def test_non_string_input_is_a_type_error_not_a_wrong_answer():
    with pytest.raises(TypeError):
        normalize_skill(None)  # type: ignore[arg-type]
