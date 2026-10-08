"""Stage 2 - normalization with finite-state transducers (pyformlang)."""

from __future__ import annotations

from src.contracts import ExtractionResult
from src.normalization.transducers import canonical_token as normalize_skill
from src.vocabulary import Profile

__all__ = ["normalize", "normalize_skill", "sort_for_profile"]


def normalize(extracted: ExtractionResult) -> list[str]:
    """Map every raw skill string to its canonical token (e.g. JS -> JAVASCRIPT).

    Input:  ExtractionResult.
    Output: canonical tokens from ``vocabulary.TOKENS``, without duplicates, in
            order of first appearance (languages, frameworks, databases, tools,
            concepts). Strings with no known canonical form are dropped.
    """
    tokens = (normalize_skill(raw) for raw in extracted.raw_skills())
    return list(dict.fromkeys(token for token in tokens if token is not None))


def sort_for_profile(tokens: list[str], profile: Profile) -> list[str]:
    """Order tokens by ``vocabulary.PROFILE_ORDER[profile]``.

    Input:  canonical tokens in any order, and a profile.
    Output: the same tokens in the profile's canonical order.
    """
    raise NotImplementedError("Sorting is implemented in commit 26")
