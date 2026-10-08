"""``python -m src.dsl profile.rl page.html``: validate a profile and render it."""

from __future__ import annotations

import sys
from pathlib import Path

from src.dsl import DSLError, render_html, save_html, validate


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m src.dsl <profile.rl> <output.html>", file=sys.stderr)
        return 2
    try:
        model = validate(Path(argv[0]).read_text(encoding="utf-8"))
    except DSLError as error:
        print(f"invalid candidate profile: {error}", file=sys.stderr)
        return 1
    print(save_html(render_html(model), argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
