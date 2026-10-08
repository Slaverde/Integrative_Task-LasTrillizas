# Stage 4 - Simplification and Chomsky normal form of the grammar

Learning outcome RAA3: simplify grammars with normal forms. This document takes
the candidate profile grammar ([dsl-grammar.md](dsl-grammar.md)), writes it as a
plain context-free grammar, simplifies it and converts it to **Chomsky normal
form (CNF)**, where every production is `A -> B C` (two variables) or
`A -> a` (one terminal).

The code is in `src/dsl/cfg.py` (the grammar and the lexer) and
`src/dsl/normal_form.py` (the algorithms). Print the result with:

```bash
python -m src.dsl.normal_form
```

## 1. From EBNF to plain productions

The EBNF uses `[ x ]` and `{ x }`, which are not allowed in a plain grammar.
They are replaced like this:

| EBNF | Plain productions |
|---|---|
| `[ contact ]` (optional) | `OptContact -> Contact \| epsilon` |
| `{ job }` (zero or more) | `JobList -> Job JobList \| epsilon` |
| `x , { x }` (one or more) | `X -> x XTail` and `XTail -> x XTail \| epsilon` |
| `token , { "," , token }` | `SkillList -> Tok SkillTail`, `SkillTail -> comma Tok SkillTail \| epsilon` |

The terminals are the keywords (`candidate`, `contact`, `email`, ...), the
symbols (`lbrace`, `rbrace`, `colon`, `comma`) and the three lexical classes
`text`, `number` and `token`. Words such as `ACCEPTED` and `REJECTED` also look
like a `token`, so the lexer gives them their own terminals (`accepted`,
`rejected`) and the grammar says `Tok -> token | accepted | rejected`; this keeps
the language equal to the textX one.

```
Candidate     -> candidate text lbrace OptContact OptExperience OptEducation Skills Results rbrace

OptContact    -> Contact | epsilon
Contact       -> contact lbrace ContactItem ContactTail rbrace
ContactTail   -> ContactItem ContactTail | epsilon
ContactItem   -> email colon text | phone colon text | link colon text

OptExperience -> Experience | epsilon
Experience    -> experience lbrace ExpBody rbrace
ExpBody       -> years colon number JobList | Job JobList
JobList       -> Job JobList | epsilon
Job           -> job colon text

OptEducation  -> Education | epsilon
Education     -> education lbrace Study StudyList rbrace
StudyList     -> Study StudyList | epsilon
Study         -> study colon text

Skills        -> skills lbrace OptSkillList rbrace
OptSkillList  -> SkillList | epsilon
SkillList     -> Tok SkillTail
SkillTail     -> comma Tok SkillTail | epsilon

Results       -> results lbrace Result ResultTail rbrace
ResultTail    -> Result ResultTail | epsilon
Result        -> Tok colon Status
Status        -> accepted | rejected

Tok           -> token | accepted | rejected
```

23 variables and 38 productions, nine of them with an empty body (`epsilon`).

## 2. Simplification

### Step 1: eliminate epsilon productions

A variable is *nullable* if it can derive the empty string. The nullable
variables are:

`ContactTail`, `JobList`, `OptContact`, `OptEducation`, `OptExperience`,
`OptSkillList`, `ResultTail`, `SkillTail`, `StudyList`.

For every production, one new production is added for each way of leaving out
nullable symbols, and the empty bodies are deleted. The start symbol is not
nullable (a candidate always has at least `candidate`, a name and braces), so the
language does not change. Example: `Candidate` has three optional parts, so it
now has 2^3 = 8 bodies:

```
Candidate -> candidate text lbrace Skills Results rbrace
           | candidate text lbrace OptContact Skills Results rbrace
           | ... (6 more combinations of OptContact, OptExperience, OptEducation)
```

Productions: 38 -> 48.

### Step 2: eliminate unit productions

A unit production is `A -> B` with a single variable. For every pair `(A, B)`
such that `A =>* B` using only unit productions, the non-unit productions of `B`
are copied to `A`. There are 11 pairs with `A != B`:

| A | can reach |
|---|---|
| `ContactTail` | `ContactItem` |
| `ExpBody`, `JobList` | `Job` |
| `OptContact` | `Contact` |
| `OptEducation` | `Education` |
| `OptExperience` | `Experience` |
| `OptSkillList` | `SkillList`, `Tok` |
| `ResultTail` | `Result` |
| `SkillList` | `Tok` |
| `StudyList` | `Study` |

Example: `Tok -> token | accepted | rejected` is copied into `SkillList` and
`OptSkillList`, so `OptSkillList -> accepted | rejected | token | Tok SkillTail`.

Productions: 48 -> 57.

### Step 3: remove useless symbols

A symbol is useless if it derives no string of terminals, or if the start symbol
cannot reach it. After step 2, `Contact`, `Education`, `Experience` and
`SkillList` are no longer used (their bodies were copied into the `Opt...`
variables), so they are removed. The grammar has no non-generating variables.

Variables: 23 -> 19. Productions: 57 -> 48.

### Step 4: Chomsky normal form

1. **TERM.** In every body with two or more symbols, each terminal `a` is
   replaced by a new variable `Ta` with the single production `Ta -> a`
   (for example `TLbrace -> lbrace`). This adds 19 variables.
2. **BIN.** A body with more than two variables, `A -> B1 B2 ... Bn`, becomes a
   chain `A -> B1 X1`, `X1 -> B2 X2`, ..., `X(n-2) -> B(n-1) Bn`. Chains with the
   same tail share the same helper variable `X`. This adds 51 variables.

Result: 88 variables and 117 productions (18 original variables, 19 `T...`
variables and 51 `X...` helpers).

## 3. Result: the grammar in Chomsky normal form

```
Candidate -> TCandidate X1 | TCandidate X11 | TCandidate X15 | TCandidate X18 | TCandidate X20 | TCandidate X22 | TCandidate X24 | TCandidate X7
ContactItem -> TEmail X26 | TLink X26 | TPhone X26
ContactTail -> ContactItem ContactTail | TEmail X26 | TLink X26 | TPhone X26
ExpBody -> Job JobList | TJob X26 | TYears X27 | TYears X28
Job -> TJob X26
JobList -> Job JobList | TJob X26
OptContact -> TContact X30 | TContact X33
OptEducation -> TEducation X35 | TEducation X38
OptExperience -> TExperience X40
OptSkillList -> accepted | rejected | token | Tok SkillTail
Result -> Tok X42
ResultTail -> Result ResultTail | Tok X42
Results -> TResults X43 | TResults X46
SkillTail -> TComma Tok | TComma X48
Skills -> TSkills X49 | TSkills X51
Status -> accepted | rejected
Study -> TStudy X26
StudyList -> Study StudyList | TStudy X26
TCandidate -> candidate
TColon -> colon
TComma -> comma
TContact -> contact
TEducation -> education
TEmail -> email
TExperience -> experience
TJob -> job
TLbrace -> lbrace
TLink -> link
TNumber -> number
TPhone -> phone
TRbrace -> rbrace
TResults -> results
TSkills -> skills
TStudy -> study
TText -> text
TYears -> years
Tok -> accepted | rejected | token
X1 -> TText X2
X10 -> OptExperience X4
X11 -> TText X12
X12 -> TLbrace X13
X13 -> OptContact X14
X14 -> OptExperience X5
X15 -> TText X16
X16 -> TLbrace X17
X17 -> OptContact X5
X18 -> TText X19
X19 -> TLbrace X4
X2 -> TLbrace X3
X20 -> TText X21
X21 -> TLbrace X10
X22 -> TText X23
X23 -> TLbrace X14
X24 -> TText X25
X25 -> TLbrace X5
X26 -> TColon TText
X27 -> TColon TNumber
X28 -> TColon X29
X29 -> TNumber JobList
X3 -> OptContact X4
X30 -> TLbrace X31
X31 -> ContactItem X32
X32 -> ContactTail TRbrace
X33 -> TLbrace X34
X34 -> ContactItem TRbrace
X35 -> TLbrace X36
X36 -> Study X37
X37 -> StudyList TRbrace
X38 -> TLbrace X39
X39 -> Study TRbrace
X4 -> OptEducation X5
X40 -> TLbrace X41
X41 -> ExpBody TRbrace
X42 -> TColon Status
X43 -> TLbrace X44
X44 -> Result X45
X45 -> ResultTail TRbrace
X46 -> TLbrace X47
X47 -> Result TRbrace
X48 -> Tok SkillTail
X49 -> TLbrace X50
X5 -> Skills X6
X50 -> OptSkillList TRbrace
X51 -> TLbrace TRbrace
X6 -> Results TRbrace
X7 -> TText X8
X8 -> TLbrace X9
X9 -> OptContact X10
```

## 4. How we know the language did not change

The three steps and the conversion are supposed to preserve the language. We
checked it by comparing three independent recognizers (`tests/test_dsl_normal_form.py`):

| Recognizer | What it uses |
|---|---|
| textX | `src/dsl/candidate.tx`, the grammar of the project |
| pyformlang | the plain grammar of section 1, loaded as a `CFG` |
| CYK | our CNF of section 3, with the CYK algorithm (`O(n^3)`) |

They must give the same answer (accepted or rejected) on:

- the 4 valid and 17 invalid example sentences of `examples/dsl/`;
- about 400 mutations of the valid examples (delete, repeat, swap or replace
  one token), most of them invalid;
- 300 random sentences generated from the plain grammar, which must all be
  accepted by the three.

The tests also check the shape of every intermediate grammar (no empty bodies
after step 1, no unit productions after step 2, every variable reachable after
step 3, only `A -> B C` or `A -> a` at the end) and that this document lists
the same grammar that the code produces.

## 5. Observations

- **CNF is not shorter, it is more uniform.** The grammar grows from 38 to 117
  productions, mostly because three independent optional sections multiply into
  8 bodies and because long bodies are split into chains. The EBNF is much easier
  to read and to maintain; CNF is useful because every parse tree is binary, which
  makes CYK possible and simplifies proofs about the language.
- **Unit productions came from design choices.** `Tok -> token | accepted |
  rejected` and the `Opt...` wrappers create unit chains that step 2 removes.
- **Semantic rules are outside the grammar.** A sentence with an unknown skill
  such as `COBOL` is accepted by the three recognizers; only `semantics.py`
  rejects it.
- **Terminals are abstract.** `text`, `number` and `token` stand for whole classes
  of strings; the lexer (`cfg.lex`) decides which class each piece of text belongs
  to before any grammar is used.
