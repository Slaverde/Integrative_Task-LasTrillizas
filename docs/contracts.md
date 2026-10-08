# Module contracts

ResumeLens is a four-stage pipeline. Every profile goes through the same code;
only the data (vocabulary, profile order, automaton) changes per profile.

```
resume text
   |  (1) extract            src/extraction      regular expressions (re)
   v
ExtractionResult             raw strings, order of appearance
   |  (2) normalize          src/normalization   finite-state transducers
   |      sort_for_profile
   v
list[str]                    canonical tokens sorted by the profile order
   |  (3) classify           src/classification  finite automata
   v
dict[Profile, bool]          ACCEPTED / REJECTED per profile
   |  (4) to_dsl_text        src/dsl             textX grammar
   |      validate
   |      render_html
   v
HTML visualization
```

## Modules

| Stage | Function | Input | Output |
|---|---|---|---|
| 1 | `extract(text)` | resume text (`str`) | `ExtractionResult` |
| 2 | `normalize(extracted)` | `ExtractionResult` | canonical tokens (`list[str]`, no duplicates) |
| 2 | `sort_for_profile(tokens, profile)` | tokens, `Profile` | tokens in the profile's canonical order |
| 3 | `classify(tokens, profile)` | sorted tokens, `Profile` | `bool` |
| 3 | `classify_all(tokens)` | canonical tokens | `dict[Profile, bool]` |
| 4 | `to_dsl_text(candidate)` | `CandidateProfile` | DSL source text |
| 4 | `parse(dsl_text)` | DSL source text | textX model (grammar only; raises `DSLSyntaxError`) |
| 4 | `validate(dsl_text)` | DSL source text | validated textX model (raises `DSLSyntaxError` or `DSLSemanticError`) |
| 4 | `render_html(model)` | validated model | HTML string |
| - | `run_pipeline(text)` | resume text | HTML string |

The data classes (`ExtractionResult`, `CandidateProfile`) live in
`src/contracts.py`; the shared vocabulary lives in `src/vocabulary.py`.

## Canonical vocabulary

Defined in `src/vocabulary.py`:

- `TOKENS`: canonical token -> category (e.g. `JAVASCRIPT -> LANGUAGE`).
  These tokens are the output alphabet of the transducers (stage 2) and the
  input alphabet of the automata (stage 3).
- `PROFILE_ORDER`: for each profile, the category order used to sort tokens
  so the result does not depend on how the candidate wrote the resume.
  Example for Full Stack: LANGUAGE -> FRONTEND -> BACKEND -> DATABASE ->
  VERSION_CONTROL -> CONCEPT.

## Profiles

| Profile | Status |
|---|---|
| `FULL_STACK_DEVELOPER` | Given by the assignment |
| `MACHINE_LEARNING_ENGINEER` | Given by the assignment |
| `BACKEND_DEVELOPER` | **Provisional** (software profile, pending the professor's requirements) |
| `DATA_SCIENTIST` | **Provisional** (AI/data profile, pending the professor's requirements) |

## Rules between stages

- Stage 1 never normalizes or decides anything; it only returns strings.
- Stage 2 drops strings that have no canonical form.
- Stage 3 only sees canonical tokens that were sorted for the profile it checks.
- Stage 4 only receives data produced by the previous stages.
- The system does not rank candidates; it only checks whether a qualification
  pattern is satisfied.
