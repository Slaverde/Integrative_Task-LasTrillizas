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
from src.extraction.skills import extract_databases, extract_frameworks, extract_languages


def extract(text: str) -> ExtractionResult:
    """Extract contact data, skills, education and experience from resume text.

    Input:  resume text (str).
    Output: ExtractionResult with raw strings, no normalization.

    Contact data, education, languages, frameworks and databases are extracted
    so far; tools, concepts and experience are added in the next commit and
    stay empty until then.
    """
    return ExtractionResult(
        name=extract_name(text),
        emails=extract_emails(text),
        phones=extract_phones(text),
        links=extract_links(text),
        languages=extract_languages(text),
        frameworks=extract_frameworks(text),
        databases=extract_databases(text),
        education=extract_education(text),
    )
