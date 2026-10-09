"""HTML of the ResumeLens interface (pure functions, no server).

Everything that comes from the resume is escaped before it is written into the
page, and the stage 4 visualization is shown in a sandboxed ``iframe``.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from src.main import Analysis, PipelineResult
from src.vocabulary import Profile

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples" / "resumes"

_CSS = """
:root {
  --bg: #f5f5f7; --card: #ffffff; --text: #1d1d1f; --muted: #5f6368;
  --line: #dcdce1; --chip: #eceef3; --accent: #1f3a93; --accent-text: #ffffff;
  --ok: #14532d; --ok-bg: #dcfce7; --no: #5f6368; --no-bg: #eeeeee;
  --warn: #7a4b00; --warn-bg: #fff4d6; --bad: #8a1c1c; --bad-bg: #fde8e8;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #15161a; --card: #1e2026; --text: #ececf1; --muted: #a3a3ad;
    --line: #353841; --chip: #2a2d36; --accent: #9db4ff; --accent-text: #15161a;
    --ok: #bbf7d0; --ok-bg: #14532d; --no: #a3a3ad; --no-bg: #2a2d36;
    --warn: #ffe2a8; --warn-bg: #4a3600; --bad: #ffd0d0; --bad-bg: #5a1f1f;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 24px 16px 48px; background: var(--bg); color: var(--text);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  line-height: 1.5;
}
main { max-width: 960px; margin: 0 auto; }
h1 { margin: 0; font-size: 1.8rem; }
.tagline { margin: 2px 0 20px; color: var(--muted); }
h2 { margin: 0 0 12px; font-size: 1.1rem; }
h2 small { color: var(--muted); font-weight: 400; margin-left: 8px; }
.panel {
  margin-bottom: 16px; padding: 20px; background: var(--card);
  border: 1px solid var(--line); border-radius: 10px;
}
textarea {
  width: 100%; min-height: 190px; padding: 12px; resize: vertical;
  color: var(--text); background: var(--bg); border: 1px solid var(--line);
  border-radius: 8px; font: 0.9rem/1.5 ui-monospace, Consolas, monospace;
}
.actions { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px; margin-top: 12px; }
button {
  padding: 8px 20px; color: var(--accent-text); background: var(--accent);
  border: 0; border-radius: 8px; font: inherit; font-weight: 600; cursor: pointer;
}
.examples { color: var(--muted); font-size: 0.92rem; }
.examples a { margin-left: 10px; color: var(--accent); }
table { width: 100%; border-collapse: collapse; font-size: 0.93rem; }
th, td { padding: 6px 10px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }
th { width: 30%; color: var(--muted); font-weight: 600; }
tr:last-child th, tr:last-child td { border-bottom: 0; }
.chip {
  display: inline-block; margin: 2px 4px 2px 0; padding: 2px 10px; background: var(--chip);
  border-radius: 6px; font: 0.85rem ui-monospace, Consolas, monospace;
}
.dropped { color: var(--muted); font-style: italic; }
.arrow { color: var(--muted); padding: 0 6px; }
.note { margin: 12px 0 0; padding: 10px 14px; border-radius: 8px; font-size: 0.92rem; }
.warn { color: var(--warn); background: var(--warn-bg); }
.error { color: var(--bad); background: var(--bad-bg); }
.pending { color: var(--muted); background: var(--chip); }
.badge {
  display: inline-block; padding: 2px 12px; border: 1px solid currentColor;
  border-radius: 999px; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.04em;
}
.accepted { color: var(--ok); background: var(--ok-bg); }
.rejected { color: var(--no); background: var(--no-bg); }
pre {
  margin: 0 0 14px; padding: 12px; overflow-x: auto; background: var(--bg);
  border: 1px solid var(--line); border-radius: 8px; font-size: 0.85rem;
}
iframe { width: 100%; height: 720px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
footer { margin-top: 24px; color: var(--muted); font-size: 0.85rem; }
"""


def list_examples() -> dict[str, Path]:
    """Example resumes by name (the file name without extension), sorted."""
    return {path.stem: path for path in sorted(EXAMPLES_DIR.glob("*.txt"))}


_NONE = '<span class="dropped">none</span>'
_EMPTY = '<span class="dropped">empty</span>'
_NOT_FOUND = '<span class="dropped">not found</span>'


def _label(profile: Profile | str) -> str:
    value = profile.value if isinstance(profile, Profile) else profile
    return value.replace("_", " ").title()


def _chips(values: list[str]) -> str:
    return "".join(f'<span class="chip">{escape(v)}</span>' for v in values)


def _form(text: str) -> str:
    links = "".join(
        f'<a href="/?example={escape(stem, quote=True)}">{escape(_label(stem))}</a>'
        for stem in list_examples()
    )
    return (
        '<section class="panel"><form method="post" action="/">'
        '<label for="resume"><h2>Resume text</h2></label>'
        f'<textarea id="resume" name="resume" spellcheck="false">{escape(text)}</textarea>'
        '<div class="actions"><button type="submit">Analyze</button>'
        f'<span class="examples">Load an example:{links}</span></div>'
        "</form></section>"
    )


def _extraction(analysis: Analysis) -> str:
    e = analysis.extracted
    rows = [
        ("Name", escape(e.name) if e.name else _NOT_FOUND),
        ("Emails", _chips(e.emails)),
        ("Phones", _chips(e.phones)),
        ("Links", _chips(e.links)),
        ("Languages", _chips(e.languages)),
        ("Frameworks and libraries", _chips(e.frameworks)),
        ("Databases", _chips(e.databases)),
        ("Tools", _chips(e.tools)),
        ("Other qualifications", _chips(e.concepts)),
        ("Education", _chips(e.education)),
        (
            "Years of experience",
            "" if e.experience_years is None else escape(str(e.experience_years)),
        ),
        ("Jobs", _chips(e.experience)),
    ]
    body = "".join(
        f"<tr><th>{label}</th><td>{value or _NONE}</td></tr>" for label, value in rows
    )
    return (
        '<section class="panel"><h2>1. Extraction<small>regular expressions</small></h2>'
        f"<table>{body}</table>"
    ) + "</section>"


def _normalization(analysis: Analysis) -> str:
    if analysis.skill_trace:
        trace = "".join(
            "<tr>"
            f"<th>{escape(raw)}</th>"
            + (
                f'<td><span class="arrow">&rarr;</span>{_chips([token])}</td>'
                if token
                else '<td><span class="arrow">&rarr;</span>'
                '<span class="dropped">dropped (no canonical form)</span></td>'
            )
            + "</tr>"
            for raw, token in analysis.skill_trace
        )
        trace_table = f"<table>{trace}</table>"
    else:
        trace_table = '<p class="dropped">No technical skills were found.</p>'
    ordered = "".join(
        f"<tr><th>{escape(_label(profile))}</th><td>{_chips(tokens) or _EMPTY}</td></tr>"
        for profile, tokens in analysis.sorted_tokens.items()
    )
    warning = (
        ""
        if analysis.name_detected
        else '<p class="note warn">No name was found in the resume, so the candidate '
        f"is shown as &ldquo;{escape(analysis.name)}&rdquo;.</p>"
    )
    return (
        '<section class="panel"><h2>2. Normalization<small>finite-state transducers</small></h2>'
        f"{trace_table}"
        "<h2 style=\"margin-top:18px\">Sorted for each profile</h2>"
        f"<table>{ordered}</table>{warning}</section>"
    )


def _classification(result: PipelineResult | None, note: str | None) -> str:
    head = '<section class="panel"><h2>3. Recognition<small>finite automata</small></h2>'
    if result is None:
        return head + f'<p class="note pending">{escape(note or "Not available.")}</p></section>'
    rows = "".join(
        f"<tr><th>{escape(_label(profile))}</th><td>"
        f'<span class="badge {"accepted" if ok else "rejected"}">'
        f'{"ACCEPTED" if ok else "REJECTED"}</span></td></tr>'
        for profile, ok in result.classifications.items()
    )
    return head + f"<table>{rows}</table></section>"


def _candidate(result: PipelineResult | None, note: str | None, error: str | None) -> str:
    head = '<section class="panel"><h2>4. Candidate profile<small>context-free grammar (textX)</small></h2>'
    if error:
        return head + f'<p class="note error">{escape(error)}</p></section>'
    if result is None:
        return head + f'<p class="note pending">{escape(note or "Not available.")}</p></section>'
    return (
        head
        + f"<pre>{escape(result.dsl_text, quote=False)}</pre>"
        # sandbox="" turns scripts, forms and navigation off in the preview
        + f'<iframe title="Candidate visualization" sandbox="" srcdoc="{escape(result.html, quote=True)}"></iframe>'
        + "</section>"
    )


def render_page(
    text: str = "",
    analysis: Analysis | None = None,
    result: PipelineResult | None = None,
    pending_note: str | None = None,
    error: str | None = None,
) -> str:
    """The whole page.

    ``analysis`` (stages 1 and 2) and ``result`` (stages 3 and 4) are optional:
    with no analysis only the form is drawn; with an analysis but no result,
    stages 3 and 4 show ``pending_note`` (or ``error`` for stage 4).
    """
    sections = [_form(text)]
    if analysis is not None:
        sections += [
            _extraction(analysis),
            _normalization(analysis),
            _classification(result, pending_note),
            _candidate(result, pending_note, error),
        ]
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>ResumeLens</title>"
        f"<style>{_CSS}</style></head><body><main>"
        "<h1>ResumeLens</h1>"
        '<p class="tagline">Formal language-based resume screening</p>'
        + "".join(sections)
        + "<footer>ResumeLens checks whether the qualifications written in a resume "
        "satisfy a formally defined pattern. It does not rank candidates or make "
        "hiring decisions.</footer></main></body></html>\n"
    )
