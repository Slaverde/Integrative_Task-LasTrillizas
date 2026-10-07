# Stage 1 - Extraction with regular expressions

Implementation: `src/extraction/` (Python `re` module). All patterns live in
`src/extraction/patterns.py`; `contact.py` and `education.py` apply them.

Stage 1 only **detects** text that may be a qualification or candidate data.
It does not decide whether two strings are equivalent (stage 2) nor whether the
candidate satisfies a profile (stage 3). Results are stored in the
`ExtractionResult` data class (`src/contracts.py`), keeping the order of
appearance and removing duplicates.

This document covers every type of information of stage 1: contact data,
academic qualifications, technical skills (languages, frameworks/libraries,
databases, tools), other qualifications (concepts) and professional experience.

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
`PhD`, `BSc`, `MSc`, `associate degree`, `ingeniería`,
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
\b(?:Universidad|Universidade|Instituto|Politécnico|Pontificia|Escuela|Fundación)(?:[ \t]+(?:de|del|la|los|las|y)\b)*(?:[ \t]+CAP)+(?:(?:[ \t]+(?:de|del|la|los|las|y)\b)+(?:[ \t]+CAP)+)*
| \b(?:CAP[ \t]+){1,3}(?:University|Institute|College)(?:[ \t]+of(?:[ \t]+CAP)+)?
| \b(?:University|Institute|College)[ \t]+of(?:[ \t]+CAP)+
```

with `CAP = [A-ZÁÉÍÓÚÑ][\w'’-]*`. Case-sensitive.

| Alternative | Recognizes |
|---|---|
| 1 | Spanish/Portuguese form: institution word, optional connectors (`de`, `de los`, `y`...), capitalized words, and more connector + capitalized-word groups (`Universidad Icesi`, `Pontificia Universidad Javeriana`, `Universidad de los Andes`, `Instituto Tecnológico de Cali`) |
| 2 | English form with the institution word last (`Stanford University`, `Massachusetts Institute of Technology`) |
| 3 | English form with the institution word first (`University of Michigan`) |

- Accepts: `Universidad Icesi`, `Stanford University`, `University of Michigan`
- Rejects: the line break after an institution (`Universidad Icesi\nPython`
  gives only `Universidad Icesi`)

## How `extract_education` combines them

It collects the matches of patterns 5 and 6, sorts them by position in the
text, collapses repeated spaces and removes duplicates. Result for
`Ingeniería de Sistemas y Computación, Universidad Icesi (2019 - 2024)`:

```python
["Ingeniería de Sistemas y Computación", "Universidad Icesi"]
```

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

## 11. Tools

Built with the same `_skill_pattern` structure as section 7.

| Alternative | Spellings recognized |
|---|---|
| `git[ ]?hub`, `git[ ]?lab`, `bit[ ]?bucket`, `git` | `GitHub`, `Git Hub`, `GitLab`, `Bitbucket`, `Git` (the longer names come before `git`) |
| `docker`, `kubernetes`, `k8s` | `Docker`, `Kubernetes`, `K8s` |
| `jenkins`, `jira`, `postman` | the tool names |
| `jupyter(?:[ ]?(?:notebooks?\|lab))?` | `Jupyter`, `Jupyter Notebook`, `JupyterLab` |
| `linux`, `aws`, `azure`, `gcp` | operating system and cloud platforms |
| `npm`, `webpack`, `maven`, `gradle` | build and package tools |
| `ci/cd` | `CI/CD` |

`extract_tools` discards a match that lies inside a link or an e-mail, so the
`github` of `github.com/ana` is reported as a link, not as a tool.

- Accepts: `Git`, `GitHub`, `Docker`, `Jupyter Notebook`, `CI/CD`
- Rejects: the `git` inside `digital`, the `github` inside `github.com/ana`

## 12. Other qualifications (concepts)

Practices and areas of knowledge that the profiles ask for and that are neither
a language nor a tool.

| Alternative | Spellings recognized |
|---|---|
| `rest(?:ful)?[ -]?apis?`, `apis?[ ]rest(?:ful)?` | `REST API`, `REST APIs`, `RESTful API`, `REST-API`, `API REST` |
| `restful(?:[ ]web)?[ ]services?`, `restful` | `RESTful services`, `RESTful web services`, `RESTful` |
| `graphql`, `microservices?` | `GraphQL`, `microservice(s)` |
| `machine[ -]learning(?:[ ]models?)?(?:[ ]development)?` | `machine learning`, `Machine-learning model development` |
| `aprendizaje[ ](?:autom[áa]tico\|de[ ]m[áa]quinas?\|profundo)` | `aprendizaje automático`, `aprendizaje de máquina`, `aprendizaje profundo` |
| `deep[ -]learning` | `deep learning` |
| `predictive[ ]model(?:s\|ing)?`, `modelos?[ ]predictivos?` | `predictive model(s)`, `predictive modeling`, `modelo(s) predictivo(s)` |
| `data[ -]processing(?:[ ]pipelines?)?` | `data processing`, `data-processing pipelines` |
| `(?-i:ML)` | only the capital abbreviation `ML` |

A plain `REST` is not matched because "rest" is an ordinary word; it needs
`API(s)` or the `ful` suffix. `ML` is case-sensitive so `html` and `xml` do not
match.

- Accepts: `REST APIs`, `machine learning`, `data-processing pipelines`, `ML`
- Rejects: `take a rest during the rest of the day`, `html`

## 13. Professional experience

### Years of experience

```
(?<![\w.])(\d{1,2}(?:[.,]\d)?|one|two|...|ten)\+?[ \t]*(?:years?|yrs?|años?)[ \t]+(?:(?:of|de)[ \t]+)?(?:(?:professional|work|relevant|industry|hands-on|profesional)[ \t]+)?(?:experience|experiencia)(?!\w)
```
(case-insensitive)

| Part | Recognizes |
|---|---|
| `(\d{1,2}(?:[.,]\d)?\|one\|...\|ten)` | The number, written with digits (`3`, `1.5`) or as a word up to ten. Group 1 |
| `\+?` | An optional `+` (`2+ years`) |
| `(?:years?\|yrs?\|años?)` | The unit in English or Spanish |
| `(?:(?:of\|de)[ \t]+)?` | Optional connector |
| `(?:professional\|work\|...)[ \t]+` | Optional qualifier before "experience" |
| `(?:experience\|experiencia)` | The word that makes the number mean experience |

`extract_experience_years` converts the number to `int` (`1.5` becomes `1`) and
returns the largest one found, or `None`.

- Accepts: `3 years of experience`, `2+ years of professional experience`,
  `4 años de experiencia`, `Five years of relevant experience`
- Rejects: `The company was founded 10 years ago` (no "experience")

### Experience statement

The same pattern followed by an optional description:

```
YEARS_PATTERN(?:[ \t]+(?:in|with|developing|building|using|as|working[ \t]+(?:in|with|on)|en|con|desarrollando)[ \t]+[^.\n;]+)?
```

The description stops at a period, a semicolon or the end of the line:
`3 years of experience developing web applications`.

### Job entry

```
\b(?:CAP[ \t]+){0,3}(?:Developer|Engineer|Analyst|Intern|Manager|Consultant|Architect|Scientist|Administrator|Designer|Desarrolladora?|Analista|Practicante|Pasante|Consultor|Arquitecto|Cient[ií]fico)\b(?:[ \t]+(?:at|en|@)[ \t]+CAP(?:[ \t]+CAP){0,3})?(?:[ \t]*[,(|–—-]*[ \t]*DATE_RANGE\)?)?
```

with `DATE_RANGE = (?:19|20)\d{2}[ \t]*[-–—][ \t]*(?:(?:19|20)\d{2}|present|current|presente|actualidad|actual)`.

| Part | Recognizes |
|---|---|
| `(?:CAP[ \t]+){0,3}` | Up to three capitalized words before the role (`Senior Backend`) |
| `(?:Developer\|Engineer\|...)` | A role word in English or Spanish |
| `(?:[ \t]+(?:at\|en\|@)[ \t]+CAP(...){0,3})?` | Optional company: `at Acme Corp` |
| `(?:...DATE_RANGE\)?)?` | Optional date range, with a separator or parenthesis before it |

- Accepts: `Senior Backend Developer at Acme Corp (2020 - 2023)`,
  `Data Analyst en Bancolombia, 2018-2020`, `Software Engineer Intern`
- Rejects: `I like to develop` (no role word)

`extract_experience` collects the statements and the job entries, sorts them by
position and removes duplicates.

## 14. Keeping the result

The assignment asks to keep the extracted information in a file or a data
structure. `extract` returns an `ExtractionResult` (the data structure), and
`src/extraction/storage.py` saves and loads it as UTF-8 JSON:

```python
from src.extraction import extract
from src.extraction.storage import save_json, load_json

result = extract(text)
save_json(result, "output/resume.json")
assert load_json("output/resume.json") == result
```

## Known limitations

- Names are only detected in the first three non-empty lines or after a
  `Name:` label; a name written elsewhere is not found.
- Phone numbers must have ten digits; other national formats are not covered.
- `Ingeniero/a de Sistemas` written as a title is not detected as a degree,
  because "Ingeniera de datos" is also a job title; only `Ingeniería ...` is.
  The institution is still found.
- Line endings (`\r\n`) are normalized at the start of `extract()`; the
  individual functions expect `\n`.
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
- Job entries need a role word from the list and a capitalized title; titles
  such as "Ninja" or lowercase roles are not found. Years of experience are
  read only from phrases that include the word "experience"/"experiencia".
- Technologies that are not in the lists are not detected. Adding one means
  adding an alternative in `patterns.py` (and its canonical form in stage 2).

## Tests

`tests/test_extraction_contact.py`, `tests/test_extraction_education.py`,
`tests/test_extraction_skills.py`, `tests/test_extraction_experience.py` and
`tests/test_extraction_tools_concepts.py` cover every pattern with accepted and
rejected examples, a full resume with every field, the JSON round trip and the
two assignment resumes end to end (`examples/resumes/`).
