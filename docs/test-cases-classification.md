# Stage 3 - Test cases and scenarios

Tests: `tests/test_classification_*.py` (run with `python -m pytest`).
Design and vocabulary: [classification-design.md](classification-design.md).
5-tuples and diagrams: [classification-automata.md](classification-automata.md).

The goal is to check that each profile's automaton is a well-formed DFA, that
it accepts and rejects exactly the category patterns the design calls for
(including the cases that separate one team-defined profile from another),
that `classify`/`classify_all` agree with running the automata directly, that
the two given-profile examples from the assignment come out ACCEPTED end to
end, and that the diagrams and 5-tuples of the document are the ones the code
produces.

## 1. Shape of each automaton

| ID | Property | Profiles checked | Test file |
|---|---|---|---|
| M1 | The automaton is deterministic (`is_deterministic()`) | all four | `test_classification_full_stack.py`, `..._machine_learning.py`, `..._backend.py`, `..._data_scientist.py` |
| M2 | Σ is exactly the nine `vocabulary.Category` values | all four | same four files |
| M3 | `\|Q\| = len(required) + 1`, and the only final state is `q<len(required)>` | all four | same four files |
| M4 | The automaton is total: `\|δ\| = \|Q\| × \|Σ\|` | all four | `test_classification_diagrams.py` |

## 2. Unit cases per profile

| ID | Profile | Input (category sequence) | Expected | Test file |
|---|---|---|---|---|
| F1 | Full Stack Developer | `LANGUAGE, FRONTEND, BACKEND, DATABASE, VERSION_CONTROL` (the assignment's example) | ACCEPTED | `test_classification_full_stack.py` |
| F2 | Full Stack Developer | the same five categories, one at a time removed | REJECTED, for each of the five | `test_classification_full_stack.py` |
| F3 | Full Stack Developer | the five required with `CONCEPT` interleaved | ACCEPTED (optional category does not block) | `test_classification_full_stack.py` |
| F4 | Full Stack Developer | `LANGUAGE` repeated before the rest | ACCEPTED (a repeat is a self-loop, not a second requirement) | `test_classification_full_stack.py` |
| F5 | Full Stack Developer | `[]`, `[CONCEPT, TOOL]` | REJECTED (empty, or only optional categories) | `test_classification_full_stack.py` |
| L1 | Machine Learning Engineer | `LANGUAGE, DATA_LIBRARY, ML_LIBRARY` (the assignment's example, with repeats of `DATA_LIBRARY`/`ML_LIBRARY`) | ACCEPTED | `test_classification_machine_learning.py` |
| L2 | Machine Learning Engineer | only the three required, nothing optional | ACCEPTED | `test_classification_machine_learning.py` |
| L3 | Machine Learning Engineer | the three required, one at a time removed | REJECTED, for each of the three | `test_classification_machine_learning.py` |
| L4 | Machine Learning Engineer | the three required with `DATABASE`/`CONCEPT`/`VERSION_CONTROL` interleaved | ACCEPTED | `test_classification_machine_learning.py` |
| L5 | Machine Learning Engineer | `[]`, `[DATABASE, VERSION_CONTROL, CONCEPT]` | REJECTED | `test_classification_machine_learning.py` |
| B1 | Backend Developer (team-defined) | `LANGUAGE, BACKEND, DATABASE, VERSION_CONTROL` | ACCEPTED | `test_classification_backend.py` |
| B2 | Backend Developer | the four required, one at a time removed | REJECTED, for each of the four | `test_classification_backend.py` |
| B3 | Backend Developer | `LANGUAGE, FRONTEND, DATABASE, VERSION_CONTROL` (`FRONTEND` in place of `BACKEND`) | REJECTED - the test that confirms this profile is not Full Stack Developer | `test_classification_backend.py` |
| B4 | Backend Developer | the four required with `TOOL`/`CONCEPT` interleaved | ACCEPTED | `test_classification_backend.py` |
| B5 | Backend Developer | `[]` | REJECTED | `test_classification_backend.py` |
| D1 | Data Scientist (team-defined) | `LANGUAGE, DATA_LIBRARY, DATABASE, TOOL` | ACCEPTED | `test_classification_data_scientist.py` |
| D2 | Data Scientist | the four required, one at a time removed | REJECTED, for each of the four | `test_classification_data_scientist.py` |
| D3 | Data Scientist | `LANGUAGE, DATA_LIBRARY, ML_LIBRARY` (a typical Machine Learning Engineer pattern, no `DATABASE`/`TOOL`) | REJECTED - the test that confirms this profile is not Machine Learning Engineer | `test_classification_data_scientist.py` |
| D4 | Data Scientist | the four required with `ML_LIBRARY`/`VERSION_CONTROL` interleaved | ACCEPTED | `test_classification_data_scientist.py` |
| D5 | Data Scientist | `[]` | REJECTED | `test_classification_data_scientist.py` |

Cases B3 and D3 are the ones that matter most for the design: they are the
direct check that the team-defined profiles do not collapse into the two
given ones (see [classification-design.md](classification-design.md)
section 3).

## 3. `classify` / `classify_all`

| ID | Check | Test file |
|---|---|---|
| C1 | `classify(sort_for_profile(tokens, p), p)` agrees with `classify_all(tokens)[p]`, for every profile | `test_classification_classify_all.py` |
| C2 | `classify_all` returns exactly the four `Profile` values as keys | `test_classification_classify_all.py` |
| C3 | `classify_all([])` rejects every profile | `test_classification_classify_all.py` |
| C4 | A token outside `vocabulary.TOKENS` raises `ValueError` (from `sort_for_profile`, stage 2's contract - stage 3 does not mask it) | `test_classification_classify_all.py` |

## 4. Scenarios (complete résumés, stages 1-3)

Each scenario runs `extract`, `normalize` and `classify_all` on a full résumé
and checks the ACCEPTED/REJECTED verdict for every profile
(`test_classification_classify_all.py`).

| Scenario | Résumé | Expected |
|---|---|---|
| A. Full Stack from the assignment | `wednesday_addams.txt` | `FULL_STACK_DEVELOPER: ACCEPTED` (matches `docs/requirements.md`'s worked example) |
| B. ML Engineer from the assignment | `mary_jane_watson.txt` | `MACHINE_LEARNING_ENGINEER: ACCEPTED` (matches `docs/requirements.md`'s worked example) |

## 5. Documents in sync with the code

| ID | Check | Test file |
|---|---|---|
| G1 | The Mermaid diagrams and the table of sizes in `docs/classification-automata.md` are the ones generated from the automata | `test_classification_diagrams.py` |
| G2 | The generated path of required-category edges matches each profile's `*_REQUIRED` list in `automata.py` | `test_classification_diagrams.py` |
| G3 | The generated diagram draws the initial state, the double-circled final state, and every required edge | `test_classification_diagrams.py` |
| G4 | `python -m src.classification.diagrams` prints a known block and rejects an unknown name | `test_classification_diagrams.py` |

If G1 fails, run `python -m src.classification.diagrams <name>` and paste the
new block in `docs/classification-automata.md`.
