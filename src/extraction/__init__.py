"""Stage 1 - information extraction with regular expressions (``re``)."""

from __future__ import annotations

from src.contracts import ExtractionResult
from src.extraction.contact import (
    extract_emails,
    extract_links,
    extract_name,
    extract_phones,
)
from src.extraction.education import extract_education


def extract(text: str) -> ExtractionResult:
    """Extract contact data, skills, education and experience from resume text.

    Input:  resume text (str).
    Output: ExtractionResult with raw strings, no normalization.

    Contact data and education are extracted so far; skills and experience
    are added in the next commits and stay empty until then.
    """
    return ExtractionResult(
        name=extract_name(text),
        emails=extract_emails(text),
        phones=extract_phones(text),
        links=extract_links(text),
        education=extract_education(text),
    )
