"""
tests/test_tac.py - Unit Test Suite for DevLang Three Address Code (TAC) Generation.
Verifies IR generation for statements, precedence, control structures, temporaries, and labels.
"""

import unittest
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from tac_generator import TACGenerator


class TestTACGenerator(unittest.TestCase):

    def _generate_tac(self, code: str):
        lexer = Lexer(code)
        tokens, lex_errs = lexer.tokenize()
        self.assertEqual(len(lex_errs), 0, f"Lexical errors: {lex_errs}")

        parser = Parser(tokens)
        ast, parse_errs = parser.parse()
        self.assertEqual(len(parse_errs), 0, f"Syntax errors: {parse_errs}")

        analyzer = SemanticAnalyzer(ast)
        is_ok, sem_errs, _ = analyzer.analyze()
        self.assertTrue(is_ok, f"Semantic errors: {sem_errs}")

        generator = TACGenerator(ast)
        return generator.generate()

    def test_01_simple_assignment(self):
        code = "START\nint a = 10;\na = 20;\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 10",
            "a = 20"
        ]
        self.assertEqual(tac, expected)

    def test_02_simple_arithmetic(self):
        code = "START\nint a = 10;\nint b = 20;\nint c = a + b;\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 10",
            "b = 20",
            "t1 = a + b",
            "c = t1"
        ]
        self.assertEqual(tac, expected)

    def test_03_complex_arithmetic(self):
        code = "START\nint a = 10;\nint b = 20;\nint c = a + b * 2;\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 10",
            "b = 20",
            "t1 = b * 2",
            "t2 = a + t1",
            "c = t2"
        ]
        self.assertEqual(tac, expected)

    def test_04_operator_precedence(self):
        code = "START\nint a = 1;\nint b = 2;\nint c = 3;\nint d = 4;\nint res = a * b + c / d;\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 1",
            "b = 2",
            "c = 3",
            "d = 4",
            "t1 = a * b",
            "t2 = c / d",
            "t3 = t1 + t2",
            "res = t3"
        ]
        self.assertEqual(tac, expected)

    def test_05_relational_expression(self):
        code = "START\nint a = 10;\nint b = 20;\nint cond = a < b;\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 10",
            "b = 20",
            "t1 = a < b",
            "cond = t1"
        ]
        self.assertEqual(tac, expected)

    def test_06_print(self):
        code = "START\nint a = 10;\nprint(a + 5);\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 10",
            "t1 = a + 5",
            "print t1"
        ]
        self.assertEqual(tac, expected)

    def test_07_if_statement(self):
        code = "START\nint a = 10;\nif (a > 5) {\na = a - 1;\n}\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 10",
            "t1 = a > 5",
            "ifFalse t1 goto L1",
            "t2 = a - 1",
            "a = t2",
            "L1:"
        ]
        self.assertEqual(tac, expected)

    def test_08_if_else_statement(self):
        code = "START\nint a = 10;\nif (a == 10) {\na = 1;\n} else {\na = 0;\n}\nEND"
        tac = self._generate_tac(code)
        expected = [
            "a = 10",
            "t1 = a == 10",
            "ifFalse t1 goto L1",
            "a = 1",
            "goto L2",
            "L1:",
            "a = 0",
            "L2:"
        ]
        self.assertEqual(tac, expected)

    def test_09_while_loop(self):
        code = "START\nint count = 3;\nwhile (count > 0) {\ncount = count - 1;\n}\nEND"
        tac = self._generate_tac(code)
        expected = [
            "count = 3",
            "L1:",
            "t1 = count > 0",
            "ifFalse t1 goto L2",
            "t2 = count - 1",
            "count = t2",
            "goto L1",
            "L2:"
        ]
        self.assertEqual(tac, expected)

    def test_10_multiple_temporary_variables(self):
        code = "START\nint x = 1 + 2 + 3 + 4;\nEND"
        tac = self._generate_tac(code)
        expected = [
            "t1 = 1 + 2",
            "t2 = t1 + 3",
            "t3 = t2 + 4",
            "x = t3"
        ]
        self.assertEqual(tac, expected)

    def test_11_multiple_labels(self):
        code = "START\nint x = 0;\nif (x == 0) {\nif (x < 1) {\nx = 5;\n}\n}\nEND"
        tac = self._generate_tac(code)
        expected = [
            "x = 0",
            "t1 = x == 0",
            "ifFalse t1 goto L1",
            "t2 = x < 1",
            "ifFalse t2 goto L2",
            "x = 5",
            "L2:",
            "L1:"
        ]
        self.assertEqual(tac, expected)


if __name__ == "__main__":
    unittest.main()