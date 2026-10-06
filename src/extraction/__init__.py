"""Stage 1 - information extraction with regular expressions (``re``)."""

from __future__ import annotations

from src.contracts import ExtractionResult


def extract(text: str) -> ExtractionResult:
    """Extract contact data, skills, education and experience from resume text.

    Input:  resume text (str).
    Output: ExtractionResult with raw strings, no normalization.
    """
    raise NotImplementedError("Stage 1 is implemented in commits 3-5")
