# Stage 2 - Normalization: design and variant dictionary

Implementation: `src/normalization/` (finite-state transducers with `pyformlang`).
Data: `src/normalization/variants.py`. Tests: `tests/test_normalization_*.py`.

Stage 2 receives the raw strings of stage 1 (`ExtractionResult.raw_skills()`)
and returns canonical tokens from `vocabulary.TOKENS`. Two spellings of the
same technology must give the same token (`JS` and `Javascript` give
`JAVASCRIPT`); a string with no known canonical form is dropped.

## 1. Model

Each raw string goes through two transducers, one after the other:

```
raw string --(C: cleaner)--> key --(D: dictionary)--> canonical token
 "Node.js"                  "NODEJS"                   NODE_JS
 "scikit learn"             "SCIKITLEARN"              SCIKIT_LEARN
```

| Transducer | Reads | Writes | What it does |
|---|---|---|---|
| **C**, cleaner (one for all) | characters of the raw string | characters of the key | Turns lower case into upper case, removes accents, deletes the separators (space, tab, `-`, `.`, `_`) and keeps letters, digits and `+` |
| **D**, dictionary (three of them) | characters of the key plus an end marker `⊣` | one canonical token | A prefix tree with one branch per spelling; it writes the token when the end marker arrives |

Why two machines instead of one big dictionary of raw spellings: `React.js`,
`React js`, `react-js` and `ReactJS` would need four branches, and every new
technology would multiply the cases (`Scikit-learn`, `scikit learn`,
`scikit_learn`, ...). With C in front, D only needs one branch per *key*, and
the stage is case-insensitive and tolerant to hyphens and spaces by
construction, not by a pile of special cases.

C and D are applied in sequence. Composing two transducers is a standard
operation (the composition of two rational relations is rational), but
`pyformlang` does not provide it, so `normalize` runs C and then D.

### The three dictionaries

D is split in three transducers, one per kind of qualification, so each one
can be defined, drawn and tested on its own:

| Transducer | Canonical tokens it writes | Module |
|---|---|---|
| `languages` | `LANGUAGE` tokens | `variants.LANGUAGE_VARIANTS` |
| `frameworks` | `FRONTEND`, `BACKEND`, `DATA_LIBRARY`, `ML_LIBRARY` tokens | `variants.FRAMEWORK_VARIANTS` |
| `databases_tools` | `DATABASE`, `VERSION_CONTROL`, `TOOL` and `CONCEPT` tokens | `variants.DATABASE_TOOL_VARIANTS` |

The three dictionaries have disjoint keys (checked by a test), so it does not
matter which one a string is tried on first: at most one of them accepts it.

### The end marker

A transducer in `pyformlang` writes output on its transitions, not in the
final state. Some spellings are a prefix of another one (`JAVA` and
`JAVASCRIPT`, `NODE` and `NODEJS`, `MONGO` and `MONGODB`), so writing the token
on the last letter would make the machine non-deterministic. Instead, D reads
one extra symbol `⊣` after the key and writes the token on that transition.
`normalize` appends `⊣` itself; it is never part of a spelling.

## 2. Reading a spelling

1. Run C on the raw string. If C has no transition for a character (`#`, `/`,
   `@`, an emoji), the string has no canonical form and is dropped.
2. Run D on the key followed by `⊣`. If D has no path for it, the string is
   dropped; otherwise D writes the token.

| Raw string | Key | Token |
|---|---|---|
| `JS`, `Javascript`, `Java Script`, `ECMAScript` | `JS`, `JAVASCRIPT`, `JAVASCRIPT`, `ECMASCRIPT` | `JAVASCRIPT` |
| `React.js`, `ReactJS`, `React JS` | `REACTJS` | `REACT` |
| `Postgres`, `PostgreSQL`, `Postgre SQL` | `POSTGRES`, `POSTGRESQL` | `POSTGRESQL` |
| `scikit learn`, `Scikit-learn`, `sklearn` | `SCIKITLEARN`, `SKLEARN` | `SCIKIT_LEARN` |
| `C#` | (rejected by C) | dropped |
| `Rust` | `RUST` (D has no branch) | dropped |

## 3. Variant dictionary

One entry per canonical token. A spelling is listed once per key, so
`Node.js`, `Node JS` and `node-js` appear as `NodeJS`. The order of the tokens
inside a category is the tie-break order used by the sorting step
(`docs/normalization-sorting.md`).

### 3.1 Languages

| Token | Spellings |
|---|---|
| `JAVASCRIPT` | `JS`, `JavaScript` (also `Java Script`), `ECMAScript` |
| `TYPESCRIPT` | `TS`, `TypeScript` (also `Type Script`) |
| `PYTHON` | `Python`, `Python3` |
| `JAVA` | `Java` |
| `KOTLIN` | `Kotlin` |
| `CPP` | `C++`, `CPP` |

### 3.2 Frameworks and libraries

| Token | Category | Spellings |
|---|---|---|
| `REACT` | frontend | `React`, `ReactJS` (also `React.js`, `React JS`) |
| `ANGULAR` | frontend | `Angular`, `AngularJS` |
| `VUE` | frontend | `Vue`, `VueJS` (also `Vue.js`) |
| `NEXT_JS` | frontend | `NextJS` (also `Next.js`) |
| `NODE_JS` | backend | `NodeJS` (also `Node.js`, `Node JS`, `Node js`) |
| `EXPRESS_JS` | backend | `ExpressJS` (also `Express.js`) |
| `DJANGO` | backend | `Django` |
| `FLASK` | backend | `Flask` |
| `FASTAPI` | backend | `FastAPI` (also `Fast API`) |
| `SPRING_BOOT` | backend | `SpringBoot` (also `Spring Boot`, `SPRING-BOOT`) |
| `PANDAS` | data library | `Pandas` |
| `NUMPY` | data library | `NumPy` (also `Num Py`) |
| `SCIKIT_LEARN` | ML library | `Scikit-learn` (also `scikit learn`), `sklearn` |
| `TENSORFLOW` | ML library | `TensorFlow` (also `Tensor Flow`) |
| `PYTORCH` | ML library | `PyTorch` (also `Py Torch`) |
| `KERAS` | ML library | `Keras` |

### 3.3 Databases, tools and concepts

| Token | Category | Spellings |
|---|---|---|
| `SQL` | database | `SQL` |
| `POSTGRESQL` | database | `PostgreSQL` (also `Postgre SQL`), `Postgres` |
| `MYSQL` | database | `MySQL` (also `My SQL`) |
| `MONGODB` | database | `MongoDB` (also `Mongo DB`), `Mongo` |
| `MARIADB` | database | `MariaDB` |
| `SQL_SERVER` | database | `SQL Server` |
| `SQLITE` | database | `SQLite` |
| `NOSQL` | database | `NoSQL` (also `No-SQL`) |
| `REDIS` | database | `Redis` |
| `FIREBASE` | database | `Firebase` |
| `GIT` | version control | `Git`, `GitHub`, `GitLab`, `Bitbucket` |
| `DOCKER` | tool | `Docker` |
| `KUBERNETES` | tool | `Kubernetes`, `K8s` |
| `JUPYTER` | tool | `Jupyter`, `Jupyter Notebook(s)`, `JupyterLab` |
| `REST_API` | concept | `REST API(s)`, `RESTful API(s)`, `RESTful`, `RESTful (web) service(s)`, `API(s) REST`, `API(s) RESTful` |
| `GRAPHQL` | concept | `GraphQL` |
| `MACHINE_LEARNING` | concept | `ML`, `machine learning` (with `model(s)` and/or `development`), `aprendizaje automático`, `aprendizaje de máquina(s)`, `aprendizaje profundo`, `deep learning`, `predictive model(s)`, `predictive modeling`, `modelo(s) predictivo(s)` |

## 4. Design decisions

These are the open questions of the team's hand-over notes, decided one by one.
Changing any of them means editing `vocabulary.py` and one dictionary entry;
the transducers are rebuilt from the dictionary.

| ID | Question | Decision | Reason |
|---|---|---|---|
| D1 | Technologies that stage 1 detects and the vocabulary did not have | Added `KOTLIN`, `CPP`, `NEXT_JS`, `EXPRESS_JS`, `FASTAPI`, `KERAS`, `REDIS`, `KUBERNETES`, `GRAPHQL`. Every database stage 1 detects also became a token (`MARIADB`, `SQL_SERVER`, `SQLITE`, `NOSQL`, `FIREBASE`) | The profiles ask for "a database" or "SQL or NoSQL", so any database must count; the others are named in the profile descriptions or are the usual member of their category (`Express.js` for backend, `Keras` for ML) |
| D2 | Detected technologies that stay out | Dropped (no token): `C#`, `PHP`, `Golang`, `Swift`, `Rust`, `Ruby`, `Scala`, `SciPy`, `Matplotlib`, `Jenkins`, `Jira`, `Postman`, `Linux`, `AWS`, `Azure`, `GCP`, `npm`, `webpack`, `Maven`, `Gradle`, `CI/CD`, `microservices`, `data processing (pipelines)` | No profile asks for them, and every token added to the alphabet is one more symbol for the automata of stage 3. If the professor's requirements for profiles 3 and 4 name any of them, add the token and one dictionary entry |
| D3 | `GitHub`, `GitLab`, `Bitbucket` | Normalized to `GIT` | They are hosting services for Git repositories; a candidate who lists one uses Git. Example: `laura_gomez.txt` writes `github` and never `Git` |
| D4 | Machine-learning concepts | `predictive models`, `deep learning` and the Spanish equivalents normalize to `MACHINE_LEARNING`; `data-processing pipelines` is dropped | The assignment describes an ML engineer as one who builds "predictive or learning-based models"; deep learning is a kind of machine learning; data processing alone says nothing about ML |
| D5 | Tokens whose category is not in the profile order | `sort_for_profile` puts them **last**, in vocabulary order | The automaton of a profile reads the relevant tokens first and only needs loops in its final states (see `docs/normalization-sorting.md`) |
| D6 | Several tokens of one category (`JAVASCRIPT` and `PYTHON`) | Stage 2 keeps all of them | Deciding which one satisfies a profile is stage 3's job; stage 2 only normalizes and orders |
| D7 | Candidate without a name | Not a stage 2 matter: the pipeline names the candidate `Unknown candidate` (see `docs/contracts.md`) | Stage 2 never sees the name |
| D8 | Order of the output of `normalize` | Order of first appearance in `raw_skills()` (languages, frameworks, databases, tools, concepts), no duplicates | Deterministic; the profile order is applied later by `sort_for_profile` |

## 5. Contract

| Function | Input | Output |
|---|---|---|
| `normalize(extracted)` | `ExtractionResult` | canonical tokens in `vocabulary.TOKENS`, no duplicates; strings with no canonical form are dropped |
| `sort_for_profile(tokens, profile)` | tokens, `Profile` | the same tokens in the order of `PROFILE_ORDER[profile]` |

Both are described with their formal definitions in
`docs/normalization-transducers.md` and `docs/normalization-sorting.md`.
