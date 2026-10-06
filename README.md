# ResumeLens - Formal Language-Based Resume Screening

Integrative Task 1, Computación y Estructuras Discretas III (2026-2).

ResumeLens reads a resume as plain text and checks whether the qualifications
it explicitly mentions satisfy the qualification pattern of a professional
profile. It does **not** rank candidates or make hiring decisions.

## Team

Team: **Las Trillizas** (E35)

| Member | Main responsibility |
|---|---|
| Santiago Laverde | Contracts, stage 1 (regular expressions), stage 4 (textX DSL and HTML) |
| Mauricio Marin | Literature review, profiles, stage 3 (finite automata) |
| Alejandro Arango | Stage 2 (transducers), sorting, pipeline, UI and integration tests |

IDE used: TODO

## Pipeline

| Stage | Formal model | Library | Folder |
|---|---|---|---|
| 1. Extraction | Regular expressions | `re` | `src/extraction` |
| 2. Normalization | Finite-state transducers | `pyformlang` | `src/normalization` |
| 3. Pattern recognition | Finite automata (DFA/NFA/ε-NFA) | `pyformlang` | `src/classification` |
| 4. Candidate profile language | Context-free grammar | `textX` | `src/dsl` |

The four profiles (Full Stack Developer, Machine Learning Engineer and two
team-defined profiles) go through the same code. See
[docs/contracts.md](docs/contracts.md) for the inputs and outputs of each
module.

## Repository layout

```
docs/       design, formalization and test cases
examples/   example resumes from the assignment
src/        one folder per stage, plus main.py (pipeline)
tests/   automated tests
```

## Setup

```bash
pip install -r requirements.txt
python -m pytest
```

## Documentation

- [Requirements and traceability](docs/requirements.md)
- [Module contracts](docs/contracts.md)
- [Example resumes](examples/README.md)
