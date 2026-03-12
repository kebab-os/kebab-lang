"""Command-line interface — shared between `bin/kebab` and `python -m kebab`."""

import sys
from . import run, LexerError, ParseError, KebabRuntimeError


def main(argv=None):
    args = (argv or sys.argv)[1:]

    if not args:
        print("usage: kebab <file.kb>", file=sys.stderr)
        print("       kebab --help", file=sys.stderr)
        sys.exit(1)

    if args[0] in ("-h", "--help"):
        print(
            "kebab — a fun, skewered programming language\n"
            "\n"
            "usage: kebab <file.kb>\n"
            "\n"
            "language features:\n"
            "  serve <expr>;                  print a value\n"
            "  skewer <name> = <expr>;        declare a variable\n"
            "  if (<cond>) { } else { }       conditional\n"
            "  grill (<cond>) { }             while loop\n"
            "  wrap <name>(<params>) { }      define a function\n"
            "  return <expr>;                 return from a function\n"
            "  random(<n>)                    random integer in [0, n)\n"
            "  # comment                      line comment\n"
            "  // comment                     line comment (alt)\n"
        )
        sys.exit(0)

    filepath = args[0]

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            source = fh.read()
    except FileNotFoundError:
        print(f"error: file not found: '{filepath}'", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"error: cannot read file: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        run(source)
    except (LexerError, ParseError, KebabRuntimeError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
