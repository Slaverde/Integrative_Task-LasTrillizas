"""Stage 3 - qualification pattern recognition with finite automata (pyformlang).

Four independent DFAs, one per profile (see ``src/classification/automata.py``
and docs/classification-design.md). Each one reads the *category* of every
canonical token (``vocabulary.TOKENS``), not the token itself, and accepts
iff every category its profile requires appeared at least once.
"""

from __future__ import annotations

from collections.abc import Callable

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from src.classification.automata import (
    build_backend_developer,
    build_data_scientist,
    build_full_stack_developer,
    build_machine_learning_engineer,
)
from src.normalization import sort_for_profile
from src.vocabulary import TOKENS, Profile

_BUILDERS: dict[Profile, Callable[[], DeterministicFiniteAutomaton]] = {
    Profile.FULL_STACK_DEVELOPER: build_full_stack_developer,
    Profile.MACHINE_LEARNING_ENGINEER: build_machine_learning_engineer,
    Profile.BACKEND_DEVELOPER: build_backend_developer,
    Profile.DATA_SCIENTIST: build_data_scientist,
}

_AUTOMATA: dict[Profile, DeterministicFiniteAutomaton] = {
    profile: builder() for profile, builder in _BUILDERS.items()
}
"""Built once at import time: a pyformlang automaton does not change after
construction, and the four of them are reused for every résumé."""


def _category_sequence(tokens: list[str]) -> list[str]:
    """Canonical tokens -> their category names, in the same order.

    A token stage 2 could not have produced (missing from ``TOKENS``) is
    skipped rather than raising, so a stray value never crashes stage 3;
    in practice every token here already comes from ``normalize``.
    """
    return [TOKENS[token].value for token in tokens if token in TOKENS]


def classify(tokens: list[str], profile: Profile) -> bool:
    """Run the profile's automaton over the sorted canonical tokens.

    Input:  tokens already sorted with ``sort_for_profile`` for this profile.
    Output: True (ACCEPTED) or False (REJECTED).
    """
    return _AUTOMATA[profile].accepts(_category_sequence(tokens))


def classify_all(tokens: list[str]) -> dict[Profile, bool]:
    """Classify the same tokens against all four profiles.

    Input:  canonical tokens in any order (sorted internally per profile).
    Output: {profile: accepted?} for every profile in ``Profile``.
    """
    return {
        profile: classify(sort_for_profile(tokens, profile), profile)
        for profile in Profile
    }
