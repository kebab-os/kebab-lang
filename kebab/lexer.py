"""Lexer (tokenizer) for the kebab language."""

from .tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"[line {line}] Lexer error: {message}")
        self.line = line


class Lexer:
    """Converts source code text into a list of tokens."""

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def tokenize(self) -> list:
        while not self._at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, None, self.line))
        return self.tokens

    # ------------------------------------------------------------------ helpers

    def _at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        return ch

    def _peek(self) -> str:
        if self._at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _add_token(self, type: TokenType, value=None):
        self.tokens.append(Token(type, value, self.line))

    # ---------------------------------------------------------------- scanning

    def _scan_token(self):
        ch = self._advance()

        if ch == "(":
            self._add_token(TokenType.LPAREN)
        elif ch == ")":
            self._add_token(TokenType.RPAREN)
        elif ch == "{":
            self._add_token(TokenType.LBRACE)
        elif ch == "}":
            self._add_token(TokenType.RBRACE)
        elif ch == ",":
            self._add_token(TokenType.COMMA)
        elif ch == ";":
            self._add_token(TokenType.SEMICOLON)
        elif ch == "+":
            self._add_token(TokenType.PLUS)
        elif ch == "-":
            self._add_token(TokenType.MINUS)
        elif ch == "*":
            self._add_token(TokenType.STAR)
        elif ch == "%":
            self._add_token(TokenType.PERCENT)
        elif ch == "/":
            if self._match("/"):
                # line comment
                while self._peek() != "\n" and not self._at_end():
                    self._advance()
            else:
                self._add_token(TokenType.SLASH)
        elif ch == "#":
            # hash comment
            while self._peek() != "\n" and not self._at_end():
                self._advance()
        elif ch == "!":
            self._add_token(
                TokenType.BANG_EQUAL if self._match("=") else TokenType.NOT
            )
        elif ch == "=":
            self._add_token(
                TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
            )
        elif ch == "<":
            self._add_token(
                TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
            )
        elif ch == ">":
            self._add_token(
                TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
            )
        elif ch in (" ", "\r", "\t"):
            pass  # skip whitespace
        elif ch == "\n":
            self.line += 1
        elif ch == '"':
            self._string('"')
        elif ch == "'":
            self._string("'")
        elif ch.isdigit():
            self._number()
        elif ch.isalpha() or ch == "_":
            self._identifier()
        else:
            raise LexerError(f"unexpected character '{ch}'", self.line)

    def _string(self, quote: str):
        value_chars = []
        while self._peek() != quote and not self._at_end():
            if self._peek() == "\n":
                self.line += 1
            if self._peek() == "\\" and self._peek_next() in (quote, "\\", "n", "t"):
                self._advance()  # consume backslash
                esc = self._advance()
                value_chars.append({"n": "\n", "t": "\t"}.get(esc, esc))
            else:
                value_chars.append(self._advance())
        if self._at_end():
            raise LexerError("unterminated string", self.line)
        self._advance()  # closing quote
        self._add_token(TokenType.STRING, "".join(value_chars))

    def _number(self):
        while self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()  # consume '.'
            while self._peek().isdigit():
                self._advance()
        text = self.source[self.start:self.current]
        value = float(text) if "." in text else int(text)
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        text = self.source[self.start:self.current]
        ttype = KEYWORDS.get(text, TokenType.IDENTIFIER)
        if ttype == TokenType.TRUE:
            self._add_token(TokenType.BOOLEAN, True)
        elif ttype == TokenType.FALSE:
            self._add_token(TokenType.BOOLEAN, False)
        elif ttype == TokenType.NULL:
            self._add_token(TokenType.NULL, None)
        else:
            self._add_token(ttype, text if ttype == TokenType.IDENTIFIER else None)
