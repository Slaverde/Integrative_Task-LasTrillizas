"""Stage 4 - HTML visualization of a validated candidate profile.

The page is one self-contained file (no external fonts, scripts or images), so
it can be opened from disk, attached to an e-mail or printed. Every value that
comes from the resume is escaped before it is written into the page.
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

from src.vocabulary import TOKENS

_BARE_LINK = re.compile(r"(?:www\.|linkedin\.com/|github\.com/)", re.I)

_CSS = """
:root {
  --bg: #f4f4f4; --card: #ffffff; --text: #1d1d1f; --muted: #5c5c63;
  --line: #d9d9de; --chip: #eceef3; --accent: #1f3a93;
  --ok: #14532d; --ok-bg: #dcfce7; --no: #5c5c63; --no-bg: #eeeeee;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #15161a; --card: #1e2026; --text: #ececf1; --muted: #a0a0aa;
    --line: #353841; --chip: #2a2d36; --accent: #9db4ff;
    --ok: #bbf7d0; --ok-bg: #14532d; --no: #a0a0aa; --no-bg: #2a2d36;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 24px 16px; background: var(--bg); color: var(--text);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  line-height: 1.5;
}
.card {
  max-width: 860px; margin: 0 auto; padding: 32px; background: var(--card);
  border: 1px solid var(--line); border-radius: 10px;
}
header { border-bottom: 2px solid var(--text); margin-bottom: 24px; }
h1 { margin: 0 0 4px; font-size: 1.9rem; overflow-wrap: anywhere; }
header p, .note { margin: 0 0 16px; color: var(--muted); }
section { margin-bottom: 28px; }
h2 {
  margin: 0 0 12px; padding-bottom: 6px; font-size: 1.1rem;
  border-bottom: 1px solid var(--line);
}
ul { margin: 0; padding-left: 20px; }
li { margin-bottom: 4px; overflow-wrap: anywhere; }
dl { margin: 0; display: grid; grid-template-columns: max-content 1fr; gap: 6px 16px; }
dt { font-weight: 600; }
dd { margin: 0; overflow-wrap: anywhere; }
a { color: var(--accent); }
.skills { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; }
.skill {
  margin: 0; padding: 6px 12px; background: var(--chip);
  border-radius: 6px; font-family: ui-monospace, Consolas, monospace; font-size: 0.9rem;
}
.results { display: grid; gap: 12px; }
.result {
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px;
  padding: 14px 16px; border: 1px solid var(--line); border-radius: 8px;
}
.result h3 { margin: 0; flex: 1 1 220px; font-size: 1rem; }
.result p { margin: 0; flex: 1 1 100%; color: var(--muted); font-size: 0.92rem; }
.badge {
  padding: 3px 12px; border-radius: 999px; border: 1px solid currentColor;
  font-size: 0.85rem; font-weight: 700; letter-spacing: 0.04em;
}
.accepted .badge { color: var(--ok); background: var(--ok-bg); }
.rejected .badge { color: var(--no); background: var(--no-bg); }
.summary { margin: 0 0 14px; font-weight: 600; }
footer { margin-top: 8px; padding-top: 12px; border-top: 1px solid var(--line); }
footer p { margin: 0; color: var(--muted); font-size: 0.85rem; }
@media (max-width: 560px) {
  .card { padding: 20px; }
  dl { grid-template-columns: 1fr; gap: 0; }
  dt { margin-top: 8px; }
}
@media print {
  body { background: #fff; padding: 0; }
  .card { border: 0; }
}
"""


def _label(profile: str) -> str:
    """FULL_STACK_DEVELOPER -> Full Stack Developer."""
    return profile.replace("_", " ").title()


def _link_href(value: str) -> str | None:
    """Safe address for a link, or None when it must be shown as plain text."""
    if re.match(r"https?://", value, re.I):
        return value
    if _BARE_LINK.match(value):
        return "https://" + value
    return None


def _contact_value(kind: str, value: str) -> str:
    text = escape(value)
    if kind == "Email":
        return f'<a href="mailto:{escape(value, quote=True)}">{text}</a>'
    if kind == "Phone":
        number = re.sub(r"[^\d+]", "", value)
        return f'<a href="tel:{escape(number, quote=True)}">{text}</a>'
    href = _link_href(value)
    if href:
        return f'<a href="{escape(href, quote=True)}" rel="noopener noreferrer">{text}</a>'
    return text


def _contact_section(model) -> str:
    if not model.contact:
        return ""
    names = {"Email": "Email", "Phone": "Phone", "Link": "Link"}
    rows = []
    for item in model.contact.items:
        kind = type(item).__name__
        rows.append(f"<dt>{names[kind]}</dt><dd>{_contact_value(kind, item.value)}</dd>")
    return f"<section><h2>Contact</h2><dl>{''.join(rows)}</dl></section>"


def _experience_section(model) -> str:
    experience = model.experience
    if not experience:
        return ""
    parts = ["<section><h2>Experience</h2>"]
    if experience.years is not None:
        unit = "year" if experience.years == 1 else "years"
        parts.append(f"<p><strong>{experience.years} {unit}</strong> of experience</p>")
    if experience.jobs:
        items = "".join(f"<li>{escape(job.text)}</li>" for job in experience.jobs)
        parts.append(f"<ul>{items}</ul>")
    parts.append("</section>")
    return "".join(parts)


def _education_section(model) -> str:
    if not model.education:
        return ""
    items = "".join(f"<li>{escape(s.text)}</li>" for s in model.education.studies)
    return f"<section><h2>Education</h2><ul>{items}</ul></section>"


def _skills_section(model) -> str:
    if not model.skills.items:
        body = '<p class="note">No technical skills were recognized in the resume.</p>'
    else:
        chips = []
        for token in model.skills.items:
            category = TOKENS[token].value.replace("_", " ").title() if token in TOKENS else ""
            title = f' title="{escape(category, quote=True)}"' if category else ""
            chips.append(f'<li class="skill"{title}>{escape(token)}</li>')
        body = f'<ul class="skills">{"".join(chips)}</ul>'
    return f"<section><h2>Normalized Technical Skills</h2>{body}</section>"


def _results_section(model) -> str:
    accepted = [r.profile for r in model.results.items if r.status == "ACCEPTED"]
    if accepted:
        names = ", ".join(_label(p) for p in accepted)
        summary = f"Accepted profiles: {escape(names)}"
    else:
        summary = "No qualification pattern was satisfied."
    cards = []
    for result in model.results.items:
        ok = result.status == "ACCEPTED"
        label = escape(_label(result.profile))
        verdict = "satisfy" if ok else "do not satisfy"
        cards.append(
            f'<article class="result {"accepted" if ok else "rejected"}">'
            f"<h3>{label}</h3>"
            f'<span class="badge">{result.status}</span>'
            f"<p>The normalized qualifications {verdict} an accepted {label} pattern.</p>"
            f"</article>"
        )
    return (
        "<section><h2>Qualification Evaluation</h2>"
        f'<p class="summary">{summary}</p>'
        f'<div class="results">{"".join(cards)}</div></section>'
    )


def render_html(model) -> str:
    """Generate the HTML visualization of a validated model.

    Input:  validated textX model (the result of ``validate``).
    Output: a complete HTML document as a string.
    """
    name = escape(model.name)
    sections = [
        _contact_section(model),
        _experience_section(model),
        _education_section(model),
        _skills_section(model),
        _results_section(model),
    ]
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="generator" content="ResumeLens">\n'
        f"<title>{name} - ResumeLens</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '<main class="card">\n'
        f"<header><h1>{name}</h1>"
        "<p>Candidate profile generated by ResumeLens</p></header>\n"
        + "\n".join(s for s in sections if s)
        + "\n<footer><p>ResumeLens checks whether the qualifications written in a "
        "resume satisfy a formally defined pattern. It does not rank candidates or "
        "make hiring decisions.</p></footer>\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )


def save_html(html: str, path: str | Path) -> Path:
    """Write the page as UTF-8, creating folders if needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target
