"""The candidate profile language as a plain context-free grammar (BNF).

``candidate.tx`` (textX) and ``docs/dsl-grammar.md`` (EBNF) describe the
language with repetitions and optional parts. This module writes the same
language with ordinary productions, without ``[ ]``, ``{ }`` or ``( )``, so it
can be simplified and converted to Chomsky normal form (``normal_form.py``).

Terminals are the keywords, the symbols and the three lexical classes
(``text``, ``number``, ``token``); the lexer below turns DSL text into them.
Variables start with a capital letter and terminals with a lowercase letter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

EPSILON = "epsilon"

BNF = """
Candidate     -> candidate text lbrace OptContact OptExperience OptEducation Skills Results rbrace

OptContact    -> Contact | epsilon
Contact       -> contact lbrace ContactItem ContactTail rbrace
ContactTail   -> ContactItem ContactTail | epsilon
ContactItem   -> email colon text | phone colon text | link colon text

OptExperience -> Experience | epsilon
Experience    -> experience lbrace ExpBody rbrace
ExpBody       -> years colon number JobList | Job JobList
JobList       -> Job JobList | epsilon
Job           -> job colon text

OptEducation  -> Education | epsilon
Education     -> education lbrace Study StudyList rbrace
StudyList     -> Study StudyList | epsilon
Study         -> study colon text

Skills        -> skills lbrace OptSkillList rbrace
OptSkillList  -> SkillList | epsilon
SkillList     -> Tok SkillTail
SkillTail     -> comma Tok SkillTail | epsilon

Results       -> results lbrace Result ResultTail rbrace
ResultTail    -> Result ResultTail | epsilon
Result        -> Tok colon Status
Status        -> accepted | rejected

Tok           -> token | accepted | rejected
"""

START = "Candidate"

KEYWORDS = {
    "candidate", "contact", "email", "phone", "link", "experience", "years",
    "job", "education", "study", "skills", "results",
}
SYMBOLS = {"{": "lbrace", "}": "rbrace", ":": "colon", ",": "comma"}

Production = tuple[str, tuple[str, ...]]


def is_variable(symbol: str) -> bool:
    return symbol[:1].isupper()


def parse_bnf(text: str = BNF) -> dict[str, list[tuple[str, ...]]]:
    """Read ``A -> x B | y`` lines. ``epsilon`` is the empty body ``()``."""
    rules: dict[str, list[tuple[str, ...]]] = {}
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        head, body = (part.strip() for part in line.split("->"))
        for alternative in body.split("|"):
            symbols = tuple(alternative.split())
            rules.setdefault(head, []).append(() if symbols == (EPSILON,) else symbols)
    return rules


# --- lexer -------------------------------------------------------------------------


@dataclass(frozen=True)
class Lexeme:
    terminal: str
    value: str


class LexError(ValueError):
    """The text contains something that is not a terminal of the language."""


_SCANNER = re.compile(
    r"""
    (?P<skip>\s+|//[^\n]*)
  | (?P<text>"[^"\n]*")
  | (?P<number>[0-9]+)
  | (?P<token>[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)
  | (?P<word>[a-z]+)
  | (?P<symbol>[{}:,])
    """,
    re.VERBOSE,
)


def lex(text: str) -> list[Lexeme]:
    """Split DSL text into terminals; raise LexError at the first bad character."""
    lexemes: list[Lexeme] = []
    position = 0
    while position < len(text):
        match = _SCANNER.match(text, position)
        if not match:
            raise LexError(f"unexpected character {text[position]!r} at offset {position}")
        kind, value = match.lastgroup, match.group()
        position = match.end()
        if kind == "skip":
            continue
        if kind == "word":
            if value not in KEYWORDS:
                raise LexError(f"unknown word {value!r}")
            lexemes.append(Lexeme(value, value))
        elif kind == "symbol":
            lexemes.append(Lexeme(SYMBOLS[value], value))
        elif kind == "token" and value in ("ACCEPTED", "REJECTED"):
            lexemes.append(Lexeme(value.lower(), value))
        else:
            lexemes.append(Lexeme(kind, value))
    return lexemes


def terminals_of(text: str) -> list[str]:
    return [lexeme.terminal for lexeme in lex(text)]
