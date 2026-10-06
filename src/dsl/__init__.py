"""Stage 4 - candidate profile DSL (textX) and HTML visualization."""

from __future__ import annotations

from src.contracts import CandidateProfile


def to_dsl_text(candidate: CandidateProfile) -> str:
    """Serialize a CandidateProfile into DSL source text.

    Input:  CandidateProfile.
    Output: text that must be accepted by the textX grammar.
    """
    raise NotImplementedError("Stage 4 is implemented in commits 7-9")


def validate(dsl_text: str):
    """Parse DSL text with textX.

    Input:  DSL source text.
    Output: the textX model. Raises a textX syntax/semantic error if invalid.
    """
    raise NotImplementedError("Stage 4 is implemented in commit 8")


def render_html(model) -> str:
    """Generate the HTML visualization of a validated model.

    Input:  validated textX model.
    Output: HTML document as a string.
    """
    raise NotImplementedError("Stage 4 is implemented in commit 9")
