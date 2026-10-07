"""Stage 1 - technical skills (languages, frameworks/libraries, databases)."""

from __future__ import annotations

import re

from src.extraction import patterns


def _matches(pattern: re.Pattern[str], text: str) -> list[re.Match[str]]:
    return list(pattern.finditer(text))


def _unique_ignoring_case(items: list[str]) -> list[str]:
    """Remove duplicates ("JS" and "js") keeping the first spelling seen."""
    seen: dict[str, str] = {}
    for item in items:
        seen.setdefault(item.casefold(), item)
    return list(seen.values())


def _inside(match: re.Match[str], others: list[re.Match[str]]) -> bool:
    return any(o.start() <= match.start() and match.end() <= o.end() for o in others)


def extract_frameworks(text: str) -> list[str]:
    """Frameworks and libraries as written (``React.js``, ``scikit learn``)."""
    return _unique_ignoring_case(m.group(0) for m in _matches(patterns.FRAMEWORK, text))


def extract_languages(text: str) -> list[str]:
    """Programming languages as written (``JS``, ``Javascript``).

    A match that is part of a framework name (the ``JS`` of ``Node JS``) is
    discarded, so it is not reported twice.
    """
    frameworks = _matches(patterns.FRAMEWORK, text)
    found = (
        m.group(0)
        for m in _matches(patterns.LANGUAGE, text)
        if not _inside(m, frameworks)
    )
    return _unique_ignoring_case(found)


def extract_databases(text: str) -> list[str]:
    """Database technologies as written (``Postgres``, ``Mongo DB``)."""
    return _unique_ignoring_case(m.group(0) for m in _matches(patterns.DATABASE, text))


def extract_tools(text: str) -> list[str]:
    """Tools and platforms as written (``Git``, ``GitHub``, ``Docker``).

    A match inside a link or an e-mail (the ``github`` of ``github.com/ana``)
    is contact data, not a skill, so it is discarded.
    """
    contact = _matches(patterns.LINK, text) + _matches(patterns.EMAIL, text)
    found = (
        m.group(0) for m in _matches(patterns.TOOL, text) if not _inside(m, contact)
    )
    return _unique_ignoring_case(found)


def extract_concepts(text: str) -> list[str]:
    """Other qualifications as written (``REST APIs``, ``machine learning``)."""
    return _unique_ignoring_case(m.group(0) for m in _matches(patterns.CONCEPT, text))
