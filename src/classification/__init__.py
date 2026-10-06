"""Stage 3 - qualification pattern recognition with finite automata (pyformlang)."""

from __future__ import annotations

from src.vocabulary import Profile


def classify(tokens: list[str], profile: Profile) -> bool:
    """Run the profile's automaton over the sorted canonical tokens.

    Input:  tokens already sorted with ``sort_for_profile`` for this profile.
    Output: True (ACCEPTED) or False (REJECTED).
    """
    raise NotImplementedError("Stage 3 is implemented in commits 13-16")


def classify_all(tokens: list[str]) -> dict[Profile, bool]:
    """Classify the same tokens against all four profiles.

    Input:  canonical tokens in any order (sorted internally per profile).
    Output: {profile: accepted?} for every profile in ``Profile``.
    """
    raise NotImplementedError("Stage 3 is implemented in commits 13-16")
