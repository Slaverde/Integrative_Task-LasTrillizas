"""Data contracts exchanged between the four ResumeLens stages.

    text --(1 extraction)--> ExtractionResult
         --(2 normalization)--> list[str] canonical tokens, sorted per profile
         --(3 classification)--> dict[Profile, bool]
         --(4 DSL)--> CandidateProfile -> DSL text -> HTML
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from src.vocabulary import Profile


@dataclass
class ExtractionResult:
    """Stage 1 output: raw strings exactly as written in the resume.

    Nothing is normalized or interpreted here; order of appearance is kept.
    """

    name: str | None = None
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    databases: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience_years: int | None = None
    experience: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Plain dictionary, ready to be saved as JSON."""
        return asdict(self)

    def raw_skills(self) -> list[str]:
        """All qualification strings that stage 2 must normalize."""
        return (
            self.languages
            + self.frameworks
            + self.databases
            + self.tools
            + self.concepts
        )


@dataclass
class CandidateProfile:
    """Stage 4 input: everything the DSL needs to describe a candidate."""

    name: str
    emails: list[str]
    phones: list[str]
    experience_years: int | None
    education: list[str]
    skills: list[str]  # canonical tokens, already sorted
    classifications: dict[Profile, bool]
    links: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)  # job entries

    def accepted_profiles(self) -> list[Profile]:
        return [p for p, ok in self.classifications.items() if ok]
