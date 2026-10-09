"""Diagrams and counts of the stage 2 transducers, generated from the machines.

The Mermaid blocks of docs/normalization-transducers.md are produced here, so
the drawings cannot disagree with the code (a test compares them).

    python -m src.normalization.diagrams            # print every block
    python -m src.normalization.diagrams languages  # only one transducer
"""

from __future__ import annotations

import sys

from pyformlang.fst import FST

from src.normalization.fst import build_cleaner
from src.normalization.transducers import all_transducers


def summary(fst: FST) -> dict[str, int]:
    """Sizes used in the 7-tuples: |Q|, |Σ|, |Γ|, |δ| and |F|."""
    return {
        "states": len(fst.states),
        "input_symbols": len(fst.input_symbols),
        "output_symbols": len(fst.output_symbols),
        "transitions": fst.get_number_transitions(),
        "final_states": len(fst.final_states),
    }


def _edges(fst: FST) -> list[tuple[str, str, str, str]]:
    """(source, input, target, output) for every transition, sorted."""
    edges = []
    for (source, symbol), targets in fst.transitions.items():
        for target, output in targets:
            written = "".join(str(s) for s in output)
            edges.append((str(source), str(symbol), str(target), written))
    return sorted(edges)


def mermaid_compact(fst: FST) -> str:
    """Mermaid flowchart of a dictionary D with chains of states merged.

    A state that has one way in, one way out and is not initial or final is
    folded into its edge, so the edge label is the whole string it reads
    (``JS⊣`` is the path J, S, ⊣). Branching states, the initial state and the
    final states are drawn; final states have a double circle.
    """
    edges = _edges(fst)
    outgoing: dict[str, list[tuple[str, str, str]]] = {}
    incoming: dict[str, int] = {}
    for source, symbol, target, output in edges:
        outgoing.setdefault(source, []).append((symbol, target, output))
        incoming[target] = incoming.get(target, 0) + 1

    starts = {str(s) for s in fst.start_states}
    finals = {str(s) for s in fst.final_states}
    kept = sorted(
        str(state)
        for state in fst.states
        if str(state) in starts
        or str(state) in finals
        or len(outgoing.get(str(state), [])) != 1
        or incoming.get(str(state), 0) != 1
    )
    ids = {state: f"n{index}" for index, state in enumerate(kept)}

    lines = ["flowchart LR"]
    for state in kept:
        label = state
        if state in finals:
            lines.append(f'    {ids[state]}((("{label}")))')
        elif state in starts:
            lines.append(f'    {ids[state]}(("{label}"))')
        else:
            lines.append(f'    {ids[state]}("{label}")')

    for state in kept:
        for symbol, target, output in sorted(outgoing.get(state, [])):
            word, written = symbol, output
            while target not in ids:  # fold a chain of states into one edge
                next_symbol, next_target, next_output = outgoing[target][0]
                word += next_symbol
                written += next_output
                target = next_target
            label = f"{word} / {written}" if written else word
            lines.append(f'    {ids[state]} -->|"{label}"| {ids[target]}')
    return "\n".join(lines)


def mermaid_cleaner() -> str:
    """Mermaid diagram of the cleaner C (one state, self-loops grouped by kind)."""
    return "\n".join(
        [
            "flowchart LR",
            '    q0((("q0")))',
            '    q0 -->|"a-z / A-Z"| q0',
            '    q0 -->|"A-Z 0-9 + / same symbol"| q0',
            '    q0 -->|"space tab - . _ / ε"| q0',
            '    q0 -->|"accented letter / plain upper-case letter"| q0',
        ]
    )


def counts_table() -> str:
    """Markdown table with |Q|, |Σ|, |Γ|, |δ| and |F| of every transducer."""
    machines = {"C (cleaner)": build_cleaner(), **all_transducers()}
    lines = [
        "| Transducer | \\|Q\\| | \\|Σ\\| | \\|Γ\\| | \\|δ\\| | \\|F\\| |",
        "|---|---|---|---|---|---|",
    ]
    for name, fst in machines.items():
        n = summary(fst)
        lines.append(
            f"| {name} | {n['states']} | {n['input_symbols']} | "
            f"{n['output_symbols']} | {n['transitions']} | {n['final_states']} |"
        )
    return "\n".join(lines)


def blocks() -> dict[str, str]:
    """Every generated block by name."""
    result = {"cleaner": mermaid_cleaner(), "counts": counts_table()}
    for name, fst in all_transducers().items():
        result[name] = mermaid_compact(fst)
    return result


def main(argv: list[str]) -> int:
    machines = all_transducers()
    wanted = argv or ["counts", "cleaner", *machines]
    generated = blocks()
    for name in wanted:
        if name not in generated:
            print(f"unknown transducer {name!r}; use one of {list(generated)}")
            return 2
        print(f"%% {name}")
        print(generated[name])
        if name in machines:
            print(f"%% {name}: {summary(machines[name])}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
