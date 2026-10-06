"""Stage 2 - normalization with finite-state transducers (pyformlang)."""

from __future__ import annotations

from src.contracts import ExtractionResult
from src.vocabulary import Profile


def normalize(extracted: ExtractionResult) -> list[str]:
    """Map every raw skill string to its canonical token (e.g. JS -> JAVASCRIPT).

    Input:  ExtractionResult.
    Output: canonical tokens from ``vocabulary.TOKENS``, without duplicates.
            Strings with no known canonical form are dropped.
    """
    raise NotImplementedError("Stage 2 is implemented in commits 21-27")


def sort_for_profile(tokens: list[str], profile: Profile) -> list[str]:
    """Order tokens by ``vocabulary.PROFILE_ORDER[profile]``.

    Input:  canonical tokens in any order, and a profile.
    Output: the same tokens in the profile's canonical order.
    """
    raise NotImplementedError("Sorting is implemented in commit 26")
