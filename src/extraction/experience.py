"""Stage 1 - professional experience (years and job entries)."""

from __future__ import annotations

from src.extraction import patterns

_WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _to_years(raw: str) -> int:
    word = raw.lower()
    if word in _WORD_NUMBERS:
        return _WORD_NUMBERS[word]
    return int(float(raw.replace(",", ".")))


def extract_experience_years(text: str) -> int | None:
    """Years of experience stated in the text; the largest one if several."""
    years = [_to_years(m.group(1)) for m in patterns.EXPERIENCE_YEARS.finditer(text)]
    return max(years) if years else None


def extract_experience(text: str) -> list[str]:
    """Experience statements and job entries, in order of appearance.

    A statement is "3 years of experience developing web applications"; a job
    entry is "Backend Developer at Acme Corp (2020 - 2023)".
    """
    found: list[tuple[int, str]] = []
    for pattern in (patterns.EXPERIENCE_STATEMENT, patterns.JOB):
        for m in pattern.finditer(text):
            found.append((m.start(), " ".join(m.group(0).split())))
    found.sort(key=lambda item: item[0])
    return list(dict.fromkeys(entry for _, entry in found))
