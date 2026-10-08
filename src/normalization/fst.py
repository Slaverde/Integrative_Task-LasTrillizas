"""Finite-state transducers of stage 2, built with ``pyformlang``.

Two kinds of machines are used (see docs/normalization-design.md):

* the **cleaner** C reads a raw string and writes its key (upper case, no
  accents, no separators);
* a **dictionary** D reads a key followed by the end marker and writes the
  canonical token. It is a prefix tree with one branch per spelling.

``translate`` runs C and then D.
"""

from __future__ import annotations

import string
from functools import lru_cache

from pyformlang.finite_automaton import State, Symbol
from pyformlang.fst import FST

from src.normalization.variants import (
    ACCENTS,
    KEPT_SYMBOLS,
    SEPARATORS,
    Variants,
    key_map,
)

END_MARKER = "⊣"
"""Extra input symbol read by D after the key; the token is written on it."""

START = "q0"


def build_cleaner() -> FST:
    """The cleaner C: one state, which is both initial and final.

    Every transition goes from ``q0`` back to ``q0``:

    * ``a-z``                      writes the upper-case letter;
    * ``A-Z``, ``0-9``, ``+``      write themselves;
    * separators                   write nothing (an empty output);
    * accented letters             write the plain upper-case letter.
    """
    fst = FST()
    state = State(START)
    fst.add_start_state(state)
    fst.add_final_state(state)
    for char in string.ascii_lowercase:
        fst.add_transition(state, char, state, [char.upper()])
    for char in string.ascii_uppercase + string.digits + KEPT_SYMBOLS:
        fst.add_transition(state, char, state, [char])
    for char in SEPARATORS:
        fst.add_transition(state, char, state, [])
    for char, plain in ACCENTS.items():
        fst.add_transition(state, char, state, [plain])
    return fst


def build_transducer(variants: Variants) -> FST:
    """A dictionary D: a deterministic prefix tree over the keys.

    States: ``q0`` (initial), ``p:<prefix>`` for every proper prefix of a key
    and for every whole key, and ``f:<TOKEN>`` (final) for every token.
    Transitions: one per letter of a key, writing nothing, and one on the end
    marker from the whole key to ``f:<TOKEN>``, writing the token.
    """
    fst = FST()
    start = State(START)
    fst.add_start_state(start)
    edges: set[tuple[str, str, str]] = set()

    def link(source: str, symbol: str, target: str, output: list[str]) -> None:
        if (source, symbol, target) not in edges:
            edges.add((source, symbol, target))
            fst.add_transition(State(source), symbol, State(target), output)

    for key, token in sorted(key_map(variants).items()):
        source = START
        for position, char in enumerate(key, start=1):
            target = f"p:{key[:position]}"
            link(source, char, target, [])
            source = target
        final = f"f:{token}"
        link(source, END_MARKER, final, [token])
        fst.add_final_state(State(final))
    return fst


def is_deterministic(fst: FST) -> bool:
    """True if no state has two transitions on the same input symbol."""
    return all(len(targets) == 1 for targets in fst.transitions.values())


def _run(fst: FST, symbols: list[str]) -> str | None:
    outputs = list(fst.translate([Symbol(symbol) for symbol in symbols]))
    if not outputs:
        return None
    return "".join(str(symbol) for symbol in outputs[0])


@lru_cache(maxsize=None)
def cleaner() -> FST:
    return build_cleaner()


def clean(text: str) -> str | None:
    """Run the cleaner. None if the text has a character it does not know."""
    return _run(cleaner(), list(text))


def translate_key(dictionary: FST, key: str) -> str | None:
    """Run a dictionary on a key. None if the key is not a known spelling."""
    return _run(dictionary, [*key, END_MARKER])


def translate(dictionary: FST, text: str) -> str | None:
    """Raw string -> canonical token (cleaner, then dictionary), or None."""
    key = clean(text)
    if not key:
        return None
    return translate_key(dictionary, key)
