"""Errors raised when a candidate profile is rejected."""

from __future__ import annotations


class DSLError(ValueError):
    """Base class: the candidate profile text is not valid."""


class DSLSyntaxError(DSLError):
    """The text breaks the lexical or syntactic rules of the grammar."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column


class DSLSemanticError(DSLError):
    """The text follows the grammar but breaks a semantic rule (S1 to S6)."""

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors
