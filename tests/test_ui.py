import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from src.main import analyze, run_stages
from src.ui.pages import list_examples, render_page
from src.ui.server import MAX_BODY_BYTES, build_page, make_server

RESUMES = Path(__file__).resolve().parents[1] / "examples" / "resumes"
WEDNESDAY = (RESUMES / "wednesday_addams.txt").read_text(encoding="utf-8")


# --- pages (no server) --------------------------------------------------------


def test_the_empty_page_has_the_form_and_the_examples_only():
    page = render_page()
    assert '<form method="post" action="/">' in page
    assert '<textarea id="resume" name="resume"' in page
    assert "Extraction" not in page
    for stem in list_examples():
        assert f"/?example={stem}" in page


def test_every_example_resume_is_listed():
    assert set(list_examples()) == {p.stem for p in RESUMES.glob("*.txt")}
    assert len(list_examples()) == 6


def test_the_page_shows_every_stage(stub_classifier):
    result = run_stages(WEDNESDAY, stub_classifier)
    page = render_page(WEDNESDAY, result.analysis, result)
    for title in ("1. Extraction", "2. Normalization", "3. Recognition", "4. Candidate profile"):
        assert title in page
    # stage 1: strings as written
    assert "React.js" in page and "Postgres" in page
    # stage 2: from the raw string to the token, and the order of each profile
    assert "NODE_JS" in page and "POSTGRESQL" in page
    assert "Full Stack Developer" in page and "Machine Learning Engineer" in page
    # stage 3
    assert "ACCEPTED" in page and "REJECTED" in page
    # stage 4: the DSL text and the visualization
    assert 'candidate "Wednesday Addams" {' in page
    assert "<iframe" in page and 'sandbox=""' in page


def test_stage_3_and_4_show_a_note_while_stage_3_is_missing():
    page = render_page(WEDNESDAY, analyze(WEDNESDAY), pending_note="Stage 3 is missing")
    assert page.count("Stage 3 is missing") == 2  # in stage 3 and in stage 4
    assert "2. Normalization" in page
    assert "<iframe" not in page


def test_an_error_of_stage_4_is_shown_in_that_stage():
    page = render_page(WEDNESDAY, analyze(WEDNESDAY), error="S1 unknown skill X")
    assert "S1 unknown skill X" in page
    assert "<iframe" not in page


def test_dropped_strings_are_shown_as_dropped():
    text = (RESUMES / "carlos_ruiz.txt").read_text(encoding="utf-8")
    page = render_page(text, analyze(text))
    assert page.count("dropped (no canonical form)") == 3  # CI/CD, Jenkins, microservices


def test_a_missing_name_is_explained():
    text = "3 years of experience in web development.\nSkills: Python, Git.\n"
    page = render_page(text, analyze(text))
    assert "No name was found" in page
    assert "Unknown candidate" in page


def test_a_resume_with_no_skills_is_shown_without_errors(stub_classifier):
    text = (RESUMES / "sofia_nunez.txt").read_text(encoding="utf-8")
    page = build_page(text, stub_classifier)
    assert "No technical skills were found." in page
    assert "<iframe" in page


# --- escaping ----------------------------------------------------------------

HOSTILE = (
    'Eve <script>alert("x")</script> Mallory\n'
    "Skills: JS, <img src=x onerror=alert(1)>, Git.\n"
    "</textarea><script>alert(2)</script>\n"
)


def test_text_from_the_resume_is_escaped(stub_classifier):
    page = build_page(HOSTILE, stub_classifier)
    assert "<script>" not in page
    assert "<img src=x" not in page
    assert "&lt;script&gt;" in page


def test_the_visualization_is_escaped_inside_the_iframe_attribute(stub_classifier):
    page = build_page(HOSTILE, stub_classifier)
    start = page.index('srcdoc="') + len('srcdoc="')
    attribute = page[start : page.index('"', start)]
    assert "<" not in attribute and ">" not in attribute
    assert attribute.startswith("&lt;!DOCTYPE html&gt;")  # the whole page, escaped


# --- build_page ----------------------------------------------------------------


def test_build_page_with_blank_text_gives_the_form():
    assert "1. Extraction" not in build_page("   \n ")


def test_build_page_without_stage_3_shows_stages_1_and_2(stage_3_ready):
    if stage_3_ready:
        pytest.skip("stage 3 is implemented")
    page = build_page(WEDNESDAY)
    assert "1. Extraction" in page and "2. Normalization" in page
    assert "not implemented" in page
    assert "<iframe" not in page


def test_build_page_accepts_a_classifier_with_missing_profiles():
    # the DSL writes a missing profile as REJECTED, so the profile is still valid
    assert "<iframe" in build_page(WEDNESDAY, lambda tokens: {})


# --- server ------------------------------------------------------------------


@pytest.fixture
def server(stub_classifier):
    httpd = make_server("127.0.0.1", 0, stub_classifier)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=5)


def fetch(url, data=None):
    request = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, dict(response.headers), response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read().decode("utf-8")


def test_get_the_form(server):
    status, headers, body = fetch(server + "/")
    assert status == 200
    assert headers["Content-Type"] == "text/html; charset=utf-8"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "<textarea" in body and "1. Extraction" not in body


def test_post_a_resume(server):
    data = urllib.parse.urlencode({"resume": WEDNESDAY}).encode()
    status, _, body = fetch(server + "/", data)
    assert status == 200
    assert "NODE_JS" in body
    assert "ACCEPTED" in body
    assert "Wednesday Addams" in body


def test_post_text_with_accents_and_symbols(server):
    text = "Laura Gómez Ramírez\nHabilidades: python, C++, Docker\n"
    data = urllib.parse.urlencode({"resume": text}).encode()
    status, _, body = fetch(server + "/", data)
    assert status == 200
    assert "CPP" in body and "PYTHON" in body
    assert "Gómez" in body


def test_get_an_example(server):
    status, _, body = fetch(server + "/?example=mary_jane_watson")
    assert status == 200
    assert "Mary Jane Watson" in body
    assert "SCIKIT_LEARN" in body


def test_an_unknown_example_or_a_path_is_not_found(server):
    for query in ("nothing", "../README", "..%2F..%2Fetc%2Fpasswd", "wednesday_addams.txt"):
        status, _, body = fetch(f"{server}/?example={query}")
        assert status == 404, query
        assert "root:" not in body


def test_other_paths_are_not_found(server):
    assert fetch(server + "/other")[0] == 404
    assert fetch(server + "/other", b"resume=x")[0] == 404


def test_a_body_that_is_too_big_is_refused(server):
    data = b"resume=" + b"a" * (MAX_BODY_BYTES + 1)
    assert fetch(server + "/", data)[0] == 413


def test_a_post_without_the_field_gives_the_form(server):
    status, _, body = fetch(server + "/", b"other=1")
    assert status == 200
    assert "1. Extraction" not in body
