# Stage 2 - Transducers: formal definitions and diagrams

Implementation: `src/normalization/fst.py` (builders), `transducers.py` (the
three dictionaries) and `variants.py` (the data). The diagrams of this file are
generated from the machines of the code with
`python -m src.normalization.diagrams`, and a test checks that they are up to
date (`tests/test_normalization_docs.py`).

The design (why two kinds of machines, the dictionary of variants and the
decisions taken) is in `docs/normalization-design.md`. Sorting is not done by a
transducer; see `docs/normalization-sorting.md`.

## 1. Notation

Every transducer is a 7-tuple, as in the assignment:

```
M = (Q, Σ, Γ, δ, ω, q0, F)
```

| Symbol | Meaning |
|---|---|
| Q | finite set of states |
| Σ | input alphabet |
| Γ | output alphabet |
| δ | transition function `δ: Q × Σ → Q` (partial: a missing transition rejects) |
| ω | output function `ω: Q × Σ → Γ*`, the string written when the transition `δ(q, a)` is taken |
| q0 | initial state |
| F | set of accepting states |

A run **accepts** a string if it reads all of it and stops in F. The output of
the run is the concatenation of the `ω` of every transition it took. A string
that is not accepted has no output.

**Correspondence with `pyformlang`.** The library does not keep δ and ω apart:
`fst.add_transition(q, a, q2, [x1, x2])` records both `δ(q, a) = q2` and
`ω(q, a) = x1 x2` (the list can be empty, which is `ε`). `fst.translate(word)`
returns the outputs of all the accepting runs, and nothing if there is none.
All our machines are deterministic (`is_deterministic` is tested), so there is
at most one output.

| Formal element | In the code |
|---|---|
| Q | `fst.states` |
| Σ, Γ | `fst.input_symbols`, `fst.output_symbols` |
| δ and ω | `fst.transitions`: `(q, a) -> [(q2, [outputs])]` |
| q0 | `fst.start_states` |
| F | `fst.final_states` |

## 2. Sizes

| Transducer | \|Q\| | \|Σ\| | \|Γ\| | \|δ\| | \|F\| |
|---|---|---|---|---|---|
| C (cleaner) | 1 | 112 | 37 | 112 | 1 |
| languages | 57 | 20 | 6 | 61 | 6 |
| frameworks | 132 | 25 | 16 | 135 | 16 |
| databases_tools | 332 | 27 | 17 | 370 | 17 |

## 3. Transducer C: the cleaner

It reads a raw string and writes its key. It has a single state that is
initial and final, and a loop on every symbol of Σ.

| Element | Definition |
|---|---|
| Q | {`q0`} |
| Σ | `a-z`, `A-Z`, `0-9`, `+`, the separators ` ` (space), tab, `-`, `.`, `_`, and the accented letters `áàäâéèëêíìïîóòöôúùüûñçÁÀÄÂÉÈËÊÍÌÏÎÓÒÖÔÚÙÜÛÑÇ` |
| Γ | `A-Z`, `0-9`, `+` |
| δ | `δ(q0, a) = q0` for every `a` in Σ |
| ω | `ω(q0, a)` = the upper-case letter for `a-z`; `a` itself for `A-Z`, `0-9` and `+`; `ε` for a separator; the letter without accent, in upper case, for an accented letter (`á -> A`, `ñ -> N`, `Ü -> U`) |
| q0 | `q0` |
| F | {`q0`} |

```mermaid
flowchart LR
    q0((("q0")))
    q0 -->|"a-z / A-Z"| q0
    q0 -->|"A-Z 0-9 + / same symbol"| q0
    q0 -->|"space tab - . _ / ε"| q0
    q0 -->|"accented letter / plain upper-case letter"| q0
```

What the state remembers: nothing. C does not need memory, it only rewrites one
character at a time, so one state is enough.

| Input | Run | Output |
|---|---|---|
| `Node.js` | N→N, o→O, d→D, e→E, `.`→ε, j→J, s→S | `NODEJS` |
| `scikit learn` | s→S, c→C, ..., t→T, space→ε, l→L, ..., n→N | `SCIKITLEARN` |
| `aprendizaje automático` | ..., space→ε, ..., á→A, ... | `APRENDIZAJEAUTOMATICO` |
| `C++` | C→C, +→+, +→+ | `C++` |
| `C#` | C→C, then no transition for `#` | rejected |
| `CI/CD` | C→C, I→I, then no transition for `/` | rejected |

## 4. Transducers D: the dictionaries

The three dictionaries have the same shape. Given a table of keys
`K = {(key, token)}` (the `key_map` of the group):

| Element | Definition |
|---|---|
| Q | `q0`, `p:w` for every non-empty prefix `w` of a key (the whole key included), `f:t` for every token `t` |
| Σ | the letters that appear in the keys, and the end marker `⊣` |
| Γ | the tokens of the table |
| δ | `δ(q0, a) = p:a`; `δ(p:w, a) = p:wa` if `wa` is a prefix of a key; `δ(p:k, ⊣) = f:t` for every `(k, t)` in K |
| ω | `ε` on every letter; `t` on the transition `(p:k, ⊣)` |
| q0 | `q0` |
| F | `{f:t}` for every token `t` |

The machine is a prefix tree. A state `p:w` remembers the prefix `w` that has
been read so far, and nothing else. Two keys of the same token end in the same
final state `f:t`, which is why the token is written on the end marker and not
on the last letter: `JAVA` and `JAVASCRIPT` share the path `J-A-V-A`, and only
the next symbol (`⊣` or `S`) tells them apart.

The diagrams are the **compact** form of the prefix tree: a state with one way
in and one way out is folded into its edge, so `S⊣ / JAVASCRIPT` on an edge is
the path `S`, `⊣` that writes `JAVASCRIPT`, and an edge labelled `AVA` is three
transitions that write nothing. Branching states, `q0` and the final states
are drawn. The full machine (for example `JS`) is:

```
q0 --J/ε--> p:J --S/ε--> p:JS --⊣/JAVASCRIPT--> f:JAVASCRIPT
```

### 4.1 `languages`

| Element | Definition |
|---|---|
| Q | `q0`, `p:w` for every non-empty prefix `w` of a key (the whole key included) and `f:t` for every token `t` of Γ. 57 states |
| Σ | {+, 3, A, C, E, H, I, J, K, L, M, N, O, P, R, S, T, V, Y, ⊣} |
| Γ | {`JAVASCRIPT`, `TYPESCRIPT`, `PYTHON`, `JAVA`, `KOTLIN`, `CPP`} |
| δ | `δ(q0, a) = p:a`; `δ(p:w, a) = p:wa` when `wa` is a prefix of a key; `δ(p:k, ⊣) = f:t` for every key `k` of the table below with token `t`. 61 transitions |
| ω | `ω(q, a) = ε` for a letter `a`; `ω(p:k, ⊣) = t` for the same pairs `(k, t)` |
| q0 | `q0` |
| F | {`f:t` : `t` in Γ}, 6 states |

Keys of the table:

| Token | Keys read before `⊣` |
|---|---|
| `JAVASCRIPT` | `ECMASCRIPT`, `JAVASCRIPT`, `JS` |
| `TYPESCRIPT` | `TS`, `TYPESCRIPT` |
| `PYTHON` | `PYTHON`, `PYTHON3` |
| `JAVA` | `JAVA` |
| `KOTLIN` | `KOTLIN` |
| `CPP` | `C++`, `CPP` |

```mermaid
flowchart LR
    n0((("f:CPP")))
    n1((("f:JAVA")))
    n2((("f:JAVASCRIPT")))
    n3((("f:KOTLIN")))
    n4((("f:PYTHON")))
    n5((("f:TYPESCRIPT")))
    n6("p:C")
    n7("p:J")
    n8("p:JAVA")
    n9("p:PYTHON")
    n10("p:T")
    n11(("q0"))
    n6 -->|"++⊣ / CPP"| n0
    n6 -->|"PP⊣ / CPP"| n0
    n7 -->|"AVA"| n8
    n7 -->|"S⊣ / JAVASCRIPT"| n2
    n8 -->|"SCRIPT⊣ / JAVASCRIPT"| n2
    n8 -->|"⊣ / JAVA"| n1
    n9 -->|"3⊣ / PYTHON"| n4
    n9 -->|"⊣ / PYTHON"| n4
    n10 -->|"S⊣ / TYPESCRIPT"| n5
    n10 -->|"YPESCRIPT⊣ / TYPESCRIPT"| n5
    n11 -->|"C"| n6
    n11 -->|"ECMASCRIPT⊣ / JAVASCRIPT"| n2
    n11 -->|"J"| n7
    n11 -->|"KOTLIN⊣ / KOTLIN"| n3
    n11 -->|"PYTHON"| n9
    n11 -->|"T"| n10
```

| Input | C writes | D run | Output |
|---|---|---|---|
| `JS` | `JS` | `q0 -J-> p:J -S-> p:JS -⊣/JAVASCRIPT-> f:JAVASCRIPT` | `JAVASCRIPT` |
| `Java Script` | `JAVASCRIPT` | `q0 -J-> p:J -A-> ... -T-> p:JAVASCRIPT -⊣/JAVASCRIPT-> f:JAVASCRIPT` | `JAVASCRIPT` |
| `Java` | `JAVA` | `q0 -J-> p:J -A-> p:JA -V-> p:JAV -A-> p:JAVA -⊣/JAVA-> f:JAVA` | `JAVA` |
| `JAV` | `JAV` | stops in `p:JAV`, which has no `⊣` transition | rejected |
| `Rust` | `RUST` | `q0` has no transition on `R` | rejected |

### 4.2 `frameworks`

| Element | Definition |
|---|---|
| Q | `q0`, `p:w` for every non-empty prefix `w` of a key (the whole key included) and `f:t` for every token `t` of Γ. 132 states |
| Σ | {A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, R, S, T, U, V, W, X, Y, ⊣} |
| Γ | {`REACT`, `ANGULAR`, `VUE`, `NEXT_JS`, `NODE_JS`, `EXPRESS_JS`, `DJANGO`, `FLASK`, `FASTAPI`, `SPRING_BOOT`, `PANDAS`, `NUMPY`, `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH`, `KERAS`} |
| δ | `δ(q0, a) = p:a`; `δ(p:w, a) = p:wa` when `wa` is a prefix of a key; `δ(p:k, ⊣) = f:t` for every key `k` of the table below with token `t`. 135 transitions |
| ω | `ω(q, a) = ε` for a letter `a`; `ω(p:k, ⊣) = t` for the same pairs `(k, t)` |
| q0 | `q0` |
| F | {`f:t` : `t` in Γ}, 16 states |

Keys of the table:

| Token | Keys read before `⊣` |
|---|---|
| `REACT` | `REACT`, `REACTJS` |
| `ANGULAR` | `ANGULAR`, `ANGULARJS` |
| `VUE` | `VUE`, `VUEJS` |
| `NEXT_JS` | `NEXTJS` |
| `NODE_JS` | `NODEJS` |
| `EXPRESS_JS` | `EXPRESSJS` |
| `DJANGO` | `DJANGO` |
| `FLASK` | `FLASK` |
| `FASTAPI` | `FASTAPI` |
| `SPRING_BOOT` | `SPRINGBOOT` |
| `PANDAS` | `PANDAS` |
| `NUMPY` | `NUMPY` |
| `SCIKIT_LEARN` | `SCIKITLEARN`, `SKLEARN` |
| `TENSORFLOW` | `TENSORFLOW` |
| `PYTORCH` | `PYTORCH` |
| `KERAS` | `KERAS` |

```mermaid
flowchart LR
    n0((("f:ANGULAR")))
    n1((("f:DJANGO")))
    n2((("f:EXPRESS_JS")))
    n3((("f:FASTAPI")))
    n4((("f:FLASK")))
    n5((("f:KERAS")))
    n6((("f:NEXT_JS")))
    n7((("f:NODE_JS")))
    n8((("f:NUMPY")))
    n9((("f:PANDAS")))
    n10((("f:PYTORCH")))
    n11((("f:REACT")))
    n12((("f:SCIKIT_LEARN")))
    n13((("f:SPRING_BOOT")))
    n14((("f:TENSORFLOW")))
    n15((("f:VUE")))
    n16("p:ANGULAR")
    n17("p:F")
    n18("p:N")
    n19("p:P")
    n20("p:REACT")
    n21("p:S")
    n22("p:VUE")
    n23(("q0"))
    n16 -->|"JS⊣ / ANGULAR"| n0
    n16 -->|"⊣ / ANGULAR"| n0
    n17 -->|"ASTAPI⊣ / FASTAPI"| n3
    n17 -->|"LASK⊣ / FLASK"| n4
    n18 -->|"EXTJS⊣ / NEXT_JS"| n6
    n18 -->|"ODEJS⊣ / NODE_JS"| n7
    n18 -->|"UMPY⊣ / NUMPY"| n8
    n19 -->|"ANDAS⊣ / PANDAS"| n9
    n19 -->|"YTORCH⊣ / PYTORCH"| n10
    n20 -->|"JS⊣ / REACT"| n11
    n20 -->|"⊣ / REACT"| n11
    n21 -->|"CIKITLEARN⊣ / SCIKIT_LEARN"| n12
    n21 -->|"KLEARN⊣ / SCIKIT_LEARN"| n12
    n21 -->|"PRINGBOOT⊣ / SPRING_BOOT"| n13
    n22 -->|"JS⊣ / VUE"| n15
    n22 -->|"⊣ / VUE"| n15
    n23 -->|"ANGULAR"| n16
    n23 -->|"DJANGO⊣ / DJANGO"| n1
    n23 -->|"EXPRESSJS⊣ / EXPRESS_JS"| n2
    n23 -->|"F"| n17
    n23 -->|"KERAS⊣ / KERAS"| n5
    n23 -->|"N"| n18
    n23 -->|"P"| n19
    n23 -->|"REACT"| n20
    n23 -->|"S"| n21
    n23 -->|"TENSORFLOW⊣ / TENSORFLOW"| n14
    n23 -->|"VUE"| n22
```

| Input | C writes | D run | Output |
|---|---|---|---|
| `Node.js` | `NODEJS` | `q0 -N-> p:N -O-> ... -S-> p:NODEJS -⊣/NODE_JS-> f:NODE_JS` | `NODE_JS` |
| `sklearn` | `SKLEARN` | `q0 -S-> p:S -K-> ... -⊣/SCIKIT_LEARN-> f:SCIKIT_LEARN` | `SCIKIT_LEARN` |
| `scikit learn` | `SCIKITLEARN` | `q0 -S-> p:S -C-> ... -⊣/SCIKIT_LEARN-> f:SCIKIT_LEARN` | `SCIKIT_LEARN` |
| `Scikit` | `SCIKIT` | stops in `p:SCIKIT`, no `⊣` transition | rejected |
| `SciPy` | `SCIPY` | `p:SCI` has no transition on `P` | rejected |

### 4.3 `databases_tools`

| Element | Definition |
|---|---|
| Q | `q0`, `p:w` for every non-empty prefix `w` of a key (the whole key included) and `f:t` for every token `t` of Γ. 332 states |
| Σ | {8, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, Y, Z, ⊣} |
| Γ | {`SQL`, `POSTGRESQL`, `MYSQL`, `MONGODB`, `MARIADB`, `SQL_SERVER`, `SQLITE`, `NOSQL`, `REDIS`, `FIREBASE`, `GIT`, `DOCKER`, `KUBERNETES`, `JUPYTER`, `REST_API`, `GRAPHQL`, `MACHINE_LEARNING`} |
| δ | `δ(q0, a) = p:a`; `δ(p:w, a) = p:wa` when `wa` is a prefix of a key; `δ(p:k, ⊣) = f:t` for every key `k` of the table below with token `t`. 370 transitions |
| ω | `ω(q, a) = ε` for a letter `a`; `ω(p:k, ⊣) = t` for the same pairs `(k, t)` |
| q0 | `q0` |
| F | {`f:t` : `t` in Γ}, 17 states |

Keys of the table:

| Token | Keys read before `⊣` |
|---|---|
| `SQL` | `SQL` |
| `POSTGRESQL` | `POSTGRES`, `POSTGRESQL` |
| `MYSQL` | `MYSQL` |
| `MONGODB` | `MONGO`, `MONGODB` |
| `MARIADB` | `MARIADB` |
| `SQL_SERVER` | `SQLSERVER` |
| `SQLITE` | `SQLITE` |
| `NOSQL` | `NOSQL` |
| `REDIS` | `REDIS` |
| `FIREBASE` | `FIREBASE` |
| `GIT` | `BITBUCKET`, `GIT`, `GITHUB`, `GITLAB` |
| `DOCKER` | `DOCKER` |
| `KUBERNETES` | `K8S`, `KUBERNETES` |
| `JUPYTER` | `JUPYTER`, `JUPYTERLAB`, `JUPYTERNOTEBOOK`, `JUPYTERNOTEBOOKS` |
| `REST_API` | `APIREST`, `APIRESTFUL`, `APISREST`, `APISRESTFUL`, `RESTAPI`, `RESTAPIS`, `RESTFUL`, `RESTFULAPI`, `RESTFULAPIS`, `RESTFULSERVICE`, `RESTFULSERVICES`, `RESTFULWEBSERVICE`, `RESTFULWEBSERVICES` |
| `GRAPHQL` | `GRAPHQL` |
| `MACHINE_LEARNING` | `APRENDIZAJEAUTOMATICO`, `APRENDIZAJEDEMAQUINA`, `APRENDIZAJEDEMAQUINAS`, `APRENDIZAJEPROFUNDO`, `DEEPLEARNING`, `MACHINELEARNING`, `MACHINELEARNINGDEVELOPMENT`, `MACHINELEARNINGMODEL`, `MACHINELEARNINGMODELDEVELOPMENT`, `MACHINELEARNINGMODELS`, `MACHINELEARNINGMODELSDEVELOPMENT`, `ML`, `MODELOPREDICTIVO`, `MODELOPREDICTIVOS`, `MODELOSPREDICTIVO`, `MODELOSPREDICTIVOS`, `PREDICTIVEMODEL`, `PREDICTIVEMODELING`, `PREDICTIVEMODELS` |

```mermaid
flowchart LR
    n0((("f:DOCKER")))
    n1((("f:FIREBASE")))
    n2((("f:GIT")))
    n3((("f:GRAPHQL")))
    n4((("f:JUPYTER")))
    n5((("f:KUBERNETES")))
    n6((("f:MACHINE_LEARNING")))
    n7((("f:MARIADB")))
    n8((("f:MONGODB")))
    n9((("f:MYSQL")))
    n10((("f:NOSQL")))
    n11((("f:POSTGRESQL")))
    n12((("f:REDIS")))
    n13((("f:REST_API")))
    n14((("f:SQL")))
    n15((("f:SQLITE")))
    n16((("f:SQL_SERVER")))
    n17("p:AP")
    n18("p:API")
    n19("p:APIREST")
    n20("p:APISREST")
    n21("p:APRENDIZAJE")
    n22("p:APRENDIZAJEDEMAQUINA")
    n23("p:D")
    n24("p:G")
    n25("p:GIT")
    n26("p:JUPYTER")
    n27("p:JUPYTERNOTEBOOK")
    n28("p:K")
    n29("p:M")
    n30("p:MA")
    n31("p:MACHINELEARNING")
    n32("p:MACHINELEARNINGMODEL")
    n33("p:MACHINELEARNINGMODELS")
    n34("p:MO")
    n35("p:MODELO")
    n36("p:MODELOPREDICTIVO")
    n37("p:MODELOSPREDICTIVO")
    n38("p:MONGO")
    n39("p:P")
    n40("p:POSTGRES")
    n41("p:PREDICTIVEMODEL")
    n42("p:RE")
    n43("p:REST")
    n44("p:RESTAPI")
    n45("p:RESTFUL")
    n46("p:RESTFULAPI")
    n47("p:RESTFULSERVICE")
    n48("p:RESTFULWEBSERVICE")
    n49("p:SQL")
    n50(("q0"))
    n17 -->|"I"| n18
    n17 -->|"RENDIZAJE"| n21
    n18 -->|"REST"| n19
    n18 -->|"SREST"| n20
    n19 -->|"FUL⊣ / REST_API"| n13
    n19 -->|"⊣ / REST_API"| n13
    n20 -->|"FUL⊣ / REST_API"| n13
    n20 -->|"⊣ / REST_API"| n13
    n21 -->|"AUTOMATICO⊣ / MACHINE_LEARNING"| n6
    n21 -->|"DEMAQUINA"| n22
    n21 -->|"PROFUNDO⊣ / MACHINE_LEARNING"| n6
    n22 -->|"S⊣ / MACHINE_LEARNING"| n6
    n22 -->|"⊣ / MACHINE_LEARNING"| n6
    n23 -->|"EEPLEARNING⊣ / MACHINE_LEARNING"| n6
    n23 -->|"OCKER⊣ / DOCKER"| n0
    n24 -->|"IT"| n25
    n24 -->|"RAPHQL⊣ / GRAPHQL"| n3
    n25 -->|"HUB⊣ / GIT"| n2
    n25 -->|"LAB⊣ / GIT"| n2
    n25 -->|"⊣ / GIT"| n2
    n26 -->|"LAB⊣ / JUPYTER"| n4
    n26 -->|"NOTEBOOK"| n27
    n26 -->|"⊣ / JUPYTER"| n4
    n27 -->|"S⊣ / JUPYTER"| n4
    n27 -->|"⊣ / JUPYTER"| n4
    n28 -->|"8S⊣ / KUBERNETES"| n5
    n28 -->|"UBERNETES⊣ / KUBERNETES"| n5
    n29 -->|"A"| n30
    n29 -->|"L⊣ / MACHINE_LEARNING"| n6
    n29 -->|"O"| n34
    n29 -->|"YSQL⊣ / MYSQL"| n9
    n30 -->|"CHINELEARNING"| n31
    n30 -->|"RIADB⊣ / MARIADB"| n7
    n31 -->|"DEVELOPMENT⊣ / MACHINE_LEARNING"| n6
    n31 -->|"MODEL"| n32
    n31 -->|"⊣ / MACHINE_LEARNING"| n6
    n32 -->|"DEVELOPMENT⊣ / MACHINE_LEARNING"| n6
    n32 -->|"S"| n33
    n32 -->|"⊣ / MACHINE_LEARNING"| n6
    n33 -->|"DEVELOPMENT⊣ / MACHINE_LEARNING"| n6
    n33 -->|"⊣ / MACHINE_LEARNING"| n6
    n34 -->|"DELO"| n35
    n34 -->|"NGO"| n38
    n35 -->|"PREDICTIVO"| n36
    n35 -->|"SPREDICTIVO"| n37
    n36 -->|"S⊣ / MACHINE_LEARNING"| n6
    n36 -->|"⊣ / MACHINE_LEARNING"| n6
    n37 -->|"S⊣ / MACHINE_LEARNING"| n6
    n37 -->|"⊣ / MACHINE_LEARNING"| n6
    n38 -->|"DB⊣ / MONGODB"| n8
    n38 -->|"⊣ / MONGODB"| n8
    n39 -->|"OSTGRES"| n40
    n39 -->|"REDICTIVEMODEL"| n41
    n40 -->|"QL⊣ / POSTGRESQL"| n11
    n40 -->|"⊣ / POSTGRESQL"| n11
    n41 -->|"ING⊣ / MACHINE_LEARNING"| n6
    n41 -->|"S⊣ / MACHINE_LEARNING"| n6
    n41 -->|"⊣ / MACHINE_LEARNING"| n6
    n42 -->|"DIS⊣ / REDIS"| n12
    n42 -->|"ST"| n43
    n43 -->|"API"| n44
    n43 -->|"FUL"| n45
    n44 -->|"S⊣ / REST_API"| n13
    n44 -->|"⊣ / REST_API"| n13
    n45 -->|"API"| n46
    n45 -->|"SERVICE"| n47
    n45 -->|"WEBSERVICE"| n48
    n45 -->|"⊣ / REST_API"| n13
    n46 -->|"S⊣ / REST_API"| n13
    n46 -->|"⊣ / REST_API"| n13
    n47 -->|"S⊣ / REST_API"| n13
    n47 -->|"⊣ / REST_API"| n13
    n48 -->|"S⊣ / REST_API"| n13
    n48 -->|"⊣ / REST_API"| n13
    n49 -->|"ITE⊣ / SQLITE"| n15
    n49 -->|"SERVER⊣ / SQL_SERVER"| n16
    n49 -->|"⊣ / SQL"| n14
    n50 -->|"AP"| n17
    n50 -->|"BITBUCKET⊣ / GIT"| n2
    n50 -->|"D"| n23
    n50 -->|"FIREBASE⊣ / FIREBASE"| n1
    n50 -->|"G"| n24
    n50 -->|"JUPYTER"| n26
    n50 -->|"K"| n28
    n50 -->|"M"| n29
    n50 -->|"NOSQL⊣ / NOSQL"| n10
    n50 -->|"P"| n39
    n50 -->|"RE"| n42
    n50 -->|"SQL"| n49
```

| Input | C writes | D run | Output |
|---|---|---|---|
| `Postgres` | `POSTGRES` | `q0 -P-> ... -S-> p:POSTGRES -⊣/POSTGRESQL-> f:POSTGRESQL` | `POSTGRESQL` |
| `GitHub` | `GITHUB` | `q0 -G-> ... -B-> p:GITHUB -⊣/GIT-> f:GIT` | `GIT` |
| `Machine-learning model development` | `MACHINELEARNINGMODELDEVELOPMENT` | one path of 31 letters, then `⊣/MACHINE_LEARNING` | `MACHINE_LEARNING` |
| `REST` | `REST` | stops in `p:REST`, no `⊣` transition (`REST` alone is not a spelling) | rejected |
| `Jenkins` | `JENKINS` | `p:J` has no transition on `E` (the only key that starts with `J` is `JUPYTER...`) | rejected |

## 5. How `normalize` uses them

`normalize_skill(raw)` runs C once, then tries the three dictionaries in the
order `languages`, `frameworks`, `databases_tools`. Their keys are disjoint, so
at most one accepts the key; if none does, the string has no canonical form and
`normalize` drops it.

```
raw --C--> key --D(languages)------\
               \--D(frameworks)-----+--> token, or dropped
                \--D(databases_tools)/
```

Sorting by profile is applied afterwards and is not a transducer
(`docs/normalization-sorting.md`).
