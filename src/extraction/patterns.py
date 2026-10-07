"""Compiled regular expressions of stage 1, one per type of information.

Every pattern is explained in docs/extraction-regex.md. Patterns only
*detect* text; they never normalize it or decide anything about a profile.
Horizontal gaps use ``[ \\t]`` instead of ``\\s`` so a match never crosses a
line break.
"""

from __future__ import annotations

import re

# --- Contact information ----------------------------------------------------

EMAIL = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)

PHONE = re.compile(
    r"(?<![\w.])"
    r"(?:\+\d{1,3}[ .-]?)?"
    r"(?:"
    r"\(\d{1,4}\)[ .-]?\d{3}[ .-]?\d{4}"
    r"|\d{3}[ .-]\d{3}[ .-]\d{4}"
    r"|\d{3}[ .-]\d{7}"
    r"|\d{10}"
    r")"
    r"(?!\w)"
)

LINK = re.compile(
    r"(?:https?://|www\.)[^\s<>\"']+"
    r"|(?<![@\w.])(?:linkedin\.com|github\.com)/[\w./~%-]+"
)

_NAME_WORD = r"[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñü'’-]+"
_NAME_BODY = rf"{_NAME_WORD}(?:[ \t]+{_NAME_WORD}){{1,3}}"

NAME = re.compile(_NAME_BODY)

LABELED_NAME = re.compile(
    rf"^[ \t]*(?i:name|nombre)[ \t]*:[ \t]*({_NAME_BODY})[ \t]*$", re.M
)

# Words that look like a name on the first line but are resume headings.
NAME_STOPWORDS = frozenset(
    {"curriculum", "vitae", "resume", "résumé", "cv", "profile", "hoja", "vida"}
)

# --- Academic qualifications ------------------------------------------------

_DEGREE_KEYWORD = (
    r"(?:bachelor(?:'s|’s)?|master(?:'s|’s)?|doctorate|ph\.?d|b\.?sc|m\.?sc"
    r"|associate(?:'s|’s)?[ \t]+degree"
    r"|ingenier[íi]a|ingeniero|ingeniera|tecn[óo]logo|especializaci[óo]n"
    r"|maestr[íi]a|doctorado|licenciatura)"
)
_DEGREE_STOP = (
    r"(?:from|at|with|con|desde|universidad|university|instituto|institute"
    r"|college)"
)

DEGREE = re.compile(
    rf"(?<!scrum )\b{_DEGREE_KEYWORD}\b\.?"
    rf"(?:[ \t]+(?!{_DEGREE_STOP}\b)[^\W\d_]+){{0,5}}",
    re.I,
)

_CAP = r"[A-ZÁÉÍÓÚÑ][\w'’-]*"

INSTITUTION = re.compile(
    rf"\b(?:Universidad|Universidade|Instituto|Polit[ée]cnico|Pontificia|Escuela"
    rf"|Fundaci[óo]n)(?:[ \t]+(?:de|del|la|los|las|y)\b)?(?:[ \t]+{_CAP})+"
    rf"|\b(?:{_CAP}[ \t]+){{1,3}}(?:University|Institute|College)"
    rf"(?:[ \t]+of(?:[ \t]+{_CAP})+)?"
    rf"|\b(?:University|Institute|College)[ \t]+of(?:[ \t]+{_CAP})+"
)

# --- Technical skills -------------------------------------------------------
# These patterns recognize every spelling variant of a technology exactly as
# the candidate wrote it ("JS", "React.js", "Postgres"). Deciding that two
# spellings are the same technology is the job of stage 2.


def _skill_pattern(alternatives: list[str]) -> re.Pattern[str]:
    """Case-insensitive match of one alternative that is not part of a bigger
    word. Longer or more specific alternatives must come first."""
    body = "|".join(alternatives)
    return re.compile(rf"(?<![\w.+#])(?:{body})(?!\w)", re.I)


LANGUAGE = _skill_pattern(
    [
        r"java[ ]?script",
        r"ecmascript",
        r"type[ ]?script",
        r"js",
        r"ts",
        r"python3?",
        r"java",
        r"kotlin",
        r"c\+\+",
        r"c#",
        r"php",
        r"golang",
        r"(?-i:Swift|Rust|Ruby|Scala)",
    ]
)

FRAMEWORK = _skill_pattern(
    [
        r"react(?:[ .-]?js)?",
        r"angular(?:[ .-]?js)?",
        r"vue(?:[ .-]?js)?",
        r"next[ .-]?js",
        r"node[ .-]?js",
        r"express[ .-]?js",
        r"django",
        r"flask",
        r"fast[ ]?api",
        r"spring[ -]?boot",
        r"pandas",
        r"num[ ]?py",
        r"sci[ -]?py",
        r"scikit[ -]?learn",
        r"sklearn",
        r"tensor[ ]?flow",
        r"py[ ]?torch",
        r"keras",
        r"matplotlib",
    ]
)

DATABASE = _skill_pattern(
    [
        r"postgre[ ]?sql",
        r"postgres",
        r"my[ ]?sql",
        r"maria[ ]?db",
        r"mongo[ ]?db",
        r"mongo",
        r"sql[ ]?server",
        r"sqlite",
        r"no[ -]?sql",
        r"redis",
        r"firebase",
        r"sql",
    ]
)

TOOL = _skill_pattern(
    [
        r"git[ ]?hub",
        r"git[ ]?lab",
        r"bit[ ]?bucket",
        r"git",
        r"docker",
        r"kubernetes",
        r"k8s",
        r"jenkins",
        r"jira",
        r"jupyter(?:[ ]?(?:notebooks?|lab))?",
        r"postman",
        r"linux",
        r"aws",
        r"azure",
        r"gcp",
        r"npm",
        r"webpack",
        r"maven",
        r"gradle",
        r"ci/cd",
    ]
)

# Other qualifications that profiles ask for and that are not a tool or a
# library: practices and areas of knowledge.
CONCEPT = _skill_pattern(
    [
        r"rest(?:ful)?[ -]?apis?",
        r"restful(?:[ ]web)?[ ]services?",
        r"restful",
        r"graphql",
        r"microservices?",
        r"machine[ -]learning(?:[ ]models?)?(?:[ ]development)?",
        r"deep[ -]learning",
        r"predictive[ ]model(?:s|ing)?",
        r"data[ -]processing(?:[ ]pipelines?)?",
        r"(?-i:ML)",
    ]
)

# --- Professional experience ------------------------------------------------

_NUMBER_WORDS = r"one|two|three|four|five|six|seven|eight|nine|ten"

# "3 years of experience", "2+ years of professional experience",
# "five años de experiencia". Group 1 is the number as written.
EXPERIENCE_YEARS = re.compile(
    rf"(?<![\w.])(\d{{1,2}}(?:[.,]\d)?|{_NUMBER_WORDS})\+?[ \t]*"
    r"(?:years?|yrs?|años?)[ \t]+"
    r"(?:(?:of|de)[ \t]+)?"
    r"(?:(?:professional|work|relevant|industry|hands-on|profesional)[ \t]+)?"
    r"(?:experience|experiencia)(?!\w)",
    re.I,
)

# The sentence that follows the years of experience, up to a period, a
# semicolon or the end of the line: "3 years of experience developing web
# applications".
EXPERIENCE_STATEMENT = re.compile(
    EXPERIENCE_YEARS.pattern
    + r"(?:[ \t]+(?:in|with|developing|building|using|as|working[ \t]+(?:in|with|on)"
    r"|en|con|desarrollando)[ \t]+[^.\n;]+)?",
    re.I,
)

_DATE_RANGE = (
    r"(?:19|20)\d{2}[ \t]*[-–—][ \t]*"
    r"(?:(?:19|20)\d{2}|(?i:present|current|presente|actualidad|actual))"
)

# A job: optional capitalized words + a role word, optionally "at Company"
# and a date range. "Senior Backend Developer at Acme Corp (2020 - 2023)".
JOB = re.compile(
    rf"\b(?:{_CAP}[ \t]+){{0,3}}"
    r"(?:Developer|Engineer|Analyst|Intern|Manager|Consultant|Architect|Scientist"
    r"|Administrator|Designer|Desarrolladora?|Analista|Practicante|Pasante"
    r"|Consultor|Arquitecto|Cient[ií]fico)\b"
    rf"(?:[ \t]+(?:at|en|@)[ \t]+{_CAP}(?:[ \t]+{_CAP}){{0,3}})?"
    rf"(?:[ \t]*[,(|–—-]*[ \t]*{_DATE_RANGE}\)?)?"
)
