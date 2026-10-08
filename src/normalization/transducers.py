"""The named transducers of stage 2.

Each one is a dictionary D built from one group of ``variants.py``. They are
built once and cached.
"""

from __future__ import annotations

from functools import lru_cache

from pyformlang.fst import FST

from src.normalization.fst import build_transducer
from src.normalization.variants import FRAMEWORK_VARIANTS, LANGUAGE_VARIANTS


@lru_cache(maxsize=None)
def languages_transducer() -> FST:
    """Programming languages: ``JS`` -> ``JAVASCRIPT``, ``C++`` -> ``CPP``."""
    return build_transducer(LANGUAGE_VARIANTS)


@lru_cache(maxsize=None)
def frameworks_transducer() -> FST:
    """Frameworks and libraries: ``React.js`` -> ``REACT``, ``sklearn`` ->
    ``SCIKIT_LEARN``."""
    return build_transducer(FRAMEWORK_VARIANTS)
