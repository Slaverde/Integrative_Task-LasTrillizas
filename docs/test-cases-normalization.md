# Stage 2 - Test cases and scenarios

Tests: `tests/test_normalization_*.py` (run with `python -m pytest`).
Input resumes: `examples/resumes/`.

The goal is to check that every spelling that stage 1 can report gets a decision
(a canonical token, or a conscious drop), that the transducers accept what they
should and reject what they should not, that the sorting does not depend on the
order of the resume, and that the diagrams and tables of the documents are the
ones the code produces.

## 1. Unit cases per transducer

| ID | Machine | Input | Expected | Test file |
|---|---|---|---|---|
| C1 | Cleaner | `Node.js`, `Node JS`, `NodeJS` | the key `NODEJS` for the three | `test_normalization_cleaner.py` |
| C2 | Cleaner | `Scikit-learn`, `scikit learn` | `SCIKITLEARN` | `test_normalization_cleaner.py` |
| C3 | Cleaner | `aprendizaje automático`, `APRENDIZAJE AUTOMÁTICO` | `APRENDIZAJEAUTOMATICO` | `test_normalization_cleaner.py` |
| C4 | Cleaner | `C++` | `C++` (the `+` is kept) | `test_normalization_cleaner.py` |
| C5 | Cleaner | `C#`, `CI/CD`, `node@12`, `🙂`, a line break | rejected | `test_normalization_cleaner.py` |
| C6 | Cleaner | every single character up to `U+024F` | same answer as the reference function `variant_key` | `test_normalization_cleaner.py` |
| C7 | Cleaner | a text of more than 100 characters | rejected at once | `test_normalization_cleaner.py` |
| L1 | Languages | `JS`, `Javascript`, `Java Script`, `ECMAScript` | `JAVASCRIPT` | `test_normalization_languages.py` |
| L2 | Languages | `Java` and `JavaScript` | `JAVA` and `JAVASCRIPT` (one is a prefix of the other) | `test_normalization_languages.py` |
| L3 | Languages | `C++`, `c++`, `CPP` | `CPP` | `test_normalization_languages.py` |
| L4 | Languages | `JAV`, `Javascripts`, `JS2`, `J S S` | rejected | `test_normalization_languages.py` |
| L5 | Languages | `Rust`, `C#`, `Go`, `React` | rejected (dropped by design, or another kind of skill) | `test_normalization_languages.py` |
| F1 | Frameworks | `React.js`, `ReactJS`, `React JS`, `react-js` | `REACT` | `test_normalization_frameworks.py` |
| F2 | Frameworks | `NodeJS`, `Node.js`, `Node JS`, `Node js` | `NODE_JS` | `test_normalization_frameworks.py` |
| F3 | Frameworks | `sklearn`, `scikit learn`, `Scikit-learn` | `SCIKIT_LEARN` | `test_normalization_frameworks.py` |
| F4 | Frameworks | `Tensor Flow`, `Py Torch`, `Num Py` | `TENSORFLOW`, `PYTORCH`, `NUMPY` | `test_normalization_frameworks.py` |
| F5 | Frameworks | `Rea`, `Node`, `Scikit`, `Reactive` | rejected (prefix or extra letters) | `test_normalization_frameworks.py` |
| F6 | Frameworks | `SciPy`, `Matplotlib` | rejected (dropped by design) | `test_normalization_frameworks.py` |
| F7 | Frameworks | `JS` | rejected here; the language transducer accepts it | `test_normalization_frameworks.py` |
| B1 | Databases and tools | `Postgres`, `PostgreSQL`, `Postgre SQL` | `POSTGRESQL` | `test_normalization_databases_tools.py` |
| B2 | Databases and tools | `Mongo`, `MongoDB`, `Mongo DB` | `MONGODB` | `test_normalization_databases_tools.py` |
| B3 | Databases and tools | `SQL`, `SQL Server`, `NoSQL`, `SQLite` | four different tokens | `test_normalization_databases_tools.py` |
| B4 | Databases and tools | `Git`, `GitHub`, `GitLab`, `Bitbucket` | `GIT` (decision D3) | `test_normalization_databases_tools.py` |
| B5 | Databases and tools | `REST API`, `RESTful`, `API REST`, `RESTful web services` | `REST_API` | `test_normalization_databases_tools.py` |
| B6 | Databases and tools | `Machine-learning model development`, `ML`, `aprendizaje profundo`, `predictive modeling` | `MACHINE_LEARNING` (decision D4) | `test_normalization_databases_tools.py` |
| B7 | Databases and tools | `REST`, `API`, `machine`, `deep`, `Jenkins`, `AWS`, `CI/CD`, `microservices` | rejected | `test_normalization_databases_tools.py` |
| B8 | Databases and tools | `Git`, `GitHub`, `GitLab`, `Bitbucket` | four keys end in the same final state `f:GIT` | `test_normalization_databases_tools.py` |

## 2. Shape of the machines

| ID | Property | Test file |
|---|---|---|
| M1 | The cleaner has one state, initial and final | `test_normalization_cleaner.py` |
| M2 | The cleaner and the three dictionaries are deterministic | `test_normalization_cleaner.py`, `..._languages.py`, `..._frameworks.py`, `..._databases_tools.py` |
| M3 | A dictionary has one final state per token and one path per key | the three dictionary test files |
| M4 | The output alphabet of a dictionary is exactly its set of tokens, and they belong to the categories of its group | the three dictionary test files |
| M5 | Only the end marker transitions write output | `test_normalization_languages.py` |
| M6 | A spelling is accepted by one dictionary only | the three dictionary test files |

## 3. Variant dictionary

| ID | Property | Test file |
|---|---|---|
| V1 | Every token of the dictionary is in the vocabulary, and every token of the vocabulary can be produced | `test_normalization_variants.py` |
| V2 | A token is in one group only | `test_normalization_variants.py` |
| V3 | Two spellings with the same key are an error (`key_map`), inside a group and between groups | `test_normalization_variants.py` |
| V4 | The examples of the assignment (`JS`, `React.js`, `NodeJS`, `Postgres`, `sklearn`, `Tensor Flow`, `Py Torch`) are in the dictionary | `test_normalization_variants.py` |

## 4. Scenarios (complete resumes)

Each scenario runs stage 1 and `normalize` on a full resume and compares the
tokens and the strings that are dropped (`test_normalization_resumes.py`).

| Scenario | Resume | Tokens | Dropped |
|---|---|---|---|
| A. Full Stack from the assignment | `wednesday_addams.txt` | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` | none |
| B. ML Engineer from the assignment | `mary_jane_watson.txt` | `PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT, MACHINE_LEARNING` | `data-processing pipelines` |
| C. Full Stack, many spellings | `ana_torres.txt` | `GitHub` joins `Git`; `ReactJS`, `Node js`, `Mongo DB` are normalized | `Postman` |
| D. Backend, English, messy | `carlos_ruiz.txt` | `Spring Boot` and `SPRING-BOOT` give one token, so do `REST APIs` and `RESTful APIs` | `CI/CD`, `Jenkins`, `microservices` |
| E. Data profile in Spanish | `laura_gomez.txt` | lower case (`python`, `numpy`, `mongo db`) and `github` give tokens; `modelos predictivos` gives `MACHINE_LEARNING` | none |
| F. No technical skills | `sofia_nunez.txt` | none | none |

## 5. Every spelling of stage 1

`test_normalization_resumes.py` has a table with one row for every spelling that
the patterns of stage 1 report (`docs/extraction-regex.md`, sections 8 to 12),
more than 110 rows. For each one the test checks two things: that stage 1 really
reports it in that field, and that stage 2 gives the token written in the table
or drops it. If someone adds a pattern to stage 1 and forgets stage 2, the
dictionary has to be updated; the table is where the decision is written.

## 6. Properties (must hold for any input)

| ID | Property |
|---|---|
| P1 | Normalizing a token gives the same token (`normalize_skill("NODE_JS") == "NODE_JS"`) |
| P2 | Letter case does not change the result |
| P3 | Separators (space, tab, `-`, `.`, `_`) between any two characters, or around the text, do not change the result |
| P4 | Accents do not change the result |
| P5 | A proper prefix of a spelling, or a spelling with an extra letter, is not accepted |
| P6 | The output of `normalize` has only vocabulary tokens and no duplicates |
| P7 | The order of the skills in the resume does not change the sorted sequence of any profile (the 120 orders of the five skills of Scenario A) |
| P8 | The field in which stage 1 put a string does not change its token |

## 7. Robustness cases

| ID | Input | Expected |
|---|---|---|
| R1 | `""`, `"   "`, `"-"` | dropped, no error |
| R2 | 3000 random strings with letters, digits, symbols, accents, tabs, line breaks and an emoji | never raise; the answer is a token or `None` |
| R3 | `"A" * 20000`, `"JS" + " " * 20000` | dropped in well under a second (limit of 100 characters) |
| R4 | `None` | `TypeError`, not a wrong answer |

## 8. Sorting

| ID | Case | Expected | Test file |
|---|---|---|---|
| S1 | `GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT` for Full Stack | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` | `test_normalization_sorting.py` |
| S2 | the ML example of the assignment | `PYTHON, PANDAS, NUMPY, SCIKIT_LEARN, TENSORFLOW, SQL, GIT` | `test_normalization_sorting.py` |
| S3 | the same tokens for two profiles | a different order for each | `test_normalization_sorting.py` |
| S4 | tokens of a category the profile does not list | after the listed ones, in vocabulary order | `test_normalization_sorting.py` |
| S5 | `PYTHON, JAVA, TYPESCRIPT, JAVASCRIPT` | vocabulary order inside the category | `test_normalization_sorting.py` |
| S6 | all 6! orders of 6 tokens, for the 4 profiles | the same result | `test_normalization_sorting.py` |
| S7 | sorting a sorted list; 25 random subsets per profile | no change | `test_normalization_sorting.py` |
| S8 | `RUST`, `javascript` | `ValueError` | `test_normalization_sorting.py` |

## 9. Documents in sync with the code

| ID | Check | Test file |
|---|---|---|
| D1 | The Mermaid diagrams and the table of sizes in `docs/normalization-transducers.md` are the ones generated from the machines | `test_normalization_docs.py` |
| D2 | Every key of every dictionary is listed in that document | `test_normalization_docs.py` |

If D1 fails, run `python -m src.normalization.diagrams <name>` and paste the new
block in the document.
