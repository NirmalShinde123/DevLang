"""
tests/test_semantic.py - Comprehensive Unit Tests for DevLang Semantic Analysis.
Tests all required scope, declaration, and type rule checks.
"""

import unittest
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


class TestDevLangSemanticAnalyzer(unittest.TestCase):

    def _analyze_code(self, code: str):
        lexer = Lexer(code)
        tokens, lex_errs = lexer.tokenize()
        self.assertEqual(len(lex_errs), 0, f"Lexical errors: {lex_errs}")

        parser = Parser(tokens)
        ast, parse_errs = parser.parse()
        self.assertEqual(len(parse_errs), 0, f"Syntax errors: {parse_errs}")

        analyzer = SemanticAnalyzer(ast)
        is_ok, errors, symbol_table = analyzer.analyze()
        return is_ok, errors, symbol_table

    def test_01_valid_declaration(self):
        code = "START\nint a = 10;\nfloat b;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertTrue(is_ok)
        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(st.lookup("a"))
        self.assertIsNotNone(st.lookup("b"))

    def test_02_valid_assignment(self):
        code = "START\nint a;\na = 10;\nfloat b;\nb = a;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertTrue(is_ok)
        self.assertEqual(len(errors), 0)

    def test_03_valid_expression(self):
        code = "START\nint a = 10;\nfloat b = 20.5;\nfloat c = a + b * 2.0;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertTrue(is_ok)
        self.assertEqual(len(errors), 0)

    def test_04_undeclared_variable(self):
        code = "START\nx = 10;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertFalse(is_ok)
        self.assertTrue(any("Undeclared variable 'x'" in str(e) for e in errors))

    def test_05_duplicate_declaration(self):
        code = "START\nint a = 10;\nint a = 20;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertFalse(is_ok)
        self.assertTrue(any("Duplicate declaration" in str(e) for e in errors))

    def test_06_type_mismatch_declaration(self):
        code = "START\nint a = 10.5;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertFalse(is_ok)
        self.assertTrue(any("Type mismatch" in str(e) for e in errors))

    def test_07_invalid_assignment(self):
        code = "START\nint a;\nfloat b = 5.5;\na = b;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertFalse(is_ok)
        self.assertTrue(any("Type mismatch" in str(e) for e in errors))

    def test_08_invalid_expression(self):
        code = "START\nfloat f = 5.5;\nint res = f % 2;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertFalse(is_ok)
        self.assertTrue(any("Modulo operator '%' requires integer operands" in str(e) for e in errors))

    def test_09_scope_related_error(self):
        code = "START\nif (1) {\nint inner = 5;\n}\nprint(inner);\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertFalse(is_ok)
        self.assertTrue(any("Undeclared variable 'inner'" in str(e) for e in errors))

    def test_10_valid_if_while_conditions(self):
        code = "START\nint a = 10;\nwhile (a > 0) {\nif (a == 5) {\nprint(a);\n}\na = a - 1;\n}\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertTrue(is_ok)
        self.assertEqual(len(errors), 0)

    def test_11_uninitialized_variable_usage(self):
        code = "START\nint a;\nint b = a + 1;\nEND"
        is_ok, errors, st = self._analyze_code(code)
        self.assertFalse(is_ok)
        self.assertTrue(any("used before initialization" in str(e) for e in errors))


if __name__ == "__main__":
    unittest.main()