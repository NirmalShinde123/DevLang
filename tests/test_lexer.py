"""
tests/test_lexer.py - Comprehensive Unit Tests for DevLang Lexical Analyzer.
Tests all 14 required lexical requirements.
"""

import unittest
from tokens import TokenType
from lexer import Lexer


class TestDevLangLexer(unittest.TestCase):

    def test_01_keywords(self):
        source = "START END int float if else while print"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        expected = [
            TokenType.KEYWORD_START, TokenType.KEYWORD_END,
            TokenType.KEYWORD_INT, TokenType.KEYWORD_FLOAT,
            TokenType.KEYWORD_IF, TokenType.KEYWORD_ELSE,
            TokenType.KEYWORD_WHILE, TokenType.KEYWORD_PRINT,
            TokenType.EOF
        ]
        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens], expected)

    def test_02_identifiers(self):
        source = "var1 _count total_sum A_b_C"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens[:-1]], [TokenType.IDENTIFIER] * 4)
        self.assertEqual([t.value for t in tokens[:-1]], ["var1", "_count", "total_sum", "A_b_C"])

    def test_03_integers(self):
        source = "0 10 9999"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens[:-1]], [TokenType.INT_LITERAL] * 3)
        self.assertEqual([t.value for t in tokens[:-1]], [0, 10, 9999])

    def test_04_floats(self):
        source = "0.0 10.5 3.14159"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens[:-1]], [TokenType.FLOAT_LITERAL] * 3)
        self.assertEqual([t.value for t in tokens[:-1]], [0.0, 10.5, 3.14159])

    def test_05_arithmetic_operators(self):
        source = "+ - * / %"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        expected = [
            TokenType.OP_ADD, TokenType.OP_SUB,
            TokenType.OP_MUL, TokenType.OP_DIV,
            TokenType.OP_MOD, TokenType.EOF
        ]
        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens], expected)

    def test_06_relational_operators(self):
        source = "> < >= <= == !="
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        expected = [
            TokenType.OP_GT, TokenType.OP_LT,
            TokenType.OP_GTE, TokenType.OP_LTE,
            TokenType.OP_EQ, TokenType.OP_NEQ,
            TokenType.EOF
        ]
        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens], expected)

    def test_07_assignment(self):
        source = "="
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)
        self.assertEqual(tokens[0].type, TokenType.OP_ASSIGN)

    def test_08_parentheses(self):
        source = "( )"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens[:-1]], [TokenType.LPAREN, TokenType.RPAREN])

    def test_09_braces(self):
        source = "{ }"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens[:-1]], [TokenType.LBRACE, TokenType.RBRACE])

    def test_10_semicolon(self):
        source = ";"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)
        self.assertEqual(tokens[0].type, TokenType.SEMICOLON)

    def test_11_complete_valid_statement(self):
        source = "int sum = a + 10;"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        expected_types = [
            TokenType.KEYWORD_INT, TokenType.IDENTIFIER,
            TokenType.OP_ASSIGN, TokenType.IDENTIFIER,
            TokenType.OP_ADD, TokenType.INT_LITERAL,
            TokenType.SEMICOLON, TokenType.EOF
        ]
        self.assertEqual(len(errors), 0)
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_12_invalid_character(self):
        source = "int a = $10;"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid character '$'", str(errors[0]))
        self.assertEqual(errors[0].line, 1)
        self.assertEqual(errors[0].column, 9)

    def test_13_malformed_input(self):
        source = "float x = 12.34.56;"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 1)
        self.assertIn("Malformed float literal '12.34.56'", str(errors[0]))
        self.assertEqual(errors[0].line, 1)
        self.assertEqual(errors[0].column, 11)

    def test_14_line_and_column_tracking(self):
        source = "START\n  int a = 10;\nEND"
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()

        self.assertEqual(len(errors), 0)

        # START at Line 1, Col 1
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)

        # int at Line 2, Col 3
        self.assertEqual(tokens[1].line, 2)
        self.assertEqual(tokens[1].column, 3)

        # END at Line 3, Col 1
        self.assertEqual(tokens[7].line, 3)
        self.assertEqual(tokens[7].column, 1)


if __name__ == "__main__":
    unittest.main()