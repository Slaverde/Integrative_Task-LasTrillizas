"""Diagrams and counts of the stage 3 automata, generated from the machines.

The Mermaid blocks of docs/classification-automata.md are produced here, so
the drawings cannot disagree with the code (a test compares them). Mirrors
``src/normalization/diagrams.py``'s role for stage 2, adapted to a DFA.

    python -m src.classification.diagrams                      # every block
    python -m src.classification.diagrams full_stack_developer  # one automaton
"""

from __future__ import annotations

import sys

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from src.classification.automata import (
    build_backend_developer,
    build_data_scientist,
    build_full_stack_developer,
    build_machine_learning_engineer,
)

AUTOMATA_BUILDERS = {
    "full_stack_developer": build_full_stack_developer,
    "machine_learning_engineer": build_machine_learning_engineer,
    "backend_developer": build_backend_developer,
    "data_scientist": build_data_scientist,
}


def summary(dfa: DeterministicFiniteAutomaton) -> dict[str, int]:
    """Sizes used in the 5-tuples: |Q|, |Σ|, |δ| and |F|."""
    return {
        "states": len(dfa.states),
        "input_symbols": len(dfa.symbols),
        "transitions": dfa.get_number_transitions(),
        "final_states": len(dfa.final_states),
    }


def required_path(dfa: DeterministicFiniteAutomaton) -> list[tuple[str, str, str]]:
    """(source, category, target) for every transition that advances the
    state, in state order: the required-category order of the profile.

    By construction (``automata.build_automaton``), every non-final state
    has exactly one such transition - the rest are self-loops - so this
    reads the profile's requirement straight off the automaton instead of
    importing ``FULL_STACK_REQUIRED`` and friends: the diagram can only
    disagree with the code if the automaton itself is wrong.
    """
    transitions = dfa.to_dict()
    size = len(dfa.states) - 1
    path = []
    for i in range(size):
        source = f"q{i}"
        for symbol, target in transitions[source].items():
            if str(target) != source:
                path.append((source, str(symbol), str(target)))
                break
    return path


def mermaid(dfa: DeterministicFiniteAutomaton) -> str:
    """Mermaid flowchart: one edge per required category (the linear path
    from q0 to the accepting state) plus one grouped self-loop per state
    for every other category (optional, repeated, or outside the profile).
    """
    path = required_path(dfa)
    finals = {str(state) for state in dfa.final_states}
    starts = {str(state) for state in dfa.start_states}
    states = [f"q{i}" for i in range(len(dfa.states))]

    lines = ["flowchart LR"]
    for state in states:
        if state in finals:
            lines.append(f'    {state}((("{state}")))')
        elif state in starts:
            lines.append(f'    {state}(("{state}"))')
        else:
            lines.append(f'    {state}("{state}")')
    for source, category, target in path:
        lines.append(f'    {source} -->|"{category}"| {target}')
    for state in states:
        label = "any category" if state in finals else "any other category"
        lines.append(f'    {state} -->|"{label}"| {state}')
    return "\n".join(lines)


def counts_table() -> str:
    """Markdown table with |Q|, |Σ|, |δ| and |F| of every automaton."""
    lines = [
        "| Automaton | \\|Q\\| | \\|Σ\\| | \\|δ\\| | \\|F\\| |",
        "|---|---|---|---|---|",
    ]
    for name, builder in AUTOMATA_BUILDERS.items():
        n = summary(builder())
        lines.append(
            f"| {name} | {n['states']} | {n['input_symbols']} | "
            f"{n['transitions']} | {n['final_states']} |"
        )
    return "\n".join(lines)


def blocks() -> dict[str, str]:
    """Every generated block by name."""
    result = {"counts": counts_table()}
    for name, builder in AUTOMATA_BUILDERS.items():
        result[name] = mermaid(builder())
    return result


def main(argv: list[str]) -> int:
    wanted = argv or ["counts", *AUTOMATA_BUILDERS]
    generated = blocks()
    for name in wanted:
        if name not in generated:
            print(f"unknown automaton {name!r}; use one of {list(generated)}")
            return 2
        print(f"%% {name}")
        print(generated[name])
        if name in AUTOMATA_BUILDERS:
            print(f"%% {name}: {summary(AUTOMATA_BUILDERS[name]())}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
