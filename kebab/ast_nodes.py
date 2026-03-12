"""AST node definitions for the kebab language."""

from dataclasses import dataclass, field
from typing import Any, List, Optional


# ──────────────────────────────────────────────────────────────────────── #
# Expressions                                                               #
# ──────────────────────────────────────────────────────────────────────── #

@dataclass
class NumberLiteral:
    value: float
    line: int


@dataclass
class StringLiteral:
    value: str
    line: int


@dataclass
class BoolLiteral:
    value: bool
    line: int


@dataclass
class NullLiteral:
    line: int


@dataclass
class Identifier:
    name: str
    line: int


@dataclass
class BinaryOp:
    op: str
    left: Any
    right: Any
    line: int


@dataclass
class UnaryOp:
    op: str
    operand: Any
    line: int


@dataclass
class Assignment:
    name: str
    value: Any
    line: int


@dataclass
class Call:
    callee: Any          # Identifier or expression
    args: List[Any]
    line: int


@dataclass
class RandomCall:
    """Built-in random(n) — returns a random integer in [0, n)."""
    n_expr: Any
    line: int


# ──────────────────────────────────────────────────────────────────────── #
# Statements                                                                #
# ──────────────────────────────────────────────────────────────────────── #

@dataclass
class ServeStmt:
    """serve <expr>; — print a value."""
    expr: Any
    line: int


@dataclass
class SkewerStmt:
    """skewer <name> = <expr>; — declare / assign a variable."""
    name: str
    value: Any
    line: int


@dataclass
class IfStmt:
    condition: Any
    then_branch: List[Any]
    else_branch: Optional[List[Any]]
    line: int


@dataclass
class GrillStmt:
    """grill (<condition>) { ... } — while loop."""
    condition: Any
    body: List[Any]
    line: int


@dataclass
class WrapStmt:
    """wrap name(params) { ... } — function definition."""
    name: str
    params: List[str]
    body: List[Any]
    line: int


@dataclass
class ReturnStmt:
    value: Optional[Any]
    line: int


@dataclass
class ExprStmt:
    """A bare expression used as a statement (e.g. a function call)."""
    expr: Any
    line: int
