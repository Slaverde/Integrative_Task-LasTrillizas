"""Stage 1 - academic qualifications (degrees and institutions)."""

from __future__ import annotations

from src.extraction import patterns


def extract_education(text: str) -> list[str]:
    """Degree phrases and institution names, in order of appearance."""
    found: list[tuple[int, str]] = []
    for pattern in (patterns.DEGREE, patterns.INSTITUTION):
        for m in pattern.finditer(text):
            found.append((m.start(), " ".join(m.group(0).split())))
    found.sort(key=lambda item: item[0])
    return list(dict.fromkeys(entry for _, entry in found))
