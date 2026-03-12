"""Public API for the kebab language runtime."""

from .lexer import Lexer, LexerError
from .parser import Parser, ParseError
from .interpreter import Interpreter, RuntimeError as KebabRuntimeError


def run(source: str, output_fn=None) -> None:
    """Lex, parse, and interpret a kebab source string.

    Args:
        source:    The kebab source code to execute.
        output_fn: Optional callable used instead of ``print`` for output.

    Raises:
        LexerError:        on tokenisation errors.
        ParseError:        on syntax errors.
        KebabRuntimeError: on runtime errors.
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    statements = parser.parse()

    interpreter = Interpreter(output_fn=output_fn)
    interpreter.interpret(statements)


__all__ = [
    "run",
    "Lexer",
    "LexerError",
    "Parser",
    "ParseError",
    "Interpreter",
    "KebabRuntimeError",
]
