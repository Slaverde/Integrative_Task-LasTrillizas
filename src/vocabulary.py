"""Canonical vocabulary shared by every stage of ResumeLens.

Stage 2 (normalization) produces tokens from ``TOKENS``; stage 3
(classification) uses them as the alphabet of its automata; stage 4 (DSL)
validates skills against them. Keeping the vocabulary in one place lets the
four profiles go through the same code.

NOTE: the two team-defined profiles (BACKEND_DEVELOPER, DATA_SCIENTIST) are
PROVISIONAL until the professor sends their requirements.
"""

from __future__ import annotations

from enum import Enum


class Category(str, Enum):
    LANGUAGE = "LANGUAGE"
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    DATABASE = "DATABASE"
    VERSION_CONTROL = "VERSION_CONTROL"
    ML_LIBRARY = "ML_LIBRARY"
    DATA_LIBRARY = "DATA_LIBRARY"
    CONCEPT = "CONCEPT"
    TOOL = "TOOL"


class Profile(str, Enum):
    FULL_STACK_DEVELOPER = "FULL_STACK_DEVELOPER"
    MACHINE_LEARNING_ENGINEER = "MACHINE_LEARNING_ENGINEER"
    BACKEND_DEVELOPER = "BACKEND_DEVELOPER"  # provisional (software)
    DATA_SCIENTIST = "DATA_SCIENTIST"  # provisional (AI/data)


# Canonical token -> category. Insertion order is the tie-break order used
# when sorting inside a category.
TOKENS: dict[str, Category] = {
    # languages
    "JAVASCRIPT": Category.LANGUAGE,
    "TYPESCRIPT": Category.LANGUAGE,
    "PYTHON": Category.LANGUAGE,
    "JAVA": Category.LANGUAGE,
    "KOTLIN": Category.LANGUAGE,
    "CPP": Category.LANGUAGE,
    # frontend frameworks
    "REACT": Category.FRONTEND,
    "ANGULAR": Category.FRONTEND,
    "VUE": Category.FRONTEND,
    "NEXT_JS": Category.FRONTEND,
    # backend frameworks
    "NODE_JS": Category.BACKEND,
    "DJANGO": Category.BACKEND,
    "SPRING_BOOT": Category.BACKEND,
    "FLASK": Category.BACKEND,
    "EXPRESS_JS": Category.BACKEND,
    "FASTAPI": Category.BACKEND,
    # databases
    "SQL": Category.DATABASE,
    "POSTGRESQL": Category.DATABASE,
    "MYSQL": Category.DATABASE,
    "MONGODB": Category.DATABASE,
    "MARIADB": Category.DATABASE,
    "SQL_SERVER": Category.DATABASE,
    "SQLITE": Category.DATABASE,
    "NOSQL": Category.DATABASE,
    "REDIS": Category.DATABASE,
    "FIREBASE": Category.DATABASE,
    # version control
    "GIT": Category.VERSION_CONTROL,
    # data / ML libraries
    "PANDAS": Category.DATA_LIBRARY,
    "NUMPY": Category.DATA_LIBRARY,
    "SCIKIT_LEARN": Category.ML_LIBRARY,
    "TENSORFLOW": Category.ML_LIBRARY,
    "PYTORCH": Category.ML_LIBRARY,
    "KERAS": Category.ML_LIBRARY,
    # concepts
    "REST_API": Category.CONCEPT,
    "MACHINE_LEARNING": Category.CONCEPT,
    "GRAPHQL": Category.CONCEPT,
    # tools
    "DOCKER": Category.TOOL,
    "JUPYTER": Category.TOOL,
    "KUBERNETES": Category.TOOL,
}

# Canonical category order per profile (used to sort tokens before the
# automata, so the result does not depend on the order of the resume).
PROFILE_ORDER: dict[Profile, list[Category]] = {
    Profile.FULL_STACK_DEVELOPER: [
        Category.LANGUAGE,
        Category.FRONTEND,
        Category.BACKEND,
        Category.DATABASE,
        Category.VERSION_CONTROL,
        Category.CONCEPT,
    ],
    Profile.MACHINE_LEARNING_ENGINEER: [
        Category.LANGUAGE,
        Category.DATA_LIBRARY,
        Category.ML_LIBRARY,
        Category.CONCEPT,
        Category.DATABASE,
        Category.VERSION_CONTROL,
    ],
    Profile.BACKEND_DEVELOPER: [
        Category.LANGUAGE,
        Category.BACKEND,
        Category.DATABASE,
        Category.CONCEPT,
        Category.TOOL,
        Category.VERSION_CONTROL,
    ],
    Profile.DATA_SCIENTIST: [
        Category.LANGUAGE,
        Category.DATA_LIBRARY,
        Category.ML_LIBRARY,
        Category.DATABASE,
        Category.TOOL,
        Category.VERSION_CONTROL,
    ],
}
