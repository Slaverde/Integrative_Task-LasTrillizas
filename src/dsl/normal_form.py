"""Simplification and Chomsky normal form of the candidate profile grammar.

Steps, in the usual order:

1. eliminate epsilon productions,
2. eliminate unit productions (``A -> B``),
3. remove useless symbols (not generating, not reachable),
4. Chomsky normal form: every production is ``A -> B C`` or ``A -> a``.

``python -m src.dsl.normal_form`` prints the result as Markdown.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from itertools import product

from src.dsl.cfg import START, is_variable, parse_bnf

Rules = dict[str, set[tuple[str, ...]]]


@dataclass
class Grammar:
    start: str
    rules: Rules

    @property
    def variables(self) -> set[str]:
        return set(self.rules)

    @property
    def terminals(self) -> set[str]:
        return {s for bodies in self.rules.values() for b in bodies for s in b if not is_variable(s)}

    def production_count(self) -> int:
        return sum(len(bodies) for bodies in self.rules.values())

    def copy(self) -> "Grammar":
        return Grammar(self.start, {a: set(b) for a, b in self.rules.items()})


def load() -> Grammar:
    return Grammar(START, {a: set(b) for a, b in parse_bnf().items()})


# --- 1. epsilon ----------------------------------------------------------------------


def nullable_symbols(grammar: Grammar) -> set[str]:
    nullable: set[str] = set()
    changed = True
    while changed:
        changed = False
        for head, bodies in grammar.rules.items():
            if head not in nullable and any(all(s in nullable for s in b) for b in bodies):
                nullable.add(head)
                changed = True
    return nullable


def eliminate_epsilon(grammar: Grammar) -> Grammar:
    nullable = nullable_symbols(grammar)
    rules: Rules = {}
    for head, bodies in grammar.rules.items():
        new: set[tuple[str, ...]] = set()
        for body in bodies:
            options = [(s,) if s not in nullable else (s, None) for s in body]
            for choice in product(*options):
                reduced = tuple(s for s in choice if s is not None)
                if reduced:
                    new.add(reduced)
        rules[head] = new
    if grammar.start in nullable:
        raise ValueError("the language contains the empty string")
    return Grammar(grammar.start, rules)


# --- 2. unit productions -------------------------------------------------------------


def unit_pairs(grammar: Grammar) -> set[tuple[str, str]]:
    pairs = {(a, a) for a in grammar.rules}
    changed = True
    while changed:
        changed = False
        for a, b in list(pairs):
            for body in grammar.rules.get(b, ()):
                if len(body) == 1 and is_variable(body[0]) and (a, body[0]) not in pairs:
                    pairs.add((a, body[0]))
                    changed = True
    return pairs


def eliminate_units(grammar: Grammar) -> Grammar:
    rules: Rules = {a: set() for a in grammar.rules}
    for a, b in unit_pairs(grammar):
        for body in grammar.rules[b]:
            if not (len(body) == 1 and is_variable(body[0])):
                rules[a].add(body)
    return Grammar(grammar.start, rules)


# --- 3. useless symbols --------------------------------------------------------------


def remove_useless(grammar: Grammar) -> Grammar:
    generating: set[str] = set()
    changed = True
    while changed:
        changed = False
        for head, bodies in grammar.rules.items():
            if head not in generating and any(
                all(not is_variable(s) or s in generating for s in b) for b in bodies
            ):
                generating.add(head)
                changed = True
    rules = {
        a: {b for b in bodies if all(not is_variable(s) or s in generating for s in b)}
        for a, bodies in grammar.rules.items()
        if a in generating
    }
    reachable = {grammar.start}
    pending = [grammar.start]
    while pending:
        for body in rules.get(pending.pop(), ()):
            for s in body:
                if is_variable(s) and s not in reachable:
                    reachable.add(s)
                    pending.append(s)
    return Grammar(grammar.start, {a: b for a, b in rules.items() if a in reachable})


# --- 4. Chomsky normal form ----------------------------------------------------------


def to_cnf(grammar: Grammar) -> Grammar:
    rules: Rules = {a: set() for a in grammar.rules}
    terminal_vars: dict[str, str] = {}
    chain_vars: dict[tuple[str, ...], str] = {}

    def lift(terminal: str) -> str:
        name = "T" + terminal.capitalize()
        terminal_vars[terminal] = name
        return name

    def split(head: str, symbols: tuple[str, ...]) -> None:
        """Write ``head -> symbols`` with bodies of at most two variables."""
        while len(symbols) > 2:
            rest = symbols[1:]
            is_new = rest not in chain_vars
            if is_new:
                chain_vars[rest] = f"X{len(chain_vars) + 1}"
                rules[chain_vars[rest]] = set()
            rules[head].add((symbols[0], chain_vars[rest]))
            if not is_new:
                return  # that helper already derives ``rest``
            head, symbols = chain_vars[rest], rest
        rules[head].add(symbols)

    for head, bodies in sorted(grammar.rules.items()):
        for body in sorted(bodies):
            if len(body) == 1:
                rules[head].add(body)
                continue
            lifted = tuple(lift(s) if not is_variable(s) else s for s in body)
            split(head, lifted)

    for terminal, name in terminal_vars.items():
        rules[name] = {(terminal,)}
    return Grammar(grammar.start, rules)


# --- pipeline and recognizer ----------------------------------------------------------


@dataclass
class Report:
    original: Grammar
    nullable: set[str]
    no_epsilon: Grammar
    pairs: set[tuple[str, str]]
    no_units: Grammar
    useful: Grammar
    cnf: Grammar


def normalize() -> Report:
    original = load()
    nullable = nullable_symbols(original)
    no_epsilon = eliminate_epsilon(original)
    pairs = unit_pairs(no_epsilon)
    no_units = eliminate_units(no_epsilon)
    useful = remove_useless(no_units)
    return Report(original, nullable, no_epsilon, pairs, no_units, useful, to_cnf(useful))


def is_cnf(grammar: Grammar) -> bool:
    for bodies in grammar.rules.values():
        for body in bodies:
            if len(body) == 1 and not is_variable(body[0]):
                continue
            if len(body) == 2 and all(is_variable(s) for s in body):
                continue
            return False
    return True


def cyk(grammar: Grammar, word: list[str]) -> bool:
    """CYK recognizer: is ``word`` (a list of terminals) in the language?"""
    n = len(word)
    if n == 0:
        return False
    by_terminal: dict[str, set[str]] = {}
    by_pair: dict[tuple[str, str], set[str]] = {}
    for head, bodies in grammar.rules.items():
        for body in bodies:
            if len(body) == 1:
                by_terminal.setdefault(body[0], set()).add(head)
            else:
                by_pair.setdefault(body, set()).add(head)
    table = [[set() for _ in range(n)] for _ in range(n)]  # table[i][l]: start i, length l+1
    for i, symbol in enumerate(word):
        table[i][0] = set(by_terminal.get(symbol, ()))
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            cell = table[i][length - 1]
            for split in range(1, length):
                for left in table[i][split - 1]:
                    for right in table[i + split][length - split - 1]:
                        cell |= by_pair.get((left, right), set())
    return grammar.start in table[0][n - 1]


def format_rules(grammar: Grammar) -> list[str]:
    """One line per variable: ``A -> x y | z``; start symbol first."""
    order = [grammar.start] + sorted(v for v in grammar.rules if v != grammar.start)
    lines = []
    for head in order:
        bodies = sorted(grammar.rules[head], key=lambda b: (len(b), b))
        lines.append(f"{head} -> " + " | ".join(" ".join(b) for b in bodies))
    return lines


def markdown_report() -> str:
    r = normalize()
    out = [
        f"- original: {len(r.original.rules)} variables, {r.original.production_count()} productions",
        f"- nullable variables: {', '.join(sorted(r.nullable))}",
        f"- after epsilon elimination: {r.no_epsilon.production_count()} productions",
        f"- after unit elimination: {r.no_units.production_count()} productions",
        f"- after removing useless symbols: {r.useful.production_count()} productions",
        f"- Chomsky normal form: {len(r.cnf.rules)} variables, {r.cnf.production_count()} productions",
        "",
        "```",
        *format_rules(r.cnf),
        "```",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(markdown_report())
