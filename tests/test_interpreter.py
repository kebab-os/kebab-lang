"""Tests for the kebab language interpreter."""

import pytest
from kebab import run, KebabRuntimeError


def run_capture(source):
    """Run kebab source and return list of printed lines."""
    output = []
    run(source, output_fn=lambda s: output.append(s))
    return output


class TestServe:
    def test_number(self):
        assert run_capture("serve 42;") == ["42"]

    def test_string(self):
        assert run_capture('serve "hello";') == ["hello"]

    def test_true(self):
        assert run_capture("serve true;") == ["true"]

    def test_false(self):
        assert run_capture("serve false;") == ["false"]

    def test_null(self):
        assert run_capture("serve null;") == ["null"]


class TestArithmetic:
    def test_addition(self):
        assert run_capture("serve 1 + 2;") == ["3"]

    def test_subtraction(self):
        assert run_capture("serve 10 - 4;") == ["6"]

    def test_multiplication(self):
        assert run_capture("serve 3 * 4;") == ["12"]

    def test_division(self):
        assert run_capture("serve 10 / 4;") == ["2.5"]

    def test_modulo(self):
        assert run_capture("serve 10 % 3;") == ["1"]

    def test_precedence(self):
        assert run_capture("serve 2 + 3 * 4;") == ["14"]

    def test_grouping(self):
        assert run_capture("serve (2 + 3) * 4;") == ["20"]

    def test_unary_minus(self):
        assert run_capture("serve -5;") == ["-5"]

    def test_division_by_zero(self):
        with pytest.raises(KebabRuntimeError):
            run_capture("serve 1 / 0;")


class TestStringConcatenation:
    def test_concat_strings(self):
        assert run_capture('serve "foo" + "bar";') == ["foobar"]

    def test_concat_number(self):
        assert run_capture('serve "x=" + 42;') == ["x=42"]

    def test_concat_bool(self):
        assert run_capture('serve "val=" + true;') == ["val=true"]


class TestComparison:
    def test_equal_true(self):
        assert run_capture("serve 1 == 1;") == ["true"]

    def test_equal_false(self):
        assert run_capture("serve 1 == 2;") == ["false"]

    def test_not_equal(self):
        assert run_capture("serve 1 != 2;") == ["true"]

    def test_less(self):
        assert run_capture("serve 1 < 2;") == ["true"]

    def test_greater(self):
        assert run_capture("serve 3 > 2;") == ["true"]

    def test_less_equal(self):
        assert run_capture("serve 2 <= 2;") == ["true"]

    def test_greater_equal(self):
        assert run_capture("serve 3 >= 3;") == ["true"]


class TestLogical:
    def test_and_true(self):
        assert run_capture("serve true and true;") == ["true"]

    def test_and_false(self):
        assert run_capture("serve true and false;") == ["false"]

    def test_or_true(self):
        assert run_capture("serve false or true;") == ["true"]

    def test_or_false(self):
        assert run_capture("serve false or false;") == ["false"]

    def test_not_true(self):
        assert run_capture("serve not false;") == ["true"]

    def test_not_false(self):
        assert run_capture("serve not true;") == ["false"]

    def test_null_is_falsy(self):
        assert run_capture("serve not null;") == ["true"]


class TestSkewer:
    def test_declare_and_serve(self):
        assert run_capture("skewer x = 5; serve x;") == ["5"]

    def test_reassign(self):
        assert run_capture("skewer x = 1; x = 99; serve x;") == ["99"]

    def test_expression_value(self):
        assert run_capture("skewer x = 2 + 3; serve x;") == ["5"]

    def test_undefined_variable(self):
        with pytest.raises(KebabRuntimeError):
            run_capture("serve y;")


class TestIf:
    def test_if_taken(self):
        assert run_capture("if (true) { serve 1; }") == ["1"]

    def test_if_not_taken(self):
        assert run_capture("if (false) { serve 1; }") == []

    def test_if_else_then(self):
        assert run_capture("if (true) { serve 1; } else { serve 2; }") == ["1"]

    def test_if_else_else(self):
        assert run_capture("if (false) { serve 1; } else { serve 2; }") == ["2"]


class TestGrill:
    def test_basic_loop(self):
        src = "skewer i = 0; grill (i < 3) { serve i; i = i + 1; }"
        assert run_capture(src) == ["0", "1", "2"]

    def test_never_executes(self):
        src = "skewer i = 0; grill (false) { serve i; }"
        assert run_capture(src) == []


class TestWrap:
    def test_no_return_value(self):
        src = 'wrap greet(name) { serve "Hi " + name; } greet("kebab");'
        assert run_capture(src) == ["Hi kebab"]

    def test_return_value(self):
        src = "wrap add(a, b) { return a + b; } serve add(3, 4);"
        assert run_capture(src) == ["7"]

    def test_recursion(self):
        src = (
            "wrap fact(n) { if (n <= 1) { return 1; } return n * fact(n - 1); }\n"
            "serve fact(5);"
        )
        assert run_capture(src) == ["120"]

    def test_wrong_arity(self):
        with pytest.raises(KebabRuntimeError):
            run_capture("wrap f(a) { return a; } f(1, 2);")

    def test_call_non_function(self):
        with pytest.raises(KebabRuntimeError):
            run_capture("skewer x = 5; x();")


class TestRandom:
    def test_in_range(self):
        src = "skewer r = random(10); serve r >= 0; serve r < 10;"
        assert run_capture(src) == ["true", "true"]

    def test_zero_is_valid(self):
        # random(1) must always return 0
        src = "skewer r = random(1); serve r == 0;"
        assert run_capture(src) == ["true"]

    def test_bad_argument(self):
        with pytest.raises(KebabRuntimeError):
            run_capture("serve random(0);")

    def test_negative_argument(self):
        with pytest.raises(KebabRuntimeError):
            run_capture("serve random(-5);")


class TestScope:
    def test_function_scope_isolation(self):
        src = "skewer x = 10; wrap f() { skewer x = 99; } f(); serve x;"
        assert run_capture(src) == ["10"]

    def test_closure_reads_outer(self):
        src = "skewer x = 5; wrap f() { serve x; } f();"
        assert run_capture(src) == ["5"]
