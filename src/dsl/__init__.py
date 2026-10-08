"""Stage 4 - candidate profile DSL (textX) and HTML visualization."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXSyntaxError

from src.contracts import CandidateProfile
from src.dsl import semantics
from src.dsl.errors import DSLError, DSLSemanticError, DSLSyntaxError
from src.dsl.html import render_html, save_html
from src.vocabulary import Profile

__all__ = [
    "DSLError",
    "DSLSemanticError",
    "DSLSyntaxError",
    "parse",
    "render_html",
    "save_html",
    "to_dsl_text",
    "validate",
]

GRAMMAR = Path(__file__).with_name("candidate.tx")


@lru_cache(maxsize=1)
def _metamodel():
    metamodel = metamodel_from_file(str(GRAMMAR))
    # The grammar keeps the quotes of a text; the model gets the bare string.
    metamodel.register_obj_processors(
        {"Text": lambda text: text[1:-1], "Years": int}
    )
    return metamodel


def _text(value: str) -> str:
    """Make a string safe to put between the quotes of the DSL."""
    return " ".join(value.replace('"', "'").split())


def to_dsl_text(candidate: CandidateProfile) -> str:
    """Serialize a CandidateProfile into DSL source text.

    Input:  CandidateProfile.
    Output: text that the grammar accepts (the semantic rules still apply).
            All four profiles are listed; a profile missing from the
            classifications is written as REJECTED.
    """
    lines = [f'candidate "{_text(candidate.name)}" {{']

    contact = (
        [f'email: "{_text(e)}"' for e in candidate.emails]
        + [f'phone: "{_text(p)}"' for p in candidate.phones]
        + [f'link: "{_text(link)}"' for link in candidate.links]
    )
    if contact:
        lines += ["  contact {", *(f"    {item}" for item in contact), "  }"]

    if candidate.experience_years is not None or candidate.experience:
        lines.append("  experience {")
        if candidate.experience_years is not None:
            lines.append(f"    years: {candidate.experience_years}")
        lines += [f'    job: "{_text(job)}"' for job in candidate.experience]
        lines.append("  }")

    if candidate.education:
        lines.append("  education {")
        lines += [f'    study: "{_text(s)}"' for s in candidate.education]
        lines.append("  }")

    lines.append(f"  skills {{ {', '.join(candidate.skills)} }}")

    lines.append("  results {")
    for profile in Profile:
        status = "ACCEPTED" if candidate.classifications.get(profile) else "REJECTED"
        lines.append(f"    {profile.value}: {status}")
    lines += ["  }", "}", ""]
    return "\n".join(lines)


def parse(dsl_text: str):
    """Check only the lexical and syntactic rules (the grammar).

    Raises DSLSyntaxError with the position of the problem.
    """
    try:
        return _metamodel().model_from_str(dsl_text)
    except TextXSyntaxError as error:
        raise DSLSyntaxError(error.message, error.line, error.col) from None


def validate(dsl_text: str):
    """Parse DSL text with textX and apply the semantic rules S1 to S6.

    Input:  DSL source text.
    Output: the validated textX model.
    Raises: DSLSyntaxError (grammar) or DSLSemanticError (semantic rules);
            both are DSLError.
    """
    model = parse(dsl_text)
    semantics.check(model)
    return model
