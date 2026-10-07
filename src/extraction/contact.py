"""Stage 1 - contact information (name, e-mails, phones, links)."""

from __future__ import annotations

from src.extraction import patterns

_LINK_TRAILING_PUNCTUATION = ".,;:)"


def _unique(items: list[str]) -> list[str]:
    """Remove duplicates keeping the order of first appearance."""
    return list(dict.fromkeys(items))


def extract_emails(text: str) -> list[str]:
    return _unique(patterns.EMAIL.findall(text))


def extract_phones(text: str) -> list[str]:
    return _unique(m.group(0) for m in patterns.PHONE.finditer(text))


def extract_links(text: str) -> list[str]:
    links = (
        m.group(0).rstrip(_LINK_TRAILING_PUNCTUATION)
        for m in patterns.LINK.finditer(text)
    )
    return _unique(links)


def extract_name(text: str) -> str | None:
    """Candidate name: an explicit ``Name:`` label, else the first name-like line.

    Only the first three non-empty lines are inspected, and heading words such
    as "Curriculum Vitae" are skipped.
    """
    labeled = patterns.LABELED_NAME.search(text)
    if labeled:
        return labeled.group(1)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:3]:
        if not patterns.NAME.fullmatch(line):
            continue
        if any(w.lower() in patterns.NAME_STOPWORDS for w in line.split()):
            continue
        return line
    return None
