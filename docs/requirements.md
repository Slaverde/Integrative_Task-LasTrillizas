# Requirements and traceability

Source: assignment *Integrative Task 1 - ResumeLens* (CyED3 2026-2).
Deadline: **October 11, 2026**.

## Functional requirements

| ID | Requirement | Formal model | Library | Code | Deliverable in `docs/` |
|---|---|---|---|---|---|
| R1 | Extract contact data, languages, frameworks/libraries, databases, academic qualifications, experience, tools and other relevant qualifications; explain each pattern; keep the result in a data structure | Regular expressions | `re` | `src/extraction` | regex catalog (commits 3-5) |
| R2 | Normalize variants to a canonical form (e.g. `JS`, `Javascript` -> `JAVASCRIPT`) using our own transformations; give the 7-tuple, the diagram and the implementation of each transducer | Finite-state transducers | `pyformlang` | `src/normalization` | [normalization-transducers.md](normalization-transducers.md) (7-tuples and diagrams), [normalization-design.md](normalization-design.md) |
| R3 | Sort normalized qualifications by profile order so the result does not depend on the resume order | - | - | `src/normalization` | profile orders (commit 26) |
| R4 | One automaton per profile; give the 5-tuple, the diagram, the pattern it represents and why it is a DFA, NFA or ε-NFA | Finite automata | `pyformlang` | `src/classification` | automata definitions (commits 17-18) |
| R5 | Define a DSL for the candidate profile in EBNF (terminals and non-terminals), validate it, reject invalid input and generate an HTML or Markdown visualization | Context-free grammar | `textX` | `src/dsl` | [dsl-grammar.md](dsl-grammar.md) |
| R6 | The four profiles go through the same code, not separate implementations | - | - | `src/main.py` | `docs/contracts.md` |

Profiles: Full Stack Developer and Machine Learning Engineer (given), plus one
software profile and one AI/data profile defined by the team. The system does
not rank candidates or decide hiring; it only checks qualification patterns.

## Non-functional and delivery requirements

| Item | Requirement |
|---|---|
| Literature review | Done before implementing, to guide decisions |
| Design | Module design (functions, inputs/outputs), formalization, test cases with scenarios |
| Implementation | Python, complete model, UI and tests |
| Poster | In English, following the course guide |
| Presentation | 10 minutes, in English, technical (models, architecture, design decisions, results, limitations) |
| Repository | At least 10 commits, 2 hours apart, meaningful; `docs/` in Markdown; `README.md` with the IDE and member names |
| Contribution | Each member is evaluated through their commits |
| Team | 2 to 3 people from the same course group |
| Registration | Team name with prefix `E` + number (ours: E35), course code and group |

## Learning outcomes covered

| Outcome | Where |
|---|---|
| RAA1 - regular expressions and automata theory for language processing | stages 1, 2 and 3 |
| RAA2 - generative grammars for specialized languages | stage 4 |
| RAA3 - simplify grammars with normal forms | [dsl-grammar-normal-form.md](dsl-grammar-normal-form.md) |
| RAA6 - communicate with specialized vocabulary | poster and presentation |

## Pipeline example from the assignment

Resume fragment: `Wednesday Addams - 3 years of experience developing web
applications. Technical Skills: JS, React.js, NodeJS, Postgres, Git.`

| Stage | Result |
|---|---|
| 1. Extraction | `JS`, `React.js`, `NodeJS`, `Postgres`, `Git` |
| 2. Normalization and sorting (Full Stack order) | `JAVASCRIPT`, `REACT`, `NODE_JS`, `POSTGRESQL`, `GIT` |
| 3. Classification | `FULL_STACK_DEVELOPER`: ACCEPTED |
| 4. DSL and visualization | validated candidate profile rendered as HTML |
