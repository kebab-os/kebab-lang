"""Tree-walk interpreter for the kebab language."""

import random as _random
from . import ast_nodes as ast
from .environment import Environment


class RuntimeError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"[line {line}] Runtime error: {message}")
        self.line = line


class ReturnException(Exception):
    """Used to unwind the call stack on a return statement."""

    def __init__(self, value):
        self.value = value


class KebabFunction:
    """A user-defined kebab function."""

    def __init__(self, stmt: ast.WrapStmt, closure: Environment):
        self.stmt = stmt
        self.closure = closure

    def arity(self) -> int:
        return len(self.stmt.params)

    def call(self, interpreter, args: list, line: int):
        env = Environment(self.closure)
        for param, arg in zip(self.stmt.params, args):
            env.define(param, arg)
        try:
            interpreter._exec_block(self.stmt.body, env)
        except ReturnException as ret:
            return ret.value
        return None

    def __repr__(self):
        return f"<wrap {self.stmt.name}>"


class Interpreter:
    def __init__(self, output_fn=None):
        """
        output_fn: callable that receives the string to print.
        Defaults to the built-in print function.
        """
        self._output = output_fn or print
        self._globals = Environment()
        self._env = self._globals

    # ---------------------------------------------------------------- public

    def interpret(self, statements: list):
        for stmt in statements:
            self._exec(stmt)

    # --------------------------------------------------------------- execute

    def _exec(self, node):
        method = "_exec_" + type(node).__name__
        handler = getattr(self, method, None)
        if handler is None:
            raise RuntimeError(f"unknown statement type: {type(node).__name__}", 0)
        return handler(node)

    def _exec_ServeStmt(self, node: ast.ServeStmt):
        value = self._eval(node.expr)
        self._output(self._stringify(value))

    def _exec_SkewerStmt(self, node: ast.SkewerStmt):
        value = self._eval(node.value)
        self._env.define(node.name, value)

    def _exec_IfStmt(self, node: ast.IfStmt):
        if self._is_truthy(self._eval(node.condition)):
            self._exec_block(node.then_branch, Environment(self._env))
        elif node.else_branch is not None:
            self._exec_block(node.else_branch, Environment(self._env))

    def _exec_GrillStmt(self, node: ast.GrillStmt):
        while self._is_truthy(self._eval(node.condition)):
            self._exec_block(node.body, Environment(self._env))

    def _exec_WrapStmt(self, node: ast.WrapStmt):
        func = KebabFunction(node, self._env)
        self._env.define(node.name, func)

    def _exec_ReturnStmt(self, node: ast.ReturnStmt):
        value = self._eval(node.value) if node.value is not None else None
        raise ReturnException(value)

    def _exec_ExprStmt(self, node: ast.ExprStmt):
        self._eval(node.expr)

    def _exec_block(self, stmts: list, env: Environment):
        previous = self._env
        self._env = env
        try:
            for stmt in stmts:
                self._exec(stmt)
        finally:
            self._env = previous

    # --------------------------------------------------------------- evaluate

    def _eval(self, node):
        method = "_eval_" + type(node).__name__
        handler = getattr(self, method, None)
        if handler is None:
            raise RuntimeError(f"unknown expression type: {type(node).__name__}", 0)
        return handler(node)

    def _eval_NumberLiteral(self, node: ast.NumberLiteral):
        return node.value

    def _eval_StringLiteral(self, node: ast.StringLiteral):
        return node.value

    def _eval_BoolLiteral(self, node: ast.BoolLiteral):
        return node.value

    def _eval_NullLiteral(self, node: ast.NullLiteral):
        return None

    def _eval_Identifier(self, node: ast.Identifier):
        return self._env.get(node.name, node.line)

    def _eval_Assignment(self, node: ast.Assignment):
        value = self._eval(node.value)
        self._env.assign(node.name, value, node.line)
        return value

    def _eval_UnaryOp(self, node: ast.UnaryOp):
        operand = self._eval(node.operand)
        if node.op == "-":
            self._check_number(operand, node.line)
            return -operand
        if node.op == "not":
            return not self._is_truthy(operand)
        raise RuntimeError(f"unknown unary operator '{node.op}'", node.line)

    def _eval_BinaryOp(self, node: ast.BinaryOp):
        # Short-circuit logical operators
        if node.op == "and":
            left = self._eval(node.left)
            return left if not self._is_truthy(left) else self._eval(node.right)
        if node.op == "or":
            left = self._eval(node.left)
            return left if self._is_truthy(left) else self._eval(node.right)

        left = self._eval(node.left)
        right = self._eval(node.right)

        if node.op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self._stringify(left) + self._stringify(right)
            self._check_numbers(left, right, node.line)
            return left + right
        if node.op == "-":
            self._check_numbers(left, right, node.line)
            return left - right
        if node.op == "*":
            self._check_numbers(left, right, node.line)
            return left * right
        if node.op == "/":
            self._check_numbers(left, right, node.line)
            if right == 0:
                raise RuntimeError("division by zero", node.line)
            return left / right
        if node.op == "%":
            self._check_numbers(left, right, node.line)
            if right == 0:
                raise RuntimeError("modulo by zero", node.line)
            return left % right
        if node.op == "==":
            return self._is_equal(left, right)
        if node.op == "!=":
            return not self._is_equal(left, right)
        if node.op == "<":
            self._check_numbers(left, right, node.line)
            return left < right
        if node.op == "<=":
            self._check_numbers(left, right, node.line)
            return left <= right
        if node.op == ">":
            self._check_numbers(left, right, node.line)
            return left > right
        if node.op == ">=":
            self._check_numbers(left, right, node.line)
            return left >= right
        raise RuntimeError(f"unknown operator '{node.op}'", node.line)

    def _eval_Call(self, node: ast.Call):
        callee = self._eval(node.callee)
        args = [self._eval(a) for a in node.args]
        if not isinstance(callee, KebabFunction):
            raise RuntimeError(
                f"'{self._stringify(callee)}' is not a function", node.line
            )
        if len(args) != callee.arity():
            raise RuntimeError(
                f"expected {callee.arity()} argument(s) but got {len(args)}",
                node.line,
            )
        return callee.call(self, args, node.line)

    def _eval_RandomCall(self, node: ast.RandomCall):
        n = self._eval(node.n_expr)
        if not isinstance(n, (int, float)) or n != int(n) or int(n) <= 0:
            raise RuntimeError(
                "random() argument must be a positive integer", node.line
            )
        return _random.randint(0, int(n) - 1)

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def _is_truthy(value) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    @staticmethod
    def _is_equal(a, b) -> bool:
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a == b

    @staticmethod
    def _check_number(value, line: int):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise RuntimeError(f"operand must be a number, got '{value}'", line)

    @staticmethod
    def _check_numbers(left, right, line: int):
        if (
            not isinstance(left, (int, float))
            or isinstance(left, bool)
            or not isinstance(right, (int, float))
            or isinstance(right, bool)
        ):
            raise RuntimeError(
                f"operands must be numbers, got '{left}' and '{right}'", line
            )

    @staticmethod
    def _stringify(value) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(value)
