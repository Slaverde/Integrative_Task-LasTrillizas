"""Local web server of the interface (standard library only).

    python -m src.ui                 # http://127.0.0.1:8000
    python -m src.ui --port 9000 --open

It listens on the local machine only by default. A resume is pasted in the
form (POST) or loaded from ``examples/resumes`` (GET ``/?example=name``).
"""

from __future__ import annotations

import argparse
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit

from src.dsl import DSLError
from src.main import Classifier, analyze, complete
from src.ui.pages import list_examples, render_page

MAX_BODY_BYTES = 200_000
"""A resume is a few kilobytes; a bigger request is refused."""

_PENDING_STAGE_3 = (
    "Stage 3 (finite automata) is not implemented in this version, so the "
    "profiles cannot be classified yet."
)


def build_page(text: str, classifier: Classifier | None = None) -> str:
    """Resume text -> the page with every stage that could be computed."""
    if not text.strip():
        return render_page(text)
    analysis = analyze(text)
    try:
        result = complete(analysis, classifier)
    except NotImplementedError:
        return render_page(text, analysis, pending_note=_PENDING_STAGE_3)
    except DSLError as error:
        return render_page(text, analysis, error=f"The candidate profile is not valid: {error}")
    return render_page(text, analysis, result)


def make_handler(classifier: Classifier | None = None) -> type[BaseHTTPRequestHandler]:
    """Request handler class that uses ``classifier`` (default: ``classify_all``)."""

    class Handler(BaseHTTPRequestHandler):
        server_version = "ResumeLens"

        def log_message(self, format: str, *args) -> None:  # noqa: A002
            pass  # keep the terminal quiet

        def _send(self, status: HTTPStatus, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _not_found(self, message: str = "Not found") -> None:
            self._send(HTTPStatus.NOT_FOUND, render_page() + f"<!-- {message} -->")

        def do_GET(self) -> None:  # noqa: N802
            url = urlsplit(self.path)
            if url.path != "/":
                return self._not_found()
            names = parse_qs(url.query).get("example", [])
            if not names:
                return self._send(HTTPStatus.OK, render_page())
            path = list_examples().get(names[0])  # only known names, never a path
            if path is None:
                return self._not_found("Unknown example")
            text = path.read_text(encoding="utf-8")
            self._send(HTTPStatus.OK, build_page(text, classifier))

        def do_POST(self) -> None:  # noqa: N802
            if urlsplit(self.path).path != "/":
                return self._not_found()
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                return self._send(HTTPStatus.BAD_REQUEST, render_page())
            if length < 0 or length > MAX_BODY_BYTES:
                return self._send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, render_page())
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            text = parse_qs(body, keep_blank_values=True).get("resume", [""])[0]
            self._send(HTTPStatus.OK, build_page(text, classifier))

    return Handler


def make_server(
    host: str = "127.0.0.1", port: int = 8000, classifier: Classifier | None = None
) -> HTTPServer:
    """A server ready to ``serve_forever`` (port 0 picks a free port)."""
    return HTTPServer((host, port), make_handler(classifier))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.ui", description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--open", action="store_true", help="open the browser")
    args = parser.parse_args(argv)
    try:
        server = make_server(args.host, args.port)
    except OSError as error:
        print(f"cannot start the server on {args.host}:{args.port}: {error}")
        return 1
    url = f"http://{args.host}:{server.server_port}/"
    print(f"ResumeLens is running at {url} (Ctrl+C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()
    return 0
