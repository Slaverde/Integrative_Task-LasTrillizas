"""Stage 2 - normalization with finite-state transducers (pyformlang)."""

from __future__ import annotations

from src.contracts import ExtractionResult
from src.normalization.sorting import sort_by_vocabulary, sort_for_profile
from src.normalization.transducers import canonical_token as normalize_skill

__all__ = ["normalize", "normalize_skill", "sort_by_vocabulary", "sort_for_profile"]


def normalize(extracted: ExtractionResult) -> list[str]:
    """Map every raw skill string to its canonical token (e.g. JS -> JAVASCRIPT).

    Input:  ExtractionResult.
    Output: canonical tokens from ``vocabulary.TOKENS``, without duplicates, in
            order of first appearance (languages, frameworks, databases, tools,
            concepts). Strings with no known canonical form are dropped.
    """
    tokens = (normalize_skill(raw) for raw in extracted.raw_skills())
    return list(dict.fromkeys(token for token in tokens if token is not None))
