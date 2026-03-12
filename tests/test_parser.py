"""Tests for the kebab language parser."""

import pytest
from kebab.lexer import Lexer
from kebab.parser import Parser, ParseError
from kebab import ast_nodes as ast


def parse(source):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


class TestServe:
    def test_serve_number(self):
        stmts = parse("serve 42;")
        assert len(stmts) == 1
        assert isinstance(stmts[0], ast.ServeStmt)
        assert isinstance(stmts[0].expr, ast.NumberLiteral)

    def test_serve_string(self):
        stmts = parse('serve "hi";')
        assert isinstance(stmts[0].expr, ast.StringLiteral)
        assert stmts[0].expr.value == "hi"


class TestSkewer:
    def test_skewer_basic(self):
        stmts = parse("skewer x = 10;")
        assert isinstance(stmts[0], ast.SkewerStmt)
        assert stmts[0].name == "x"
        assert stmts[0].value.value == 10


class TestIf:
    def test_if_only(self):
        stmts = parse("if (true) { serve 1; }")
        assert isinstance(stmts[0], ast.IfStmt)
        assert stmts[0].else_branch is None

    def test_if_else(self):
        stmts = parse("if (false) { serve 1; } else { serve 2; }")
        assert isinstance(stmts[0], ast.IfStmt)
        assert stmts[0].else_branch is not None


class TestGrill:
    def test_grill(self):
        stmts = parse("grill (true) { serve 1; }")
        assert isinstance(stmts[0], ast.GrillStmt)


class TestWrap:
    def test_no_params(self):
        stmts = parse("wrap foo() { serve 1; }")
        assert isinstance(stmts[0], ast.WrapStmt)
        assert stmts[0].name == "foo"
        assert stmts[0].params == []

    def test_with_params(self):
        stmts = parse("wrap add(a, b) { return a + b; }")
        fn = stmts[0]
        assert fn.params == ["a", "b"]


class TestExpressions:
    def test_binary_arithmetic(self):
        stmts = parse("serve 1 + 2 * 3;")
        # should respect precedence: 1 + (2 * 3)
        expr = stmts[0].expr
        assert isinstance(expr, ast.BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.right, ast.BinaryOp)
        assert expr.right.op == "*"

    def test_grouping(self):
        stmts = parse("serve (1 + 2) * 3;")
        expr = stmts[0].expr
        assert expr.op == "*"
        assert isinstance(expr.left, ast.BinaryOp)

    def test_unary_minus(self):
        stmts = parse("serve -5;")
        expr = stmts[0].expr
        assert isinstance(expr, ast.UnaryOp)
        assert expr.op == "-"

    def test_unary_not(self):
        stmts = parse("serve not true;")
        expr = stmts[0].expr
        assert isinstance(expr, ast.UnaryOp)
        assert expr.op == "not"

    def test_call_expression(self):
        stmts = parse("foo(1, 2);")
        assert isinstance(stmts[0], ast.ExprStmt)
        assert isinstance(stmts[0].expr, ast.Call)

    def test_random_call(self):
        stmts = parse("serve random(10);")
        assert isinstance(stmts[0].expr, ast.RandomCall)

    def test_assignment_expression(self):
        stmts = parse("skewer x = 1; x = 2;")
        assign = stmts[1]
        assert isinstance(assign, ast.ExprStmt)
        assert isinstance(assign.expr, ast.Assignment)
        assert assign.expr.name == "x"


class TestErrors:
    def test_missing_semicolon(self):
        with pytest.raises(ParseError):
            parse("serve 42")

    def test_invalid_assignment_target(self):
        with pytest.raises(ParseError):
            parse("1 + 2 = 3;")

    def test_unexpected_token(self):
        with pytest.raises(ParseError):
            parse("serve ;")
