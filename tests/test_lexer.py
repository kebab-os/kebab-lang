"""Tests for the kebab language lexer."""

import pytest
from kebab.lexer import Lexer, LexerError
from kebab.tokens import TokenType


def tokenize(source):
    return Lexer(source).tokenize()


def types(tokens):
    return [t.type for t in tokens]


class TestLiterals:
    def test_integer(self):
        toks = tokenize("42;")
        assert toks[0].type == TokenType.NUMBER
        assert toks[0].value == 42

    def test_float(self):
        toks = tokenize("3.14;")
        assert toks[0].type == TokenType.NUMBER
        assert toks[0].value == pytest.approx(3.14)

    def test_string_double_quote(self):
        toks = tokenize('"hello";')
        assert toks[0].type == TokenType.STRING
        assert toks[0].value == "hello"

    def test_string_single_quote(self):
        toks = tokenize("'world';")
        assert toks[0].type == TokenType.STRING
        assert toks[0].value == "world"

    def test_string_escape_newline(self):
        toks = tokenize(r'"line1\nline2";')
        assert toks[0].value == "line1\nline2"

    def test_true(self):
        toks = tokenize("true;")
        assert toks[0].type == TokenType.BOOLEAN
        assert toks[0].value is True

    def test_false(self):
        toks = tokenize("false;")
        assert toks[0].type == TokenType.BOOLEAN
        assert toks[0].value is False

    def test_null(self):
        toks = tokenize("null;")
        assert toks[0].type == TokenType.NULL
        assert toks[0].value is None


class TestKeywords:
    def test_keywords(self):
        kw_map = {
            "serve": TokenType.SERVE,
            "skewer": TokenType.SKEWER,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "grill": TokenType.GRILL,
            "wrap": TokenType.WRAP,
            "return": TokenType.RETURN,
            "random": TokenType.RANDOM,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "not": TokenType.NOT,
        }
        for word, expected_type in kw_map.items():
            toks = tokenize(f"{word};")
            assert toks[0].type == expected_type, f"failed for keyword '{word}'"


class TestOperators:
    def test_arithmetic(self):
        toks = tokenize("+ - * / %")
        assert types(toks)[:-1] == [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT,
        ]

    def test_comparison(self):
        toks = tokenize("== != < <= > >=")
        assert types(toks)[:-1] == [
            TokenType.EQUAL_EQUAL,
            TokenType.BANG_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ]

    def test_assignment(self):
        toks = tokenize("=")
        assert toks[0].type == TokenType.EQUAL


class TestComments:
    def test_hash_comment(self):
        toks = tokenize("# this is a comment\n42;")
        assert toks[0].type == TokenType.NUMBER
        assert toks[0].value == 42

    def test_slash_slash_comment(self):
        toks = tokenize("// another comment\n42;")
        assert toks[0].type == TokenType.NUMBER
        assert toks[0].value == 42


class TestErrors:
    def test_unexpected_character(self):
        with pytest.raises(LexerError):
            tokenize("@invalid")

    def test_unterminated_string(self):
        with pytest.raises(LexerError):
            tokenize('"no closing quote')

    def test_line_tracking(self):
        toks = tokenize("1;\n2;\n3;")
        assert toks[0].line == 1
        assert toks[2].line == 2
        assert toks[4].line == 3
