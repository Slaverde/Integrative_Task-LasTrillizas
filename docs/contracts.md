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
| 2 | `normalize_skill(raw)` | one raw string | its canonical token, or `None` if it has no canonical form |
| 2 | `sort_by_vocabulary(tokens)` | tokens | the tokens in the order of `vocabulary.TOKENS` (no profile) |
| 3 | `classify(tokens, profile)` | sorted tokens, `Profile` | `bool` |
| 3 | `classify_all(tokens)` | canonical tokens | `dict[Profile, bool]` |
| 4 | `to_dsl_text(candidate)` | `CandidateProfile` | DSL source text |
| 4 | `parse(dsl_text)` | DSL source text | textX model (grammar only; raises `DSLSyntaxError`) |
| 4 | `validate(dsl_text)` | DSL source text | validated textX model (raises `DSLSyntaxError` or `DSLSemanticError`) |
| 4 | `render_html(model)` | validated model | HTML string |
| 1-2 | `analyze(text)` | resume text | `Analysis`: the `ExtractionResult`, the raw string -> token trace, the tokens and the tokens sorted for each of the four profiles |
| 3-4 | `complete(analysis, classifier=None)` | `Analysis` | `PipelineResult`: classifications, `CandidateProfile`, DSL text and HTML |
| - | `run_stages(text, classifier=None)` | resume text | `PipelineResult` (calls `analyze` and `complete`) |
| - | `run_pipeline(text, classifier=None)` | resume text | HTML string (`run_stages(...).html`) |
| - | `python -m src.ui` | resume text pasted in a form | page with every stage (`src/ui/`, standard library only) |

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

## Pipeline details

- `analyze` and `complete` are separate so a caller can show stages 1 and 2
  even if stage 3 is not ready or fails (the UI does this).
- `classifier` has the signature of `classify_all` and defaults to it. The tests
  pass a stand-in so the pipeline can be checked without stage 3.
- `classify_all` receives the canonical tokens as `normalize` gives them; it
  sorts them for each profile by itself.
- The skills of the candidate profile (stage 4) are written once, in the order
  of `vocabulary.TOKENS` (`sort_by_vocabulary`), because the DSL has a single
  skills section for all profiles.
- **Candidate without a name.** If stage 1 finds no name, the pipeline uses
  `src/main.py: UNKNOWN_NAME` (`Unknown candidate`) and `Analysis.name_detected`
  is `False`. The alternative, stopping with an error, would reject a résumé
  that has everything else; the rule S6 of the DSL (non-empty name) is still
  met, and the UI warns that the name was not found.

## Rules between stages

- Stage 1 never normalizes or decides anything; it only returns strings.
- Stage 2 drops strings that have no canonical form.
- Stage 3 only sees canonical tokens that were sorted for the profile it checks.
- Stage 4 only receives data produced by the previous stages.
- The system does not rank candidates; it only checks whether a qualification
  pattern is satisfied.
