"""
tokens.py - Token types and Token class definitions for DevLang.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    # Program Boundaries
    KEYWORD_START = auto()
    KEYWORD_END = auto()

    # Data Types
    KEYWORD_INT = auto()
    KEYWORD_FLOAT = auto()

    # Control Flow
    KEYWORD_IF = auto()
    KEYWORD_ELSE = auto()
    KEYWORD_WHILE = auto()

    # I/O Primitives
    KEYWORD_PRINT = auto()

    # Identifiers and Literals
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()

    # Arithmetic Operators
    OP_ADD = auto()       # +
    OP_SUB = auto()       # -
    OP_MUL = auto()       # *
    OP_DIV = auto()       # /
    OP_MOD = auto()       # %

    # Relational Operators
    OP_GT = auto()        # >
    OP_LT = auto()        # <
    OP_GTE = auto()       # >=
    OP_LTE = auto()       # <=
    OP_EQ = auto()        # ==
    OP_NEQ = auto()       # !=

    # Assignment
    OP_ASSIGN = auto()    # =

    # Delimiters
    SEMICOLON = auto()    # ;
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }

    # Special Tokens
    EOF = auto()
    ERROR = auto()


# Keyword lookup mapping
KEYWORDS: dict[str, TokenType] = {
    "START": TokenType.KEYWORD_START,
    "END": TokenType.KEYWORD_END,
    "int": TokenType.KEYWORD_INT,
    "float": TokenType.KEYWORD_FLOAT,
    "if": TokenType.KEYWORD_IF,
    "else": TokenType.KEYWORD_ELSE,
    "while": TokenType.KEYWORD_WHILE,
    "print": TokenType.KEYWORD_PRINT,
}


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"