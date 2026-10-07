"""Stage 1 - keeping the extracted information in a file."""

from __future__ import annotations

import json
from pathlib import Path

from src.contracts import ExtractionResult


def save_json(result: ExtractionResult, path: str | Path) -> Path:
    """Write the extraction result as UTF-8 JSON, creating folders if needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def load_json(path: str | Path) -> ExtractionResult:
    """Read back a file written by ``save_json``."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ExtractionResult(**data)
