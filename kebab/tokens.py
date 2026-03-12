"""Token types for the kebab language."""

from enum import Enum, auto


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()

    # Identifiers & keywords
    IDENTIFIER = auto()
    SERVE = auto()       # print
    SKEWER = auto()      # variable declaration
    IF = auto()
    ELSE = auto()
    GRILL = auto()       # while loop
    WRAP = auto()        # function definition
    RETURN = auto()
    RANDOM = auto()      # built-in random
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    # Comparison operators
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

    # Assignment
    EQUAL = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()

    # Special
    EOF = auto()


KEYWORDS = {
    "serve": TokenType.SERVE,
    "skewer": TokenType.SKEWER,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "grill": TokenType.GRILL,
    "wrap": TokenType.WRAP,
    "return": TokenType.RETURN,
    "random": TokenType.RANDOM,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}


class Token:
    """A single token produced by the lexer."""

    def __init__(self, type: TokenType, value, line: int):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"
