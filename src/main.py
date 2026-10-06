"""ResumeLens entry point: runs the four stages in order."""

from __future__ import annotations

from src.classification import classify_all
from src.contracts import CandidateProfile
from src.dsl import render_html, to_dsl_text, validate
from src.extraction import extract
from src.normalization import normalize


def run_pipeline(text: str) -> str:
    """Resume text -> HTML visualization of the validated candidate profile."""
    extracted = extract(text)
    tokens = normalize(extracted)
    classifications = classify_all(tokens)
    candidate = CandidateProfile(
        name=extracted.name or "",
        emails=extracted.emails,
        phones=extracted.phones,
        experience_years=extracted.experience_years,
        education=extracted.education,
        skills=tokens,
        classifications=classifications,
    )
    model = validate(to_dsl_text(candidate))
    return render_html(model)
