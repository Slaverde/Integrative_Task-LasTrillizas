# Stage 4 - Test cases and scenarios

Tests: `tests/test_dsl.py` (75), `tests/test_dsl_html.py` (32) and
`tests/test_dsl_normal_form.py` (48). Input sentences: `examples/dsl/`.

## 1. Grammar and validation (`test_dsl.py`)

| Scenario | Input | Expected |
|---|---|---|
| Valid sentences | the 4 files of `examples/dsl/valid/` | accepted by `validate`; the model has the right name, contact items, years, jobs, studies, skills and results |
| Smallest sentence | `sofia_nunez.rl`: no optional section, empty `skills { }` | accepted; `experience` and `education` are `None` |
| Experience with only jobs | `experience { job: "..." }` | accepted; `years` is `None`, not `0` |
| Lexical errors | unquoted name, lower-case skill, unterminated text | `DSLSyntaxError` |
| Syntactic errors | missing `results`, wrong order, empty `experience`, trailing comma, unclosed block, bad status | `DSLSyntaxError` with line and column |
| Malformed sentences | 16 hand-made cases: empty text, `years: -1`, `'A'` with single quotes, `job` before `years`, empty `contact`... | `DSLSyntaxError` |
| Semantic errors | the 8 files `semantic_*.rl` | pass `parse`, fail `validate` with the rule (S1 to S6) named in the file |
| Several errors at once | bad email, `years: 99`, repeated unknown skill | one `DSLSemanticError` listing S1, S2, S4 and S5 |
| Limits | years 0, 1, 60 valid and 61, 100 invalid; valid and invalid emails and phones | as listed |
| Whole vocabulary | every token of `TOKENS` as skills | accepted |
| Comments and layout | compact text (`skills{GIT,PYTHON}`) and spread text with comments | same model |
| Text generation | `CandidateProfile` -> `to_dsl_text` -> `validate` | the model keeps the data; the output equals the hand-written example |
| Safe text | name with `"` and line breaks, accents | quotes become `'`, line breaks become spaces, accents kept |
| Missing data | no name, unknown skill, lower-case skill, missing profile | rejected (S6, S1, syntax, written as `REJECTED`) |

## 2. HTML visualization (`test_dsl_html.py`)

| Scenario | Expected |
|---|---|
| Every valid example | well-formed page (balanced tags), `<html lang="en">`, UTF-8, one card per profile |
| Content | name, skills in order with their category, `ACCEPTED` and `REJECTED` marked, summary of accepted profiles |
| Nothing accepted / several accepted | "No qualification pattern was satisfied." / profiles listed |
| Empty sections | `Contact`, `Experience` and `Education` are not rendered |
| Years | `1 year`, `0 years`, `3 years`; nothing when unknown |
| Links | `mailto:`, `tel:`, `https://` added to `github.com/...` and `www....` |
| Dangerous links | `javascript:` and `data:` are shown as text, never as `href` |
| Injected HTML | `<script>`, `<img onerror>`, `<b>` and `</title>` are escaped; tags stay balanced |
| Self-contained | no `script`, `img`, `iframe`, `link`, `@import` or `src=` |
| Files | `save_html` writes UTF-8 and creates folders; the 4 pages of `docs/samples/` equal what the code generates |
| Command line | `python -m src.dsl` renders a valid file (exit 0), rejects an invalid one with the rule and writes nothing (exit 1), prints usage without arguments (exit 2) |

## 3. Normal form and equivalence of grammars (`test_dsl_normal_form.py`)

Explained in [dsl-grammar-normal-form.md](dsl-grammar-normal-form.md).

| Scenario | Expected |
|---|---|
| Shape of each step | nine nullable variables; no empty body after step 1; no unit production after step 2; every variable reachable after step 3; only `A -> B C` or `A -> a` at the end |
| Terminals | the same terminals in the original grammar and in the CNF |
| Wrong shapes | `is_cnf` rejects `A -> a b` and `A -> B` |
| Lexer | classifies terminals; rejects `git`, an open quote, `candidate Ana`, `?`; `9GIT` is `number token` |
| Examples | textX, pyformlang (plain grammar) and CYK (CNF) give the same verdict on the 21 example sentences |
| Mutations | the same verdict on 400 mutated sentences (delete, repeat, swap, replace one token); 390 are invalid, 10 still valid |
| Random sentences | 300 sentences generated from the grammar are accepted by the three recognizers; all optional sections appear |
| Semantics | `COBOL` is accepted by the grammars and rejected only by `semantics.py` |
| Documentation | `dsl-grammar-normal-form.md` lists the same CNF and plain grammar that the code produces |
