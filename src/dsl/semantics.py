"""Semantic rules S1 to S6 of the candidate profile language.

They need data that the grammar does not have (the canonical vocabulary, the
list of profiles, the contact patterns of stage 1), so they run on the model
produced by textX.
"""

from __future__ import annotations

from textx import get_location

from src.dsl.errors import DSLSemanticError
from src.extraction import patterns
from src.vocabulary import TOKENS, Profile

MAX_YEARS = 60


def _where(obj) -> str:
    return f"line {get_location(obj)['line']}"


def check(model) -> None:
    """Raise DSLSemanticError with every violated rule, or return silently."""
    errors: list[str] = []

    # S6: the name is not empty
    if not model.name.strip():
        errors.append(f"{_where(model)}: S6 the candidate name is empty")

    # S5: contact formats
    if model.contact:
        for item in model.contact.items:
            kind = type(item).__name__
            if kind == "Email" and not patterns.EMAIL.fullmatch(item.value):
                errors.append(f"{_where(item)}: S5 invalid email {item.value!r}")
            if kind == "Phone" and not patterns.PHONE.fullmatch(item.value):
                errors.append(f"{_where(item)}: S5 invalid phone {item.value!r}")

    # S4: years of experience in range
    if model.experience and model.experience.years is not None:
        if not 0 <= model.experience.years <= MAX_YEARS:
            errors.append(
                f"{_where(model.experience)}: S4 years must be between 0 and "
                f"{MAX_YEARS}, got {model.experience.years}"
            )

    # S1 and S2: skills belong to the vocabulary and are not repeated
    seen_skills: set[str] = set()
    for skill in model.skills.items:
        if skill not in TOKENS:
            errors.append(f"{_where(model.skills)}: S1 unknown skill {skill}")
        if skill in seen_skills:
            errors.append(f"{_where(model.skills)}: S2 repeated skill {skill}")
        seen_skills.add(skill)

    # S3: every profile appears exactly once
    known = {p.value for p in Profile}
    seen_profiles: set[str] = set()
    for result in model.results.items:
        if result.profile not in known:
            errors.append(f"{_where(result)}: S3 unknown profile {result.profile}")
        elif result.profile in seen_profiles:
            errors.append(f"{_where(result)}: S3 repeated profile {result.profile}")
        seen_profiles.add(result.profile)
    missing = sorted(known - seen_profiles)
    if missing:
        errors.append(
            f"{_where(model.results)}: S3 missing profiles {', '.join(missing)}"
        )

    if errors:
        raise DSLSemanticError(errors)
