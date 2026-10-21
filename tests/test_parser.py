"""
tests/test_parser.py - Suite covering all 15 Phase 2 syntax requirements.
"""

import unittest
from lexer import Lexer
from parser import Parser
from ast_nodes import (
    ProgramNode, VarDeclNode, AssignNode, BinaryOpNode,
    IfNode, WhileNode, PrintNode, LiteralNode, VarRefNode
)


class TestDevLangParser(unittest.TestCase):

    def _parse_code(self, code: str):
        lexer = Lexer(code)
        tokens, lex_errors = lexer.tokenize()
        self.assertEqual(len(lex_errors), 0, f"Lexical errors present: {lex_errors}")
        parser = Parser(tokens)
        ast, errors = parser.parse()
        return ast, errors

    def test_01_valid_minimal_program(self):
        code = "START\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 0)

    def test_02_variable_declarations(self):
        code = "START\nint a;\nfloat b = 10.5;\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(ast.statements), 2)
        self.assertIsInstance(ast.statements[0], VarDeclNode)
        self.assertEqual(ast.statements[0].name, "a")
        self.assertIsNone(ast.statements[0].initializer)
        self.assertIsInstance(ast.statements[1].initializer, LiteralNode)

    def test_03_assignments(self):
        code = "START\na = 20;\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        self.assertIsInstance(ast.statements[0], AssignNode)
        self.assertEqual(ast.statements[0].name, "a")

    def test_04_expressions(self):
        code = "START\nint val = a + b * c;\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        decl = ast.statements[0]
        self.assertIsInstance(decl.initializer, BinaryOpNode)

    def test_05_operator_precedence(self):
        # Should parse 1 + (2 * 3)
        code = "START\nint res = 1 + 2 * 3;\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        add_node = ast.statements[0].initializer
        self.assertEqual(add_node.op, "+")
        self.assertIsInstance(add_node.left, LiteralNode)
        self.assertEqual(add_node.left.value, 1)
        self.assertIsInstance(add_node.right, BinaryOpNode)
        self.assertEqual(add_node.right.op, "*")

    def test_06_print_statement(self):
        code = "START\nprint(a + 5);\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        self.assertIsInstance(ast.statements[0], PrintNode)

    def test_07_if_statement(self):
        code = "START\nif (a > 0) {\nprint(a);\n}\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        if_node = ast.statements[0]
        self.assertIsInstance(if_node, IfNode)
        self.assertIsNone(if_node.else_block)

    def test_08_if_else_statement(self):
        code = "START\nif (a > 0) {\nprint(a);\n} else {\nprint(0);\n}\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        if_node = ast.statements[0]
        self.assertIsNotNone(if_node.else_block)

    def test_09_while_statement(self):
        code = "START\nwhile (a > 0) {\na = a - 1;\n}\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        self.assertIsInstance(ast.statements[0], WhileNode)

    def test_10_nested_expressions(self):
        code = "START\nint res = (a + b) * (c - d);\nEND"
        ast, errors = self._parse_code(code)
        self.assertEqual(len(errors), 0)
        mul_node = ast.statements[0].initializer
        self.assertEqual(mul_node.op, "*")
        self.assertEqual(mul_node.left.op, "+")
        self.assertEqual(mul_node.right.op, "-")

    def test_11_missing_semicolon(self):
        code = "START\nint a = 10\nEND"
        ast, errors = self._parse_code(code)
        self.assertIsNone(ast)
        self.assertTrue(any("Expected ';'" in err.message for err in errors))

    def test_12_missing_brace(self):
        code = "START\nif (a > 0) {\nprint(a);\nEND"
        ast, errors = self._parse_code(code)
        self.assertIsNone(ast)
        self.assertTrue(any("Expected '}'" in err.message for err in errors))

    def test_13_invalid_syntax(self):
        code = "START\nint = 10;\nEND"
        ast, errors = self._parse_code(code)
        self.assertIsNone(ast)
        self.assertTrue(len(errors) > 0)

    def test_14_invalid_program_structure(self):
        code = "START\nint a = 10;\nEND\nint b = 20;"
        ast, errors = self._parse_code(code)
        self.assertIsNone(ast)
        self.assertTrue(any("Unexpected tokens after 'END'" in err.message for err in errors))

    def test_15_start_end_errors(self):
        code = "int a = 10;\nEND"
        ast, errors = self._parse_code(code)
        self.assertIsNone(ast)
        self.assertTrue(any("Expected 'START'" in err.message for err in errors))


if __name__ == "__main__":
    unittest.main()