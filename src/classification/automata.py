"""Stage 3 automata, built with ``pyformlang`` (see docs/classification-design.md).

Each profile's automaton reads the *category* sequence of a resume's sorted
tokens (``vocabulary.TOKENS`` maps a token to its ``Category``) and accepts
iff every category the profile requires appeared at least once. It is a
"required categories seen so far" counter: state ``qi`` means the first
``i`` required categories, in the profile's order, have already appeared.
Stage 2 already sorts the tokens by ``PROFILE_ORDER``, so the required
categories (when present) reach this automaton in non-decreasing order;
the automaton only has to confirm each one shows up once while reading
left to right.
"""

from __future__ import annotations

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State

from src.vocabulary import Category

ALPHABET: set[str] = {category.value for category in Category}
"""Input alphabet shared by every profile automaton: the nine categories."""


def build_automaton(required: list[Category]) -> DeterministicFiniteAutomaton:
    """A DFA (5-tuple ``Q, Σ, δ, q0, F``) that accepts a category sequence
    iff every category in ``required`` appears at least once, in that order.

    * ``Q = {q0, ..., qk}``, ``k = len(required)``.
    * ``Σ`` = every ``Category`` (``ALPHABET``), the same for all profiles.
    * ``δ(qi, c)``: ``qi+1`` if ``c`` is the next pending required category
      (``i < k`` and ``c == required[i]``); otherwise ``qi`` (self-loop —
      an optional category, a repeat, or one outside the profile at all).
      The final state ``qk`` also self-loops on every symbol: once every
      required category has been seen, nothing read afterwards changes the
      verdict.
    * ``q0`` is the initial state.
    * ``F = {qk}``.

    ``δ`` is defined for every ``(state, symbol)`` pair with exactly one
    result, so this is a DFA by construction, not something checked after
    the fact.
    """
    size = len(required)
    states = {State(f"q{i}") for i in range(size + 1)}
    dfa = DeterministicFiniteAutomaton(
        states=states,
        input_symbols=ALPHABET,
        start_state=State("q0"),
        final_states={State(f"q{size}")},
    )
    for i, category in enumerate(required):
        current, next_state = State(f"q{i}"), State(f"q{i + 1}")
        for symbol in ALPHABET:
            target = next_state if symbol == category.value else current
            dfa.add_transition(current, symbol, target)
    final = State(f"q{size}")
    for symbol in ALPHABET:
        dfa.add_transition(final, symbol, final)
    return dfa


FULL_STACK_REQUIRED: list[Category] = [
    Category.LANGUAGE,
    Category.FRONTEND,
    Category.BACKEND,
    Category.DATABASE,
    Category.VERSION_CONTROL,
]
"""Required categories for FULL_STACK_DEVELOPER (see docs/classification-design.md
section 3). CONCEPT (e.g. REST API) is read but optional."""


def build_full_stack_developer() -> DeterministicFiniteAutomaton:
    """DFA for ``Profile.FULL_STACK_DEVELOPER``."""
    return build_automaton(FULL_STACK_REQUIRED)


MACHINE_LEARNING_ENGINEER_REQUIRED: list[Category] = [
    Category.LANGUAGE,
    Category.DATA_LIBRARY,
    Category.ML_LIBRARY,
]
"""Required categories for MACHINE_LEARNING_ENGINEER (see
docs/classification-design.md section 3). DATABASE, VERSION_CONTROL and
CONCEPT are read but optional."""


def build_machine_learning_engineer() -> DeterministicFiniteAutomaton:
    """DFA for ``Profile.MACHINE_LEARNING_ENGINEER``."""
    return build_automaton(MACHINE_LEARNING_ENGINEER_REQUIRED)
