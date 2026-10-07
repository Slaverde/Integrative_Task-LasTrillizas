# Stage 4 - Candidate profile language (grammar)

The DSL describes, in a structured and validated way, everything ResumeLens
learned about one candidate: personal and contact data, experience, education,
the normalized skills and the result of the classification for every profile.

Input of this stage: the output of stages 1 to 3 (`CandidateProfile`,
`src/contracts.py`). Output: a validated model and an HTML visualization.
The grammar is implemented with textX in `src/dsl/` (next commit); this
document is its formal definition.

## 1. Example sentence

```
// Wednesday Addams
candidate "Wednesday Addams" {
  experience {
    years: 3
    job: "3 years of experience developing web applications"
  }
  skills { JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT }
  results {
    FULL_STACK_DEVELOPER: ACCEPTED
    MACHINE_LEARNING_ENGINEER: REJECTED
    BACKEND_DEVELOPER: REJECTED
    DATA_SCIENTIST: REJECTED
  }
}
```

More sentences, valid and invalid, are in `examples/dsl/`.

## 2. Grammar in EBNF

Notation: `=` defines, `,` concatenates, `|` chooses, `[ x ]` is optional,
`{ x }` is zero or more repetitions, `( x )` groups, `"x"` is a literal
terminal, `a - b` is "a except b", and `(* ... *)` is a comment.

```
(* ---- syntactic rules ---- *)
candidate_profile = "candidate" , text , "{" ,
                      [ contact ] , [ experience ] , [ education ] ,
                      skills , results ,
                    "}" ;

contact       = "contact" , "{" , contact_item , { contact_item } , "}" ;
contact_item  = ( "email" | "phone" | "link" ) , ":" , text ;

experience    = "experience" , "{" ,
                  ( "years" , ":" , integer , { job } | job , { job } ) ,
                "}" ;
job           = "job" , ":" , text ;

education     = "education" , "{" , study , { study } , "}" ;
study         = "study" , ":" , text ;

skills        = "skills" , "{" , [ token , { "," , token } ] , "}" ;

results       = "results" , "{" , result , { result } , "}" ;
result        = token , ":" , status ;
status        = "ACCEPTED" | "REJECTED" ;

(* ---- lexical rules ---- *)
text      = '"' , { character - ( '"' | newline ) } , '"' ;
integer   = digit , { digit } ;
token     = upper , { upper | digit } ,
            { "_" , ( upper | digit ) , { upper | digit } } ;
upper     = "A" | "B" | ... | "Z" ;
digit     = "0" | "1" | ... | "9" ;
comment   = "//" , { character - newline } ;   (* ignored, like white space *)
```

## 3. Terminals and non-terminals

**Terminals**

| Kind | Terminals |
|---|---|
| Keywords | `candidate`, `contact`, `email`, `phone`, `link`, `experience`, `years`, `job`, `education`, `study`, `skills`, `results`, `ACCEPTED`, `REJECTED` |
| Symbols | `{`, `}`, `:`, `,` |
| Lexical classes | `text` (double-quoted string), `integer`, `token` (upper-case identifier such as `NODE_JS`) |
| Ignored | white space, line breaks and `//` comments |

**Non-terminals**

| Non-terminal | Meaning | Repeats? | Optional? |
|---|---|---|---|
| `candidate_profile` | Start symbol: one candidate | no | no |
| `contact` | Block of contact items | no | yes |
| `contact_item` | One e-mail, phone or link | 1 or more | no (inside `contact`) |
| `experience` | Years and/or job entries | no | yes |
| `job` | One experience entry | 0 or more | yes |
| `education` | Block of study records | no | yes |
| `study` | One degree or institution | 1 or more | no (inside `education`) |
| `skills` | List of canonical tokens | no | no (the list may be empty) |
| `results` | Block of classification results | no | no |
| `result` | One profile and its status | 1 or more | no |
| `status` | `ACCEPTED` or `REJECTED` | no | no |

## 4. Structural characteristics

- **Nested blocks.** A candidate contains blocks, and each block contains
  items. Braces must be balanced, so a missing `}` is a syntax error.
- **Fixed order of sections.** `contact`, `experience`, `education`,
  `skills`, `results`. A fixed order keeps the grammar unambiguous and the
  generated text predictable.
- **Optional sections.** `contact`, `experience` and `education` may be
  missing, because a resume does not always have them (the assignment's own
  examples have no contact data). `skills` and `results` are mandatory.
- **Repeated elements.** Several contact items, jobs, studies, skills and
  results can appear, as the assignment asks.
- **Keywords versus tokens.** Keywords are lower-case and canonical tokens are
  upper-case, so a keyword can never be read as a skill. `ACCEPTED` and
  `REJECTED` also look like a `token`, but they only appear after `:` in a
  `result`, where the grammar expects a `status`.
- **Unambiguous and LL(1).** Every choice is decided by the next terminal:

  | Choice | Decided by |
  |---|---|
  | optional sections | `contact` / `experience` / `education` / `skills` |
  | `contact_item` | `email` / `phone` / `link` |
  | `experience` body | `years` / `job` |
  | repeat of `job`, `study`, `contact_item`, `result` | next terminal is the item keyword or a `token`; otherwise `}` |
  | `skills` list | `,` continues, `}` ends |
  | `status` | `ACCEPTED` / `REJECTED` |

- **Context-free, in practice regular.** The language is defined with a
  context-free grammar, as the assignment requires. Because blocks are nested
  only two levels deep, the language could also be described with a regular
  expression; the grammar form is kept because it is the natural way to
  express nested blocks and it lets new nested sections be added without
  redesigning the language.
- **Why braces and not indentation.** Braces make the structure explicit, so
  the generated text does not depend on white space.

### Leftmost derivation of the smallest sentence

```
candidate "A" { skills { } results { FULL_STACK_DEVELOPER: REJECTED } }
```

```
candidate_profile
=> "candidate" text "{" skills results "}"
=> "candidate" "A" "{" "skills" "{" "}" results "}"
=> "candidate" "A" "{" "skills" "{" "}" "results" "{" result "}" "}"
=> "candidate" "A" "{" "skills" "{" "}" "results" "{" token ":" status "}" "}"
=> "candidate" "A" "{" "skills" "{" "}" "results" "{" FULL_STACK_DEVELOPER ":" REJECTED "}" "}"
```

(`contact`, `experience` and `education` were skipped through their optional
brackets.)

## 5. What the grammar rejects

The assignment asks to reject representations that break the lexical or
syntactic rules. Rules that need data outside the grammar are checked after
parsing (semantic rules).

**Lexical errors** (the text does not form a valid terminal)

| Input | Why it is rejected |
|---|---|
| `candidate Ana { ... }` | the name is not a quoted `text` |
| `skills { git }` | a skill is not an upper-case `token` |
| `candidate "Ana { ... }` | the `text` is never closed |

**Syntactic errors** (valid terminals in an invalid order)

| Input | Why it is rejected |
|---|---|
| no `results` block | `results` is mandatory |
| `results` before `skills` | sections have a fixed order |
| `experience { }` | needs `years` or at least one `job` |
| `skills { GIT, }` | a `,` must be followed by a `token` |
| missing final `}` | unbalanced braces |
| `FULL_STACK_DEVELOPER: MAYBE` | `status` is `ACCEPTED` or `REJECTED` |

**Semantic errors** (valid sentence, invalid meaning)

| ID | Rule |
|---|---|
| S1 | Every skill token belongs to the canonical vocabulary (`src/vocabulary.py`) |
| S2 | A skill token is not repeated |
| S3 | Every `result` names a known profile, and each of the four profiles appears exactly once |
| S4 | `years` is between 0 and 60 |
| S5 | Each `email` and `phone` has a valid format (same patterns as stage 1) |
| S6 | The candidate name is not empty |

## 6. Mapping with `CandidateProfile`

| DSL | `CandidateProfile` field |
|---|---|
| `candidate "name"` | `name` |
| `email: "..."` | `emails` |
| `phone: "..."` | `phones` |
| `link: "..."` | `links` (new field, added with the textX implementation) |
| `years: n` | `experience_years` |
| `job: "..."` | `experience` (new field, added with the textX implementation) |
| `study: "..."` | `education` |
| `skills { ... }` | `skills` |
| `results { P: ACCEPTED }` | `classifications[P] = True` |

## 7. Design decisions

- **One result per profile, all four listed.** Listing `REJECTED` explicitly
  makes the output complete and lets the HTML show every profile. The
  assignment's "result for each accepted profile" is covered because several
  profiles can be `ACCEPTED` at the same time.
- **Profile names are tokens, not keywords.** The two team-defined profiles are
  still provisional; checking them in rule S3 means a change in the vocabulary
  does not require changing the grammar.
- **Skills are checked against the vocabulary after parsing.** Putting every
  skill in the grammar would force a grammar change each time a technology is
  added.
- **Strings cannot contain `"`.** It keeps the lexical rule simple; stage 1
  never produces a double quote inside a name, job or degree.
