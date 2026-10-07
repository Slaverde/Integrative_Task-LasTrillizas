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
from src.extraction.experience import extract_experience, extract_experience_years
from src.extraction.skills import (
    extract_concepts,
    extract_databases,
    extract_frameworks,
    extract_languages,
    extract_tools,
)


def extract(text: str) -> ExtractionResult:
    """Extract contact data, skills, education and experience from resume text.

    Input:  resume text (str).
    Output: ExtractionResult with raw strings, no normalization.

    Every field of ExtractionResult is filled; a field with nothing found
    stays empty (or None for the name and the years of experience).
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return ExtractionResult(
        name=extract_name(text),
        emails=extract_emails(text),
        phones=extract_phones(text),
        links=extract_links(text),
        languages=extract_languages(text),
        frameworks=extract_frameworks(text),
        databases=extract_databases(text),
        tools=extract_tools(text),
        concepts=extract_concepts(text),
        education=extract_education(text),
        experience_years=extract_experience_years(text),
        experience=extract_experience(text),
    )
