# Stage 3 - Classification: literature review and design

Implementation: `src/classification/` (finite automata with `pyformlang`).
Depends on: `src/vocabulary.py` (`Category`, `Profile`, `TOKENS`,
`PROFILE_ORDER`). Tests: `tests/test_classification_*.py` (added in later
commits of this stage).

Stage 3 receives the canonical tokens of stage 2, already sorted for one
profile by `sort_for_profile`, and decides `ACCEPTED` or `REJECTED` for that
profile. It does not rank candidates and does not compare profiles against
each other; each profile has its own independent pattern.

## 1. Literature review

**Course material.** The formal definitions and the `pyformlang` API used
below come directly from the course slides (`CyEDIIIdiapositivas3` to `7`,
2026-2): the 5-tuple notation `δ : Q × Σ → Q` for a DFA and
`δ : Q × Σ ∪ {λ} → ℘(Q)` for an NFA / NFA-λ, and the construction pattern
(`DeterministicFiniteAutomaton(states=..., input_symbols=...,
start_state=..., final_states=...)` followed by `add_transitions`), which
`src/normalization/fst.py` already follows for the stage 2 transducers.
Keeping stage 3 on the same construction style keeps the four stages
consistent and keeps the automata easy to compare with what was taught.

**Why a DFA and not an NFA/NFA-λ.** Standard automata theory (as covered in
the course and in general references such as the
[Wikipedia article on deterministic finite automata](https://en.wikipedia.org/wiki/Deterministic_finite_automaton))
establishes that a DFA is the right tool when the accept/reject decision
for every (state, symbol) pair is unambiguous and total. Qualification
pattern recognition fits that case: given a state (how many required
categories have been satisfied so far) and the category of the next token,
there is exactly one next state, never a choice between several. An
NFA or NFA-λ would be needed if the pattern allowed several independent
ways of being satisfied that could not be merged into one deterministic
walk (e.g. "either A or B, but checked in different orders"), which is not
the case here, because stage 2 already sorts the tokens into a fixed
per-profile category order before they reach this stage.

**Why categories and not resume keywords.** General discussions of
keyword-matching applicant tracking systems (e.g.
[ATS keyword-matching limitations](https://topechelon.com/?p=239519)) point
out the same weakness the assignment itself raises in its problem
statement: matching on literal strings conflates spelling variation with
qualification and gives no formal guarantee about what was actually
checked. Running the automaton over `vocabulary.Category` instead of over
raw tokens addresses this directly: a candidate who lists two different
backend frameworks still produces one `BACKEND` symbol as far as the
automaton is concerned, which is the right level of abstraction for "does
this profile's required skill groups appear", not "does this exact
spelling appear".

## 2. Model

### 2.1 From tokens to the automaton's alphabet

Stage 2's `sort_for_profile(tokens, profile)` returns the canonical tokens
ordered by the profile's `PROFILE_ORDER`. Stage 3 maps each token to its
`Category` (via `vocabulary.TOKENS`) before running the automaton:

```
sorted tokens (Full Stack):  JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
category sequence:           LANGUAGE,   FRONTEND, BACKEND, DATABASE, VERSION_CONTROL
```

The automaton's input alphabet Σ is `vocabulary.Category` (9 symbols), the
same for all four profiles; what changes per profile is the state count and
the transition function.

### 2.2 One DFA per profile

Each profile's automaton is a **linear "required categories seen so
far" counter**:

- **States** `Q = {q0, q1, ..., qk}`, where `k` is the number of categories
  the profile requires (`len(required)`). `qi` means "the first `i`
  required categories, in the profile's order, have already appeared".
- **Alphabet** `Σ` = `vocabulary.Category` (all 9 categories), the same set
  for every profile, so the automaton is total: every state has a
  transition for every symbol.
- **Transition function** `δ(qi, c)`:
  - if `i < k` and `c` equals `required[i]` (the next pending required
    category) → `qi+1`;
  - otherwise → `qi` (self-loop: an optional category, a repeat of an
    already-seen required category, or any category not in `required` at
    all leaves the state unchanged).
- **Initial state** `q0`.
- **Accepting states** `F = {qk}` only: every required category has been
  seen, in order.

Because `δ` is defined for every `(qi, c)` pair and gives exactly one
result, this is a DFA by construction — not something that has to be
checked afterward.

**Why "in order" is not a real restriction.** `required` is a subsequence
of the profile's own `PROFILE_ORDER`, and stage 2 already outputs the
tokens sorted by `PROFILE_ORDER`. So by the time the sequence reaches
stage 3, the required categories (if present at all) necessarily appear in
non-decreasing `PROFILE_ORDER` position, which is exactly the order `δ`
expects. The automaton does not need to search or backtrack; it only needs
to confirm that each required category shows up at some point while
scanning left to right once.

**Example** (Full Stack, resume from the assignment:
`JS, React.js, NodeJS, Postgres, Git`):

| Step | Category read | State before | State after |
|---|---|---|---|
| 1 | LANGUAGE | q0 | q1 |
| 2 | FRONTEND | q1 | q2 |
| 3 | BACKEND | q2 | q3 |
| 4 | DATABASE | q3 | q4 |
| 5 | VERSION_CONTROL | q4 | q5 (accepting) |

Result: `FULL_STACK_DEVELOPER -> ACCEPTED`, matching the example in the
assignment and in `docs/requirements.md`.

## 3. Required categories per profile

No further specification for the two team-defined profiles arrived from
the professor (the assignment only says "detailed requirements... will be
provided separately" — see `docs/requirements.md`), so the team defines
them here, with a justification, as the assignment allows.

| Profile | Required (must all appear) | Optional (read but do not affect acceptance) | Why |
|---|---|---|---|
| `FULL_STACK_DEVELOPER` | LANGUAGE, FRONTEND, BACKEND, DATABASE, VERSION_CONTROL | CONCEPT | The assignment lists these five as the technology groups that define the role; REST APIs (`CONCEPT`) are a nice-to-have the reference profile only says "may include". |
| `MACHINE_LEARNING_ENGINEER` | LANGUAGE, DATA_LIBRARY, ML_LIBRARY | DATABASE, VERSION_CONTROL, CONCEPT | The assignment's core list for this role is Python + data libraries + ML frameworks; SQL and Git are listed but not what distinguishes the role. |
| `BACKEND_DEVELOPER` (team-defined, software) | LANGUAGE, BACKEND, DATABASE, VERSION_CONTROL | CONCEPT, TOOL | Same server-side stack as Full Stack, minus `FRONTEND` — the one category that defines the difference between the two roles. |
| `DATA_SCIENTIST` (team-defined, AI/data) | LANGUAGE, DATA_LIBRARY, DATABASE, TOOL | ML_LIBRARY, VERSION_CONTROL | Emphasizes data analysis and tooling (e.g. Jupyter) over production ML frameworks, so the pattern does not collapse into a near-duplicate of `MACHINE_LEARNING_ENGINEER`. |

`BACKEND_DEVELOPER` and `DATA_SCIENTIST` stay marked provisional in
`src/vocabulary.py` until/unless the professor sends a different
specification; if one arrives, only this table and the corresponding
automaton need to change, not the model in section 2.

## 4. What stage 3 does not do

- It does not normalize or extract anything (stages 1 and 2's job).
- It does not compare candidates against each other or rank them.
- It does not decide which profile "fits best" — `classify_all` runs all
  four independent automata and returns one `ACCEPTED`/`REJECTED` per
  profile; a candidate can be accepted for more than one, or for none.

## 5. Next in this stage

- `src/classification/automata.py`: one `build_<profile>()` function per
  profile, following `src/normalization/fst.py`'s style.
- `classify(tokens, profile)` / `classify_all(tokens)` in
  `src/classification/__init__.py`, replacing the current
  `NotImplementedError` stubs.
- Transition diagrams generated from the code (not drawn by hand), the
  same way `src/normalization/diagrams.py` does for stage 2.
- `tests/test_classification_*.py` covering the two given profiles, the
  two team-defined ones, and the boundary cases (missing exactly one
  required category, extra optional categories, empty input).
