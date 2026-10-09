"""``python -m src.ui``: start the local web interface."""

from __future__ import annotations

import sys

from src.ui.server import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
