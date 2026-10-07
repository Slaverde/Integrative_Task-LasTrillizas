# Stage 1 - Test cases and scenarios

Tests: `tests/test_extraction_*.py` (run with `python -m pytest`).
Input resumes: `examples/resumes/`.

The goal is to check, for each type of information, that the regular
expressions accept what they should, reject what they should not, and that
the whole stage behaves well on complete resumes and on hostile input.

## 1. Unit cases per pattern

| ID | Pattern | Input | Expected | Test file |
|---|---|---|---|---|
| E1 | E-mail | `john.doe+cv@mail.example.com` | found | `test_extraction_contact.py` |
| E2 | E-mail | `write to ana@icesi.edu.co.` | `ana@icesi.edu.co`, no final dot | `test_extraction_contact.py` |
| E3 | E-mail | `ana@localhost` | nothing | `test_extraction_education.py` |
| T1 | Phone | `+57 300 123 4567`, `300-123-4567`, `3001234567`, `+1 (415) 555-2671` | all found | `test_extraction_contact.py` |
| T2 | Phone | `2019-2023`, `12345`, 14 digits | nothing | `test_extraction_contact.py` |
| L1 | Link | `(https://ana.dev/projects),` | URL without `)` and `,` | `test_extraction_contact.py` |
| L2 | Link | `ana@github.com` | nothing | `test_extraction_contact.py` |
| N1 | Name | `Wednesday Addams` on the first line | found | `test_extraction_contact.py` |
| N2 | Name | `Curriculum Vitae` then `Ana Pérez` | `Ana Pérez` | `test_extraction_contact.py` |
| N3 | Name | `3 years of experience` | `None` | `test_extraction_contact.py` |
| D1 | Degree | `Bachelor of Science in Computer Science from Stanford University` | degree and institution | `test_extraction_education.py` |
| D2 | Degree | `Certified Scrum Master` | nothing | `test_extraction_education.py` |
| I1 | Institution | `Universidad Icesi\nPython` | `Universidad Icesi`, line break respected | `test_extraction_education.py` |
| S1 | Language | `Javascript` | only `Javascript`, not `Java` | `test_extraction_skills.py` |
| S2 | Framework | `Node JS, React.js, NodeJS` | frameworks only, no language `JS` | `test_extraction_skills.py` |
| S3 | Framework | `a tree node` | nothing | `test_extraction_skills.py` |
| S4 | Database | `PostgreSQL`, `MySQL, NoSQL` | no extra `SQL` | `test_extraction_skills.py` |
| H1 | Tool | `github.com/ana, ana@gitlab.com` | no tool | `test_extraction_tools_concepts.py` |
| C1 | Concept | `take a rest during the rest of the day` | nothing | `test_extraction_tools_concepts.py` |
| C2 | Concept | `html xml ml` | nothing (`ML` is case-sensitive) | `test_extraction_tools_concepts.py` |
| X1 | Experience | `4 años de experiencia`, `Five years of relevant experience` | 4 and 5 | `test_extraction_experience.py` |
| X2 | Experience | `The company was founded 10 years ago` | `None` | `test_extraction_experience.py` |
| X3 | Experience | `Data Analyst en Bancolombia, 2018-2020` | job entry with company and dates | `test_extraction_experience.py` |

## 2. Scenarios (complete resumes)

Each scenario runs `extract()` on a full resume and compares **every field**
of `ExtractionResult` with the expected value (`test_extraction_resumes.py`).

| Scenario | Resume | What it checks |
|---|---|---|
| A. Full Stack from the assignment | `wednesday_addams.txt` | `JS`, `React.js`, `NodeJS`, `Postgres`, `Git` and 3 years |
| B. ML Engineer from the assignment | `mary_jane_watson.txt` | Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git; concepts `predictive models` and `data-processing pipelines` |
| C. Full Stack with many spellings | `ana_torres.txt` | `Javascript`, `ReactJS`, `Node js`, `Mongo DB`, `REST API`, a Spanish degree and institution |
| D. Backend, English, messy format | `carlos_ruiz.txt` | Bullets, upper-case skills (`SPRING-BOOT`, `GIT`), `+1 (415) ...`, a link ending in a period, `6+ years`, job with dates |
| E. Data profile in Spanish | `laura_gomez.txt` | Accents, all-caps name, `Universidad de los Andes`, `Analista de Datos en Bancolombia`, `modelos predictivos` |
| F. No technical skills | `sofia_nunez.txt` | Contact and experience are found, every skill list is empty (used later to check rejection) |

## 3. Invariants (must hold for any resume)

| ID | Property |
|---|---|
| P1 | Every extracted skill appears in the original text |
| P2 | A skill is never reported in two categories |
| P3 | No list has duplicates (ignoring case) |
| P4 | Extracting the same text twice gives the same result |
| P5 | Windows line endings (`\r\n`) give the same result as `\n` |
| P6 | The order of the skills in the resume does not change what is found |
| P7 | Letter case does not change which skills are found |
| P8 | Extra spaces, tabs and blank lines do not change the result |
| P9 | Every example resume in `examples/resumes/` has an expected result |

## 4. Robustness cases

| ID | Input | Expected |
|---|---|---|
| R1 | `""`, `" "`, `"\n\n"`, `"\t \r\n"` | empty result, name and years are `None` |
| R2 | Prose with `rest`, `swift`, `rust`, `react` as ordinary words | no database, language, concept or tool |
| R3 | 5000 repetitions of a skills line | processed, no duplicates |
| R4 | 20000 `A`, thousands of `Universidad ` and `a.` | finishes (no catastrophic backtracking) |

## 5. Persistence

| ID | Case | Expected |
|---|---|---|
| J1 | `save_json` then `load_json` | the loaded result equals the original; the file is UTF-8 and keeps accents |

## 6. Bugs found while designing these cases

They were fixed and are now covered by the tests above.

| Bug | Cause | Fix |
|---|---|---|
| `Nombre: Juan Pérez` not found with Windows line endings | the `\r` before `\n` blocked the end-of-line match | `extract()` normalizes line endings and the pattern accepts `\r` |
| `Ingeniera de datos` reported as a degree | `ingeniero/a` was a degree keyword, but it is also a job title | removed from the degree keywords |
| `Analista de Datos en Bancolombia` reported only as `Analista` | Spanish roles put the specialty after the role | the job pattern accepts `de ...` after the role |
| `Universidad de los Andes` not found | the connector `de los` was followed by a lowercase word | the institution pattern accepts several connectors |
