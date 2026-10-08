"""The plain CFG and its Chomsky normal form describe the same language as textX.

Three independent recognizers are compared on the example files and on
thousands of mutated and randomly generated sentences:

* textX (``src.dsl.parse``): the real grammar of the project,
* pyformlang on the BNF version of the grammar (``src/dsl/cfg.py``),
* a CYK recognizer on the Chomsky normal form (``src/dsl/normal_form.py``).
"""

import random
from functools import lru_cache
from pathlib import Path

import pytest
from pyformlang.cfg import CFG, Production, Terminal, Variable

from src.dsl import DSLSyntaxError, parse
from src.dsl.cfg import BNF, EPSILON, START, LexError, is_variable, lex, parse_bnf, terminals_of
from src.dsl.normal_form import (
    cyk,
    eliminate_epsilon,
    eliminate_units,
    format_rules,
    is_cnf,
    load,
    normalize,
    nullable_symbols,
    remove_useless,
    unit_pairs,
)

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples" / "dsl"
VALID = sorted((EXAMPLES / "valid").glob("*.rl"))
INVALID = sorted((EXAMPLES / "invalid").glob("*.rl"))


# --- recognizers -----------------------------------------------------------------------


@lru_cache(maxsize=1)
def report():
    return normalize()


@lru_cache(maxsize=1)
def pyformlang_cfg() -> CFG:
    productions = set()
    for head, bodies in parse_bnf().items():
        for body in bodies:
            symbols = [Variable(s) if is_variable(s) else Terminal(s) for s in body]
            productions.add(Production(Variable(head), symbols))
    return CFG(productions=productions, start_symbol=Variable(START))


def textx_accepts(text: str) -> bool:
    try:
        parse(text)
        return True
    except DSLSyntaxError:
        return False


def cnf_accepts(text: str) -> bool:
    try:
        return cyk(report().cnf, terminals_of(text))
    except LexError:
        return False


def bnf_accepts(text: str) -> bool:
    try:
        word = [Terminal(t) for t in terminals_of(text)]
    except LexError:
        return False
    return bool(word) and pyformlang_cfg().contains(word)


def assert_all_agree(text: str, expected: bool | None = None):
    results = {
        "textX": textx_accepts(text),
        "BNF (pyformlang)": bnf_accepts(text),
        "CNF (CYK)": cnf_accepts(text),
    }
    assert len(set(results.values())) == 1, f"recognizers disagree on {text!r}: {results}"
    if expected is not None:
        assert results["textX"] is expected, text


# --- the forms -------------------------------------------------------------------------


def test_bnf_has_no_ebnf_operators():
    for line in BNF.strip().splitlines():
        if line.strip():
            assert not set("[]()") & set(line.split("->")[1].replace("{", "").replace("}", ""))


def test_original_grammar_is_in_the_expected_shape():
    grammar = load()
    assert grammar.start == START
    assert len(grammar.rules) == 23
    # epsilon productions are stored as empty bodies
    assert sum(1 for b in parse_bnf().values() for body in b if body == ()) == 9


def test_nullable_variables():
    assert nullable_symbols(load()) == {
        "OptContact", "OptExperience", "OptEducation", "OptSkillList",
        "ContactTail", "JobList", "StudyList", "SkillTail", "ResultTail",
    }


def test_no_epsilon_productions_after_step_1():
    grammar = eliminate_epsilon(load())
    assert all(body for bodies in grammar.rules.values() for body in bodies)


def test_no_unit_productions_after_step_2():
    grammar = eliminate_units(eliminate_epsilon(load()))
    for bodies in grammar.rules.values():
        for body in bodies:
            assert not (len(body) == 1 and is_variable(body[0]))


def test_unit_pairs_contain_the_chains_of_the_grammar():
    pairs = unit_pairs(eliminate_epsilon(load()))
    assert ("Tok", "Tok") in pairs
    assert ("OptContact", "Contact") in pairs
    assert ("OptSkillList", "SkillList") in pairs
    # SkillList -> Tok SkillTail, and SkillTail is nullable, so SkillList -> Tok
    assert ("OptSkillList", "Tok") in pairs


def test_useless_symbols_are_removed_after_step_3():
    useful = report().useful
    reachable = {useful.start}
    pending = [useful.start]
    while pending:
        for body in useful.rules[pending.pop()]:
            for s in body:
                if is_variable(s) and s not in reachable:
                    reachable.add(s)
                    pending.append(s)
    assert reachable == set(useful.rules)
    assert len(useful.rules) < len(report().no_units.rules)


def test_result_is_in_chomsky_normal_form():
    cnf = report().cnf
    assert is_cnf(cnf)
    assert all(body for bodies in cnf.rules.values() for body in bodies)
    for bodies in cnf.rules.values():
        for body in bodies:
            assert len(body) in (1, 2)
            if len(body) == 1:
                assert not is_variable(body[0])
            else:
                assert all(is_variable(s) for s in body)


def test_the_start_symbol_never_appears_on_a_right_side():
    cnf = report().cnf
    assert all(cnf.start not in body for bodies in cnf.rules.values() for body in bodies)


def test_terminals_are_preserved():
    assert report().cnf.terminals == load().terminals == report().useful.terminals


def test_is_cnf_rejects_other_shapes():
    broken = report().cnf.copy()
    broken.rules["Status"].add(("accepted", "rejected"))
    assert not is_cnf(broken)
    broken = report().cnf.copy()
    broken.rules["Status"].add(("Tok",))
    assert not is_cnf(broken)


def test_markdown_document_lists_the_same_normal_form():
    doc = (ROOT / "docs" / "dsl-grammar-normal-form.md").read_text(encoding="utf-8")
    for line in format_rules(report().cnf):
        assert line in doc, line
    for line in BNF.strip().splitlines():
        if line.strip():
            assert " ".join(line.split()) in " ".join(doc.split()), line


# --- the lexer ---------------------------------------------------------------------------


def test_lexer_classifies_terminals():
    text = 'candidate "Ana" { years: 3 job: "x" skills { GIT, NODE_JS } results { A: ACCEPTED } } // end'
    assert terminals_of(text) == [
        "candidate", "text", "lbrace", "years", "colon", "number", "job", "colon", "text",
        "skills", "lbrace", "token", "comma", "token", "rbrace",
        "results", "lbrace", "token", "colon", "accepted", "rbrace", "rbrace",
    ]


@pytest.mark.parametrize("text", ["git", '"open', "candidate Ana", "skills ?", "ab"])
def test_lexer_rejects_what_is_not_a_terminal(text):
    with pytest.raises(LexError):
        lex(text)


def test_a_number_glued_to_a_token_is_two_terminals():
    assert terminals_of("9GIT") == ["number", "token"]


# --- the examples ----------------------------------------------------------------------------


@pytest.mark.parametrize("path", VALID, ids=[p.stem for p in VALID])
def test_valid_examples_are_in_the_language_of_every_grammar(path):
    assert_all_agree(path.read_text(encoding="utf-8"), expected=True)


@pytest.mark.parametrize("path", INVALID, ids=[p.stem for p in INVALID])
def test_invalid_examples_get_the_same_verdict_in_every_grammar(path):
    # semantic examples are valid for the grammar; the others are not
    assert_all_agree(path.read_text(encoding="utf-8"), expected=path.name.startswith("semantic"))


# --- mutations of the valid examples -----------------------------------------------------------

FILLERS = ["{", "}", ":", ",", "candidate", "skills", "results", "years", "job", '"x"', "7", "GIT", "ACCEPTED"]


def mutations(path: Path, seed: int):
    values = [lexeme.value for lexeme in lex(path.read_text(encoding="utf-8"))]
    rng = random.Random(seed)
    for i in range(len(values)):
        yield "delete", " ".join(values[:i] + values[i + 1 :])
        yield "duplicate", " ".join(values[: i + 1] + values[i:])
        if i + 1 < len(values):
            swapped = values[:]
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
            yield "swap", " ".join(swapped)
        replaced = values[:]
        replaced[i] = rng.choice(FILLERS)
        yield "replace", " ".join(replaced)


@pytest.mark.parametrize("path", VALID, ids=[p.stem for p in VALID])
def test_mutated_examples_get_the_same_verdict_in_every_grammar(path):
    cases = [text for _, text in mutations(path, seed=2026)]
    sample = random.Random(1).sample(cases, min(len(cases), 100))
    checked = rejected = 0
    for text in sample:
        assert_all_agree(text)
        checked += 1
        rejected += not cnf_accepts(text)
    assert checked >= 100
    assert rejected > checked // 2  # most mutations really break the sentence


# --- random sentences of the grammar ---------------------------------------------------------------


def generate(rng: random.Random, symbol: str = START, depth: int = 0) -> list[str]:
    if not is_variable(symbol):
        return [symbol]
    bodies = parse_bnf()[symbol]
    if depth > 6:
        body = min(bodies, key=len)  # the shortest alternative ends the recursion
    else:
        body = rng.choice(bodies)
    return [t for s in body for t in generate(rng, s, depth + 1)]


def to_text(terminals: list[str], rng: random.Random) -> str:
    fill = {
        "text": lambda: '"' + rng.choice(["Ana", "a b", "x", ""]) + '"',
        "number": lambda: str(rng.randint(0, 99)),
        "token": lambda: rng.choice(["GIT", "NODE_JS", "SQL", "Z9"]),
        "lbrace": lambda: "{", "rbrace": lambda: "}", "colon": lambda: ":", "comma": lambda: ",",
        "accepted": lambda: "ACCEPTED", "rejected": lambda: "REJECTED",
    }
    return " ".join(fill[t]() if t in fill else t for t in terminals)


def test_random_sentences_of_the_grammar_are_accepted_everywhere():
    rng = random.Random(7)
    seen_lengths = set()
    for _ in range(300):
        terminals = generate(rng)
        text = to_text(terminals, rng)
        seen_lengths.add(len(terminals))
        assert_all_agree(text, expected=True)
    assert len(seen_lengths) > 10  # the sample is varied, not always the same shape


def test_random_sentences_use_every_optional_section():
    rng = random.Random(11)
    words = {t for _ in range(300) for t in generate(rng)}
    assert {"contact", "experience", "education", "email", "phone", "link", "years", "job", "study"} <= words


def test_epsilon_is_only_the_empty_body():
    assert EPSILON not in {s for b in parse_bnf().values() for body in b for s in body}
    assert not cyk(report().cnf, [])


def test_semantic_rules_are_outside_the_grammar():
    # An unknown skill is a valid sentence for the CFG: only semantics.py rejects it.
    text = (EXAMPLES / "invalid" / "semantic_unknown_skill.rl").read_text(encoding="utf-8")
    assert_all_agree(text, expected=True)


def test_status_words_are_also_valid_tokens_in_every_grammar():
    # textX reads ACCEPTED as a token anywhere a token is allowed; the CFG must too.
    text = 'candidate "A" { skills { ACCEPTED, REJECTED } results { ACCEPTED: ACCEPTED } }'
    assert_all_agree(text, expected=True)
