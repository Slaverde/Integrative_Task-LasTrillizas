"""Variant dictionary of stage 2: how candidates write a qualification.

Every entry maps a canonical token of ``vocabulary.TOKENS`` to the spellings
that stand for it. Spellings are written the way people write them, but only
one spelling per *key* is needed: before a spelling is compared with the
dictionary it goes through ``variant_key``, which ignores letter case, accents
and the separators (space, hyphen, dot, underscore). So ``Node.js``,
``Node JS``, ``NodeJS`` and ``node-js`` all have the key ``NODEJS`` and the
dictionary lists just one of them.

The dictionary is split in three groups, one per transducer (see
docs/normalization-design.md):

* languages
* frameworks and libraries
* databases, tools and concepts
"""

from __future__ import annotations

from collections.abc import Mapping

# --- Alphabet of the cleaner -------------------------------------------------
# ``variant_key`` is the reference definition of the cleaner transducer
# (src/normalization/fst.py builds the same machine from these constants).

SEPARATORS = " \t-._"
"""Characters that are deleted: they never change which technology it is."""

ACCENTS: dict[str, str] = {
    **dict(zip("áàäâéèëêíìïîóòöôúùüûñç", "AAAAEEEEIIIIOOOOUUUUNC")),
    **dict(zip("ÁÀÄÂÉÈËÊÍÌÏÎÓÒÖÔÚÙÜÛÑÇ", "AAAAEEEEIIIIOOOOUUUUNC")),
}
"""Accented letters and the plain upper-case letter they become."""

KEPT_SYMBOLS = "+"
"""Symbols that are part of a name (``C++``) and are kept as they are."""


def variant_key(text: str) -> str:
    """Spelling -> key: upper case, no accents, no separators.

    ``Scikit-learn`` and ``scikit learn`` give ``SCIKITLEARN``.
    Raises ValueError if the text has a character the cleaner does not know
    (for example ``#`` or ``/``): such a spelling has no canonical form.
    """
    key: list[str] = []
    for char in text:
        if char in SEPARATORS:
            continue
        if char in ACCENTS:
            key.append(ACCENTS[char])
        elif char.isascii() and char.isalnum():
            key.append(char.upper())
        elif char in KEPT_SYMBOLS:
            key.append(char)
        else:
            raise ValueError(f"character {char!r} is not part of any spelling")
    return "".join(key)


# --- The dictionary ---------------------------------------------------------

Variants = Mapping[str, tuple[str, ...]]

LANGUAGE_VARIANTS: Variants = {
    "JAVASCRIPT": ("JS", "JavaScript", "ECMAScript"),
    "TYPESCRIPT": ("TS", "TypeScript"),
    "PYTHON": ("Python", "Python3"),
    "JAVA": ("Java",),
    "KOTLIN": ("Kotlin",),
    "CPP": ("C++",),
}

FRAMEWORK_VARIANTS: Variants = {
    # frontend
    "REACT": ("React", "ReactJS"),
    "ANGULAR": ("Angular", "AngularJS"),
    "VUE": ("Vue", "VueJS"),
    "NEXT_JS": ("NextJS",),
    # backend
    "NODE_JS": ("NodeJS",),
    "EXPRESS_JS": ("ExpressJS",),
    "DJANGO": ("Django",),
    "FLASK": ("Flask",),
    "FASTAPI": ("FastAPI",),
    "SPRING_BOOT": ("SpringBoot",),
    # data and machine-learning libraries
    "PANDAS": ("Pandas",),
    "NUMPY": ("NumPy",),
    "SCIKIT_LEARN": ("Scikit-learn", "sklearn"),
    "TENSORFLOW": ("TensorFlow",),
    "PYTORCH": ("PyTorch",),
    "KERAS": ("Keras",),
}

DATABASE_TOOL_VARIANTS: Variants = {
    # databases
    "SQL": ("SQL",),
    "POSTGRESQL": ("PostgreSQL", "Postgres"),
    "MYSQL": ("MySQL",),
    "MONGODB": ("MongoDB", "Mongo"),
    "MARIADB": ("MariaDB",),
    "SQL_SERVER": ("SQL Server",),
    "SQLITE": ("SQLite",),
    "NOSQL": ("NoSQL",),
    "REDIS": ("Redis",),
    "FIREBASE": ("Firebase",),
    # version control: hosting platforms count as Git (decision D3)
    "GIT": ("Git", "GitHub", "GitLab", "Bitbucket"),
    # tools
    "DOCKER": ("Docker",),
    "KUBERNETES": ("Kubernetes", "K8s"),
    "JUPYTER": (
        "Jupyter",
        "Jupyter Notebook",
        "Jupyter Notebooks",
        "JupyterLab",
    ),
    # concepts
    "REST_API": (
        "REST API",
        "REST APIs",
        "RESTful API",
        "RESTful APIs",
        "RESTful",
        "RESTful service",
        "RESTful services",
        "RESTful web service",
        "RESTful web services",
        "API REST",
        "APIs REST",
        "API RESTful",
        "APIs RESTful",
    ),
    "GRAPHQL": ("GraphQL",),
    # predictive models and deep learning count as machine learning (D4)
    "MACHINE_LEARNING": (
        "ML",
        "machine learning",
        "machine learning model",
        "machine learning models",
        "machine learning development",
        "machine learning model development",
        "machine learning models development",
        "aprendizaje automático",
        "aprendizaje de máquina",
        "aprendizaje de máquinas",
        "aprendizaje profundo",
        "deep learning",
        "predictive model",
        "predictive models",
        "predictive modeling",
        "modelo predictivo",
        "modelos predictivos",
        "modelo predictivos",
        "modelos predictivo",
    ),
}

GROUPS: dict[str, Variants] = {
    "languages": LANGUAGE_VARIANTS,
    "frameworks": FRAMEWORK_VARIANTS,
    "databases_tools": DATABASE_TOOL_VARIANTS,
}
"""One dictionary per transducer, in the order they are tried."""


def key_map(variants: Variants) -> dict[str, str]:
    """Dictionary of one group -> {key: canonical token}.

    Raises ValueError if two spellings of the group have the same key (the
    second one would be redundant or, worse, point to another token).
    """
    keys: dict[str, str] = {}
    for token, spellings in variants.items():
        for spelling in spellings:
            key = variant_key(spelling)
            if key in keys:
                raise ValueError(
                    f"{spelling!r} has key {key}, already used for {keys[key]}"
                )
            keys[key] = token
    return keys
