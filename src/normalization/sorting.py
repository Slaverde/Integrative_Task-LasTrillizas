"""Sorting of canonical tokens by the order of a profile.

This step is plain code, not a transducer: see docs/normalization-sorting.md
for why a finite-state machine cannot do it in general.
"""

from __future__ import annotations

from src.vocabulary import PROFILE_ORDER, TOKENS, Profile


def _check_known(tokens: list[str]) -> None:
    unknown = sorted({token for token in tokens if token not in TOKENS})
    if unknown:
        raise ValueError(f"not canonical tokens: {', '.join(unknown)}")


def sort_by_vocabulary(tokens: list[str]) -> list[str]:
    """Order tokens as they appear in ``vocabulary.TOKENS`` (no profile).

    Used where one list is needed for all profiles, such as the skills of the
    candidate profile in stage 4.
    """
    _check_known(tokens)
    position = {token: index for index, token in enumerate(TOKENS)}
    return sorted(tokens, key=position.__getitem__)


def sort_for_profile(tokens: list[str], profile: Profile) -> list[str]:
    """Order tokens by ``vocabulary.PROFILE_ORDER[profile]``.

    The sort key of a token is a pair:

    1. the position of its category in the order of the profile; a category
       that the profile does not list goes after all the listed ones;
    2. its position in ``vocabulary.TOKENS``, which breaks ties inside a
       category (and keeps the tokens outside the profile in a fixed order).

    The key depends only on the token, so the result does not depend on the
    order of the input. Raises ValueError for a string that is not a token.
    """
    _check_known(tokens)
    rank = {category: index for index, category in enumerate(PROFILE_ORDER[profile])}
    outside = len(rank)
    position = {token: index for index, token in enumerate(TOKENS)}
    return sorted(
        tokens,
        key=lambda token: (rank.get(TOKENS[token], outside), position[token]),
    )
