# Integration - Test cases and scenarios

Tests: `tests/test_integration.py`, `tests/test_pipeline.py`, `tests/test_ui.py`
(run with `python -m pytest`). Input resumes: `examples/resumes/`.

These tests check the stages working together: the four profiles through the
same code, the pipeline from text to HTML, and the interface. The tests that
need stage 3 (the automata) skip themselves while `classify_all` raises
`NotImplementedError` and start running when it is implemented; no test has to
be edited. Until then a stand-in classifier (`stub_classifier` in
`tests/conftest.py`) replaces stage 3.

## 1. Stages 1 and 2 on the four profiles

| ID | Scenario | Expected |
|---|---|---|
| I1 | `wednesday_addams.txt` and `mary_jane_watson.txt`, sorted for Full Stack and Machine Learning Engineer (the profiles of the assignment) | the exact sequences written in the test; for Full Stack, `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`. The two provisional profiles have no hard-coded sequence, so a change of their order does not break the tests (I3 covers them) |
| I2 | `ana_torres.txt` for Full Stack | `JAVASCRIPT, TYPESCRIPT, REACT, NODE_JS, POSTGRESQL, MONGODB, GIT, REST_API, GRAPHQL` |
| I3 | every example resume, every profile | the sequence is a reordering of the same tokens, without duplicates, with the categories in the order of the profile |
| I4 | a spy on `sort_for_profile` while `analyze` runs | called once per profile, always the same function |
| I5 | the skills line of each resume shuffled 15 times | the sequences of the 4 profiles do not change |
| I6 | the 120 orders of `JS, React.js, NodeJS, Postgres, Git` | one sequence per profile |

## 2. Pipeline with a stand-in for stage 3

| ID | Scenario | Expected |
|---|---|---|
| I7 | the 6 example resumes through `run_stages` | the DSL text validates (rules S1 to S6), lists the same skills as the candidate, has the 4 profiles, and the HTML is generated |
| I8 | `laura_gomez.txt` | `GIT` appears (from `github`, D3) and `MACHINE_LEARNING` (from `modelos predictivos`, D4) |
| I9 | the same skills written in two ways (`JS, React.js, NodeJS, Postgres, Git` and `Javascript, ReactJS, Node js, PostgreSQL, github`) | exactly the same HTML |
| I10 | a resume with no name | the candidate is `Unknown candidate`, the DSL is valid, the UI warns about it |
| I11 | the classifier receives the canonical tokens | the stand-in records `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` |
| I12 | a classifier that omits profiles | the DSL writes them as `REJECTED` |
| I13 | `run_pipeline` without a classifier | uses `classify_all` (checked by replacing it) |

## 3. With the real stage 3 (skipped until it exists)

| ID | Scenario | Expected |
|---|---|---|
| I14 | `wednesday_addams.txt`, `ana_torres.txt` | `FULL_STACK_DEVELOPER` accepted |
| I15 | `mary_jane_watson.txt` | `MACHINE_LEARNING_ENGINEER` accepted |
| I16 | `sofia_nunez.txt` | no profile accepted |
| I17 | the 120 orders of the tokens of scenario I1 | `classify_all` gives the same answer |

`carlos_ruiz.txt` and `laura_gomez.txt` are not checked against a profile here
because the two team profiles are provisional (see `examples/README.md`).

## 4. Interface

| ID | Scenario | Expected |
|---|---|---|
| U1 | the form with no resume | form and example links only |
| U2 | a resume with a classifier | the four stages, the DSL text and a sandboxed `iframe` with the HTML |
| U3 | stage 3 missing | stages 1 and 2 shown, a note in stages 3 and 4, no `iframe` |
| U4 | dropped strings (`carlos_ruiz.txt`) | shown as "dropped (no canonical form)" |
| U5 | a resume with `<script>`, `<img onerror>` and `</textarea>` | nothing is written unescaped, in the page or in the `iframe` |
| U6 | `GET /?example=name` | loads that example; unknown names and paths such as `../README` give 404 |
| U7 | `POST` a resume with accents and `C++` | `CPP` and `PYTHON` are shown, accents are kept |
| U8 | a body over 200 KB, a path other than `/` | 413 and 404 |

## 5. How to run only these

```bash
python -m pytest tests/test_integration.py tests/test_pipeline.py tests/test_ui.py -rs
```

`-rs` prints the reason of every skipped test.
