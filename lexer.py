"""
lexer.py - Lexical Analyzer (Scanner) for DevLang.
Converts source code string into a sequence of Tokens with line and column tracking.
"""

from dataclasses import dataclass
from tokens import Token, TokenType, KEYWORDS


@dataclass
class LexicalError:
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"[LEXICAL_ERROR] Line {self.line}, Column {self.column}: {self.message}"


class Lexer:
    def __init__(self, source: str):
        self.source: str = source
        self.position: int = 0
        self.line: int = 1
        self.column: int = 1
        self.errors: list[LexicalError] = []

    def _is_at_end(self) -> bool:
        return self.position >= len(self.source)

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.position]

    def _peek_next(self) -> str:
        if self.position + 1 >= len(self.source):
            return '\0'
        return self.source[self.position + 1]

    def _advance(self) -> str:
        ch = self._peek()
        self.position += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _scan_identifier_or_keyword(self, start_line: int, start_col: int) -> Token:
        ident_str = ""
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == '_'):
            ident_str += self._advance()

        token_type = KEYWORDS.get(ident_str, TokenType.IDENTIFIER)
        return Token(token_type, ident_str, start_line, start_col)

    def _scan_number(self, start_line: int, start_col: int) -> Token:
        num_str = ""
        while not self._is_at_end() and self._peek().isdigit():
            num_str += self._advance()

        # Check for floating point literal
        if self._peek() == '.':
            if self._peek_next().isdigit():
                num_str += self._advance()  # Consume '.'
                while not self._is_at_end() and self._peek().isdigit():
                    num_str += self._advance()

                # Check for malformed float with extra dots (e.g. 12.34.56)
                if self._peek() == '.':
                    bad_str = num_str
                    while not self._is_at_end() and (self._peek().isdigit() or self._peek() == '.'):
                        bad_str += self._advance()
                    err_msg = f"Malformed float literal '{bad_str}'"
                    self.errors.append(LexicalError(err_msg, start_line, start_col))
                    return Token(TokenType.ERROR, bad_str, start_line, start_col)

                return Token(TokenType.FLOAT_LITERAL, float(num_str), start_line, start_col)
            else:
                # Trailing dot with no digits following (e.g., "12.")
                num_str += self._advance()  # Consume '.'
                err_msg = f"Malformed float literal '{num_str}' (expected digits after decimal point)"
                self.errors.append(LexicalError(err_msg, start_line, start_col))
                return Token(TokenType.ERROR, num_str, start_line, start_col)

        return Token(TokenType.INT_LITERAL, int(num_str), start_line, start_col)

    def tokenize(self) -> tuple[list[Token], list[LexicalError]]:
        tokens: list[Token] = []

        while not self._is_at_end():
            start_line = self.line
            start_col = self.column
            ch = self._peek()

            # Skip whitespace
            if ch in (' ', '\t', '\r', '\n'):
                self._advance()
                continue

            # Handle single-line comments (# or //)
            if ch == '#' or (ch == '/' and self._peek_next() == '/'):
                while not self._is_at_end() and self._peek() != '\n':
                    self._advance()
                continue

            # Keywords and Identifiers
            if ch.isalpha() or ch == '_':
                tokens.append(self._scan_identifier_or_keyword(start_line, start_col))
                continue

            # Numeric Literals (int or float)
            if ch.isdigit():
                tokens.append(self._scan_number(start_line, start_col))
                continue

            # Operators and Delimiters
            if ch == '+':
                self._advance()
                tokens.append(Token(TokenType.OP_ADD, "+", start_line, start_col))
            elif ch == '-':
                self._advance()
                tokens.append(Token(TokenType.OP_SUB, "-", start_line, start_col))
            elif ch == '*':
                self._advance()
                tokens.append(Token(TokenType.OP_MUL, "*", start_line, start_col))
            elif ch == '/':
                self._advance()
                tokens.append(Token(TokenType.OP_DIV, "/", start_line, start_col))
            elif ch == '%':
                self._advance()
                tokens.append(Token(TokenType.OP_MOD, "%", start_line, start_col))
            elif ch == '=':
                self._advance()
                if self._peek() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.OP_EQ, "==", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.OP_ASSIGN, "=", start_line, start_col))
            elif ch == '>':
                self._advance()
                if self._peek() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.OP_GTE, ">=", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.OP_GT, ">", start_line, start_col))
            elif ch == '<':
                self._advance()
                if self._peek() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.OP_LTE, "<=", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.OP_LT, "<", start_line, start_col))
            elif ch == '!':
                self._advance()
                if self._peek() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.OP_NEQ, "!=", start_line, start_col))
                else:
                    self.errors.append(LexicalError("Unexpected character '!' (did you mean '!='?)", start_line, start_col))
                    tokens.append(Token(TokenType.ERROR, "!", start_line, start_col))
            elif ch == ';':
                self._advance()
                tokens.append(Token(TokenType.SEMICOLON, ";", start_line, start_col))
            elif ch == '(':
                self._advance()
                tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col))
            elif ch == ')':
                self._advance()
                tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col))
            elif ch == '{':
                self._advance()
                tokens.append(Token(TokenType.LBRACE, "{", start_line, start_col))
            elif ch == '}':
                self._advance()
                tokens.append(Token(TokenType.RBRACE, "}", start_line, start_col))
            else:
                self._advance()
                self.errors.append(LexicalError(f"Invalid character '{ch}'", start_line, start_col))
                tokens.append(Token(TokenType.ERROR, ch, start_line, start_col))

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens, self.errors