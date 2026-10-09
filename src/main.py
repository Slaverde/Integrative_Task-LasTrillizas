"""ResumeLens entry point: runs the four stages in order.

    text --extract--> ExtractionResult --normalize--> tokens
         --sort_for_profile (x4)--> sorted tokens per profile
         --classify_all--> {profile: accepted?}
         --to_dsl_text / validate / render_html--> HTML

The work is split in two so that a caller (the UI, for example) can show the
first two stages even if the third one fails:

* ``analyze``  stages 1 and 2 (extraction, normalization, sorting);
* ``complete`` stages 3 and 4 (classification, DSL, HTML).

``run_stages`` runs both and ``run_pipeline`` returns only the HTML.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.classification import classify_all
from src.contracts import CandidateProfile, ExtractionResult
from src.dsl import render_html, to_dsl_text, validate
from src.extraction import extract
from src.normalization import (
    normalize,
    normalize_skill,
    sort_by_vocabulary,
    sort_for_profile,
)
from src.vocabulary import Profile

UNKNOWN_NAME = "Unknown candidate"
"""Name used when stage 1 finds none (decision D7, see docs/contracts.md)."""

Classifier = Callable[[list[str]], dict[Profile, bool]]
"""Same signature as ``classify_all``."""


@dataclass
class Analysis:
    """Output of stages 1 and 2."""

    extracted: ExtractionResult
    skill_trace: list[tuple[str, str | None]]
    """Every raw skill string with its canonical token (None if it was dropped)."""
    tokens: list[str]
    """Canonical tokens, without duplicates, in order of appearance."""
    sorted_tokens: dict[Profile, list[str]]
    """The tokens in the order of each of the four profiles."""

    @property
    def name_detected(self) -> bool:
        return bool(self.extracted.name and self.extracted.name.strip())

    @property
    def name(self) -> str:
        return self.extracted.name.strip() if self.name_detected else UNKNOWN_NAME


@dataclass
class PipelineResult:
    """Output of the four stages."""

    analysis: Analysis
    classifications: dict[Profile, bool]
    candidate: CandidateProfile
    dsl_text: str
    html: str


def analyze(text: str) -> Analysis:
    """Stages 1 and 2: resume text -> raw strings, tokens and sorted tokens.

    The same ``sort_for_profile`` runs for the four profiles; only the order
    stored in ``vocabulary.PROFILE_ORDER`` differs.
    """
    extracted = extract(text)
    tokens = normalize(extracted)
    return Analysis(
        extracted=extracted,
        skill_trace=[(raw, normalize_skill(raw)) for raw in extracted.raw_skills()],
        tokens=tokens,
        sorted_tokens={p: sort_for_profile(tokens, p) for p in Profile},
    )


def complete(analysis: Analysis, classifier: Classifier | None = None) -> PipelineResult:
    """Stages 3 and 4: classify, build the candidate profile, validate, render.

    ``classifier`` defaults to ``classify_all``. It receives the canonical
    tokens (it sorts them for each profile by itself). Raises
    NotImplementedError while stage 3 is not implemented, and the DSL errors
    of stage 4 if the candidate profile is not valid.
    """
    classifications = (classifier or classify_all)(analysis.tokens)
    extracted = analysis.extracted
    candidate = CandidateProfile(
        name=analysis.name,
        emails=extracted.emails,
        phones=extracted.phones,
        experience_years=extracted.experience_years,
        education=extracted.education,
        skills=sort_by_vocabulary(analysis.tokens),
        classifications=classifications,
        links=extracted.links,
        experience=extracted.experience,
    )
    dsl_text = to_dsl_text(candidate)
    html = render_html(validate(dsl_text))
    return PipelineResult(analysis, classifications, candidate, dsl_text, html)


def run_stages(text: str, classifier: Classifier | None = None) -> PipelineResult:
    """Resume text -> every intermediate result of the four stages."""
    return complete(analyze(text), classifier)


def run_pipeline(text: str, classifier: Classifier | None = None) -> str:
    """Resume text -> HTML visualization of the validated candidate profile."""
    return run_stages(text, classifier).html
