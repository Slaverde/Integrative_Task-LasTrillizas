# Stage 1 - Extraction with regular expressions

Implementation: `src/extraction/` (Python `re` module). All patterns live in
`src/extraction/patterns.py`; `contact.py` and `education.py` apply them.

Stage 1 only **detects** text that may be a qualification or candidate data.
It does not decide whether two strings are equivalent (stage 2) nor whether the
candidate satisfies a profile (stage 3). Results are stored in the
`ExtractionResult` data class (`src/contracts.py`), keeping the order of
appearance and removing duplicates.

This document covers contact information, academic qualifications and
technical skills (languages, frameworks/libraries and databases). Tools and
experience are added in a later commit.

Notation: `[ \t]` is used instead of `\s` so a match never crosses a line
break; `\w` is a letter, digit or underscore.

## 1. E-mail

```
[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}
```

| Part | Recognizes |
|---|---|
| `[A-Za-z0-9._%+-]+` | Local part: one or more letters, digits or `. _ % + -` |
| `@` | The separator |
| `[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*` | One or more domain labels separated by dots |
| `\.[A-Za-z]{2,}` | Final dot and a top-level domain of at least two letters |

Language: strings `local@domain.tld`. The mandatory final `\.[A-Za-z]{2,}`
makes the match stop before a sentence-ending period.

- Accepts: `john.doe+cv@mail.example.com`, `ana@icesi.edu.co`
- Rejects: `Skills: Python`, `ana@localhost`

## 2. Phone number

```
(?<![\w.])(?:\+\d{1,3}[ .-]?)?(?:\(\d{1,4}\)[ .-]?\d{3}[ .-]?\d{4}|\d{3}[ .-]\d{3}[ .-]\d{4}|\d{3}[ .-]\d{7}|\d{10})(?!\w)
```

| Part | Recognizes |
|---|---|
| `(?<![\w.])` | The match cannot start in the middle of a word or number |
| `(?:\+\d{1,3}[ .-]?)?` | Optional country code, e.g. `+57 ` |
| `\(\d{1,4}\)[ .-]?\d{3}[ .-]?\d{4}` | Area code in parentheses, then 3 + 4 digits |
| `\d{3}[ .-]\d{3}[ .-]\d{4}` | Digits in groups 3-3-4 |
| `\d{3}[ .-]\d{7}` | Groups 3-7 |
| `\d{10}` | Ten consecutive digits |
| `(?!\w)` | The match cannot end in the middle of a longer number |

Language: ten-digit phone numbers in the usual groupings, with an optional
country code.

- Accepts: `+57 300 123 4567`, `300-123-4567`, `3001234567`, `+573001234567`,
  `+1 (415) 555-2671`, `(601) 555 1234`
- Rejects: `2019-2023`, `12345`, `12345678901234`

## 3. Links

```
(?:https?://|www\.)[^\s<>"']+|(?<![@\w.])(?:linkedin\.com|github\.com)/[\w./~%-]+
```

| Alternative | Recognizes |
|---|---|
| `(?:https?://\|www\.)[^\s<>"']+` | A URL starting with `http://`, `https://` or `www.`, up to a space or quote |
| `(?<![@\w.])(?:linkedin\.com\|github\.com)/[\w./~%-]+` | A LinkedIn or GitHub path written without protocol |

The code removes trailing `. , ; : )` from each match, so
`(https://ana.dev/projects),` gives `https://ana.dev/projects`. The lookbehind
`(?<![@\w.])` prevents `ana@github.com` from being read as a link.

- Accepts: `https://ana.dev/projects`, `linkedin.com/in/ana-perez`,
  `github.com/anaperez`, `www.ana.dev`
- Rejects: `ana@github.com`

## 4. Candidate name

Two patterns, with `NAME_BODY = W([ \t]+W){1,3}` where
`W = [A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñü'’-]+`:

```
NAME          = W([ \t]+W){1,3}
LABELED_NAME  = ^[ \t]*(?i:name|nombre)[ \t]*:[ \t]*(NAME_BODY)[ \t]*$     (multiline)
```

Language: two to four words, each starting with a capital letter (accents,
hyphens and apostrophes allowed; all-caps words also match).

Strategy (`extract_name`):

1. If a line `Name: ...` / `Nombre: ...` exists, use it.
2. Otherwise inspect only the first three non-empty lines and take the first
   that matches `NAME` completely and has no heading word (`Curriculum`,
   `Vitae`, `Resume`, `CV`, `Profile`, `Hoja`, `Vida`).

- Accepts: `Wednesday Addams`, `MARÍA JOSÉ Pérez-Núñez`, `Nombre: Juan Pérez`
- Rejects: `Curriculum Vitae`, `3 years of experience`, `skills: python`

## 5. Academic degrees

```
(?<!scrum )\b(?:KEYWORD)\b\.?(?:[ \t]+(?!STOP\b)[^\W\d_]+){0,5}        (case-insensitive)
```

`KEYWORD` is one of: `bachelor`, `master` (with optional `'s`), `doctorate`,
`PhD`, `BSc`, `MSc`, `associate degree`, `ingeniería`, `ingeniero/a`,
`tecnólogo`, `especialización`, `maestría`, `doctorado`, `licenciatura`.
`STOP` is one of: `from at with con desde universidad university instituto
institute college`.

| Part | Recognizes |
|---|---|
| `(?<!scrum )` | Excludes "Scrum Master" |
| `\b(?:KEYWORD)\b\.?` | A degree word, with an optional final dot (`B.Sc.`) |
| `[ \t]+(?!STOP\b)[^\W\d_]+` repeated 0 to 5 times | Up to five following words made of letters only, stopping at digits, punctuation, line breaks or a stop word |

Language: a degree word followed by the name of the program, e.g. `Bachelor of
Science in Computer Science`. The words `of`, `in`, `de`, `y`, etc. are covered
by the generic word class.

- Accepts: `Bachelor of Science in Computer Science`, `Ingeniería de Sistemas y
  Computación`, `B.Sc. in Physics`, `Maestría en Analítica`
- Rejects: `Certified Scrum Master`

## 6. Institutions

```
\b(?:Universidad|Universidade|Instituto|Politécnico|Pontificia|Escuela|Fundación)(?:[ \t]+(?:de|del|la|los|las|y)\b)?(?:[ \t]+CAP)+
| \b(?:CAP[ \t]+){1,3}(?:University|Institute|College)(?:[ \t]+of(?:[ \t]+CAP)+)?
| \b(?:University|Institute|College)[ \t]+of(?:[ \t]+CAP)+
```

with `CAP = [A-ZÁÉÍÓÚÑ][\w'’-]*`. Case-sensitive.

| Alternative | Recognizes |
|---|---|
| 1 | Spanish/Portuguese form: institution word, optional connector, then capitalized words (`Universidad Icesi`, `Pontificia Universidad Javeriana`) |
| 2 | English form with the institution word last (`Stanford University`, `Massachusetts Institute of Technology`) |
| 3 | English form with the institution word first (`University of Michigan`) |

- Accepts: `Universidad Icesi`, `Stanford University`, `University of Michigan`
- Rejects: the line break after an institution (`Universidad Icesi\nPython`
  gives only `Universidad Icesi`)

## 7. Skills: common structure

The three skill patterns are built by the same function (`_skill_pattern` in
`patterns.py`):

```
(?<![\w.+#])(?:ALT1|ALT2|...)(?!\w)        (case-insensitive)
```

| Part | Recognizes |
|---|---|
| `(?<![\w.+#])` | The match cannot start in the middle of a word, after a dot, or after `+` / `#` (so `JS` is not found inside `Node.js`, nor `SQL` inside `MySQL`) |
| `(?:ALT1\|ALT2\|...)` | One spelling variant of a technology. Longer alternatives come first, so `SQL Server` is read before `SQL` and `Java Script` before `Java` |
| `(?!\w)` | The match cannot end in the middle of a longer word (`Java` is not found inside `JavaScript`) |

Stage 1 keeps each match **exactly as written** (`React.js`, `Postgres`); it
does not say that `ReactJS` and `React.js` are the same technology, that is
stage 2. Duplicates are removed ignoring case (`JS` and `js`), keeping the
first spelling.

## 8. Programming languages

Alternatives (each one is a regular expression; `[ ]?` is an optional space):

| Alternative | Spellings recognized |
|---|---|
| `java[ ]?script` | `JavaScript`, `Javascript`, `Java Script` |
| `ecmascript` | `ECMAScript` |
| `type[ ]?script` | `TypeScript`, `Type Script` |
| `js`, `ts` | `JS`, `TS` (any case) |
| `python3?` | `Python`, `Python3` |
| `java`, `kotlin`, `php`, `golang` | the language names |
| `c\+\+`, `c#` | `C++`, `C#` |
| `(?-i:Swift\|Rust\|Ruby\|Scala)` | only with a capital first letter, because `swift` or `rust` are ordinary English words |

Language: the set of spellings above, each as a whole word.
A match that lies inside a framework match (the `JS` of `Node JS`) is
discarded by `extract_languages`, so it is not reported as a language.

- Accepts: `JS`, `Javascript`, `Java Script`, `Python3`, `C++`
- Rejects: the `Java` inside `JavaScript`, the `JS` inside `React.js`

## 9. Frameworks and libraries

| Alternative | Spellings recognized |
|---|---|
| `react(?:[ .-]?js)?` | `React`, `React.js`, `ReactJS`, `React JS` |
| `angular(?:[ .-]?js)?`, `vue(?:[ .-]?js)?` | `Angular`, `AngularJS`, `Vue`, `Vue.js` |
| `next[ .-]?js`, `node[ .-]?js`, `express[ .-]?js` | `Next.js`, `NodeJS`, `Node.js`, `Node JS`, `ExpressJS` (the `js` is required, so a plain "node" is not matched) |
| `django`, `flask`, `fast[ ]?api` | `Django`, `Flask`, `FastAPI`, `Fast API` |
| `spring[ -]?boot` | `Spring Boot`, `SpringBoot`, `Spring-Boot` (plain "Spring" is not matched) |
| `pandas`, `num[ ]?py`, `sci[ -]?py` | `pandas`, `NumPy`, `Num Py`, `SciPy` |
| `scikit[ -]?learn`, `sklearn` | `Scikit-learn`, `scikit learn`, `scikit-learn`, `sklearn` |
| `tensor[ ]?flow`, `py[ ]?torch`, `keras` | `TensorFlow`, `Tensor Flow`, `PyTorch`, `Py Torch`, `Keras` |
| `matplotlib` | `Matplotlib` |

- Accepts: `React.js`, `NodeJS`, `scikit learn`, `Tensor Flow`
- Rejects: `a tree node` (no `js`), `Spring 2023`

## 10. Databases

| Alternative | Spellings recognized |
|---|---|
| `postgre[ ]?sql`, `postgres` | `PostgreSQL`, `Postgre SQL`, `Postgres` |
| `my[ ]?sql`, `maria[ ]?db` | `MySQL`, `My SQL`, `MariaDB` |
| `mongo[ ]?db`, `mongo` | `MongoDB`, `Mongo DB`, `Mongo` |
| `sql[ ]?server`, `sqlite` | `SQL Server`, `SQLServer`, `SQLite` |
| `no[ -]?sql` | `NoSQL`, `No SQL`, `No-SQL` |
| `redis`, `firebase` | `Redis`, `Firebase` |
| `sql` | `SQL` |

The order matters: `sql` is last, so `SQL Server` and `NoSQL` are matched as
a whole before the generic `SQL` can match part of them. Because of the
lookbehind, `SQL` is also never found inside `PostgreSQL` or `MySQL`.

- Accepts: `Postgres`, `Mongo DB`, `NoSQL`, `SQL`
- Rejects: the `SQL` inside `PostgreSQL`

## How `extract_education` combines them

It collects the matches of patterns 5 and 6, sorts them by position in the
text, collapses repeated spaces and removes duplicates. Result for
`Ingeniería de Sistemas y Computación, Universidad Icesi (2019 - 2024)`:

```python
["Ingeniería de Sistemas y Computación", "Universidad Icesi"]
```

## Known limitations

- Names are only detected in the first three non-empty lines or after a
  `Name:` label; a name written elsewhere is not found.
- Phone numbers must have ten digits; other national formats are not covered.
- Degree phrases stop at the first digit, comma or stop word, so a long program
  name can be cut at five words.
- If a degree is followed directly by an institution with no comma and no stop
  word (`Master of Science Stanford University`), the degree absorbs the first
  institution word and the institution also swallows the last degree word
  (`Master of Science Stanford` and `Science Stanford University`).

- Skills are searched in the whole text, not only in a "Technical Skills"
  section, so a technology mentioned in a job description is also extracted.
- Some technology names are also ordinary English words. Where possible the
  pattern requires an extra marker (`js` for Node, Express and Next; `boot` for
  Spring; a capital letter for Swift, Rust, Ruby and Scala), but a plain
  "react" or "angular" in a sentence is still reported as a framework.
- Technologies that are not in the lists are not detected. Adding one means
  adding an alternative in `patterns.py` (and its canonical form in stage 2).

## Tests

`tests/test_extraction_contact.py`, `tests/test_extraction_education.py` and
`tests/test_extraction_skills.py` cover every pattern with accepted and
rejected examples, and check the two assignment resumes end to end
(`examples/resumes/`).
