"""The named transducers of stage 2.

Each one is a dictionary D built from one group of ``variants.py``. They are
built once and cached.
"""

from __future__ import annotations

from functools import lru_cache

from pyformlang.fst import FST

from src.normalization.fst import build_transducer, clean, translate_key
from src.normalization.variants import (
    DATABASE_TOOL_VARIANTS,
    FRAMEWORK_VARIANTS,
    LANGUAGE_VARIANTS,
)


@lru_cache(maxsize=None)
def languages_transducer() -> FST:
    """Programming languages: ``JS`` -> ``JAVASCRIPT``, ``C++`` -> ``CPP``."""
    return build_transducer(LANGUAGE_VARIANTS)


@lru_cache(maxsize=None)
def frameworks_transducer() -> FST:
    """Frameworks and libraries: ``React.js`` -> ``REACT``, ``sklearn`` ->
    ``SCIKIT_LEARN``."""
    return build_transducer(FRAMEWORK_VARIANTS)


@lru_cache(maxsize=None)
def databases_tools_transducer() -> FST:
    """Databases, tools and concepts: ``Postgres`` -> ``POSTGRESQL``,
    ``GitHub`` -> ``GIT``, ``RESTful API`` -> ``REST_API``."""
    return build_transducer(DATABASE_TOOL_VARIANTS)


def all_transducers() -> dict[str, FST]:
    """The three dictionaries by name, in the order they are tried."""
    return {
        "languages": languages_transducer(),
        "frameworks": frameworks_transducer(),
        "databases_tools": databases_tools_transducer(),
    }


def canonical_token(raw: str) -> str | None:
    """Raw string -> canonical token, or None if it has no canonical form.

    The cleaner runs once; then the three dictionaries are tried in order.
    Their keys are disjoint, so at most one of them accepts the key.
    """
    key = clean(raw)
    if not key:
        return None
    for dictionary in all_transducers().values():
        token = translate_key(dictionary, key)
        if token is not None:
            return token
    return None
