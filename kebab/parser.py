"""Parser for the kebab language.

Grammar (simplified):

    program        → statement* EOF
    statement      → serve_stmt
                   | skewer_stmt
                   | if_stmt
                   | grill_stmt
                   | wrap_stmt
                   | return_stmt
                   | expr_stmt
    serve_stmt     → "serve" expression ";"
    skewer_stmt    → "skewer" IDENTIFIER "=" expression ";"
    if_stmt        → "if" "(" expression ")" block ( "else" block )?
    grill_stmt     → "grill" "(" expression ")" block
    wrap_stmt      → "wrap" IDENTIFIER "(" params? ")" block
    return_stmt    → "return" expression? ";"
    expr_stmt      → expression ";"
    block          → "{" statement* "}"
    expression     → assignment
    assignment     → IDENTIFIER "=" assignment | logic_or
    logic_or       → logic_and ( "or" logic_and )*
    logic_and      → equality ( "and" equality )*
    equality       → comparison ( ("==" | "!=") comparison )*
    comparison     → term ( ("<" | "<=" | ">" | ">=") term )*
    term           → factor ( ("+" | "-") factor )*
    factor         → unary ( ("*" | "/" | "%") unary )*
    unary          → ("not" | "-") unary | call
    call           → primary ( "(" arguments? ")" )*
    primary        → NUMBER | STRING | BOOLEAN | NULL
                   | "random" "(" expression ")"
                   | IDENTIFIER
                   | "(" expression ")"
"""

from .tokens import Token, TokenType
from . import ast_nodes as ast


class ParseError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"[line {line}] Parse error: {message}")
        self.line = line


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.current = 0

    # ---------------------------------------------------------------- public

    def parse(self) -> list:
        statements = []
        while not self._at_end():
            statements.append(self._statement())
        return statements

    # ------------------------------------------------------------ helpers

    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        if not self._at_end():
            self.current += 1
        return self._previous()

    def _check(self, *types) -> bool:
        return self._peek().type in types

    def _match(self, *types) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, ttype: TokenType, message: str) -> Token:
        if self._check(ttype):
            return self._advance()
        raise ParseError(message, self._peek().line)

    # ---------------------------------------------------------- statements

    def _statement(self):
        if self._match(TokenType.SERVE):
            return self._serve_stmt()
        if self._match(TokenType.SKEWER):
            return self._skewer_stmt()
        if self._match(TokenType.IF):
            return self._if_stmt()
        if self._match(TokenType.GRILL):
            return self._grill_stmt()
        if self._match(TokenType.WRAP):
            return self._wrap_stmt()
        if self._match(TokenType.RETURN):
            return self._return_stmt()
        return self._expr_stmt()

    def _serve_stmt(self):
        line = self._previous().line
        expr = self._expression()
        self._expect(TokenType.SEMICOLON, "expected ';' after 'serve' value")
        return ast.ServeStmt(expr, line)

    def _skewer_stmt(self):
        line = self._previous().line
        name_tok = self._expect(TokenType.IDENTIFIER, "expected variable name after 'skewer'")
        self._expect(TokenType.EQUAL, "expected '=' after variable name")
        value = self._expression()
        self._expect(TokenType.SEMICOLON, "expected ';' after variable value")
        return ast.SkewerStmt(name_tok.value, value, line)

    def _if_stmt(self):
        line = self._previous().line
        self._expect(TokenType.LPAREN, "expected '(' after 'if'")
        condition = self._expression()
        self._expect(TokenType.RPAREN, "expected ')' after condition")
        then_branch = self._block()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._block()
        return ast.IfStmt(condition, then_branch, else_branch, line)

    def _grill_stmt(self):
        line = self._previous().line
        self._expect(TokenType.LPAREN, "expected '(' after 'grill'")
        condition = self._expression()
        self._expect(TokenType.RPAREN, "expected ')' after condition")
        body = self._block()
        return ast.GrillStmt(condition, body, line)

    def _wrap_stmt(self):
        line = self._previous().line
        name_tok = self._expect(TokenType.IDENTIFIER, "expected function name after 'wrap'")
        self._expect(TokenType.LPAREN, "expected '(' after function name")
        params = []
        if not self._check(TokenType.RPAREN):
            params.append(
                self._expect(TokenType.IDENTIFIER, "expected parameter name").value
            )
            while self._match(TokenType.COMMA):
                params.append(
                    self._expect(TokenType.IDENTIFIER, "expected parameter name").value
                )
        self._expect(TokenType.RPAREN, "expected ')' after parameters")
        body = self._block()
        return ast.WrapStmt(name_tok.value, params, body, line)

    def _return_stmt(self):
        line = self._previous().line
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        self._expect(TokenType.SEMICOLON, "expected ';' after return value")
        return ast.ReturnStmt(value, line)

    def _expr_stmt(self):
        line = self._peek().line
        expr = self._expression()
        self._expect(TokenType.SEMICOLON, "expected ';' after expression")
        return ast.ExprStmt(expr, line)

    def _block(self) -> list:
        self._expect(TokenType.LBRACE, "expected '{'")
        stmts = []
        while not self._check(TokenType.RBRACE) and not self._at_end():
            stmts.append(self._statement())
        self._expect(TokenType.RBRACE, "expected '}'")
        return stmts

    # --------------------------------------------------------- expressions

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._logic_or()
        if self._match(TokenType.EQUAL):
            line = self._previous().line
            if not isinstance(expr, ast.Identifier):
                raise ParseError("invalid assignment target", line)
            value = self._assignment()
            return ast.Assignment(expr.name, value, line)
        return expr

    def _logic_or(self):
        left = self._logic_and()
        while self._match(TokenType.OR):
            line = self._previous().line
            right = self._logic_and()
            left = ast.BinaryOp("or", left, right, line)
        return left

    def _logic_and(self):
        left = self._equality()
        while self._match(TokenType.AND):
            line = self._previous().line
            right = self._equality()
            left = ast.BinaryOp("and", left, right, line)
        return left

    def _equality(self):
        left = self._comparison()
        while self._check(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self._advance().type
            line = self._previous().line
            right = self._comparison()
            left = ast.BinaryOp(
                "==" if op == TokenType.EQUAL_EQUAL else "!=", left, right, line
            )
        return left

    def _comparison(self):
        left = self._term()
        ops = {
            TokenType.LESS: "<",
            TokenType.LESS_EQUAL: "<=",
            TokenType.GREATER: ">",
            TokenType.GREATER_EQUAL: ">=",
        }
        while self._peek().type in ops:
            op = ops[self._advance().type]
            line = self._previous().line
            right = self._term()
            left = ast.BinaryOp(op, left, right, line)
        return left

    def _term(self):
        left = self._factor()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op = "+" if self._advance().type == TokenType.PLUS else "-"
            line = self._previous().line
            right = self._factor()
            left = ast.BinaryOp(op, left, right, line)
        return left

    def _factor(self):
        left = self._unary()
        ops = {
            TokenType.STAR: "*",
            TokenType.SLASH: "/",
            TokenType.PERCENT: "%",
        }
        while self._peek().type in ops:
            op = ops[self._advance().type]
            line = self._previous().line
            right = self._unary()
            left = ast.BinaryOp(op, left, right, line)
        return left

    def _unary(self):
        if self._match(TokenType.NOT):
            line = self._previous().line
            operand = self._unary()
            return ast.UnaryOp("not", operand, line)
        if self._match(TokenType.MINUS):
            line = self._previous().line
            operand = self._unary()
            return ast.UnaryOp("-", operand, line)
        return self._call()

    def _call(self):
        expr = self._primary()
        while self._match(TokenType.LPAREN):
            line = self._previous().line
            args = []
            if not self._check(TokenType.RPAREN):
                args.append(self._expression())
                while self._match(TokenType.COMMA):
                    args.append(self._expression())
            self._expect(TokenType.RPAREN, "expected ')' after arguments")
            expr = ast.Call(expr, args, line)
        return expr

    def _primary(self):
        tok = self._peek()

        if self._match(TokenType.NUMBER):
            return ast.NumberLiteral(self._previous().value, self._previous().line)

        if self._match(TokenType.STRING):
            return ast.StringLiteral(self._previous().value, self._previous().line)

        if self._match(TokenType.BOOLEAN):
            return ast.BoolLiteral(self._previous().value, self._previous().line)

        if self._match(TokenType.NULL):
            return ast.NullLiteral(self._previous().line)

        if self._match(TokenType.RANDOM):
            line = self._previous().line
            self._expect(TokenType.LPAREN, "expected '(' after 'random'")
            n_expr = self._expression()
            self._expect(TokenType.RPAREN, "expected ')' after random argument")
            return ast.RandomCall(n_expr, line)

        if self._match(TokenType.IDENTIFIER):
            prev = self._previous()
            return ast.Identifier(prev.value, prev.line)

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._expect(TokenType.RPAREN, "expected ')' after expression")
            return expr

        raise ParseError(f"unexpected token '{tok.value or tok.type.name}'", tok.line)
