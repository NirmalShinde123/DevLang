"""
semantic_analyzer.py - Context Validator and Type Checker for DevLang.
Traverses the AST to enforce compile-time rules and scope management.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, PrintNode, BinaryOpNode,
    UnaryOpNode, LiteralNode, VarRefNode
)
from symbol_table import SymbolTable, Symbol


@dataclass
class SemanticErrorRecord:
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"[SEMANTIC_ERROR] Line {self.line}, Column {self.column}: {self.message}"


class SemanticAnalyzer:
    def __init__(self, ast: ProgramNode):
        self.ast: ProgramNode = ast
        self.symbol_table: SymbolTable = SymbolTable()
        self.errors: List[SemanticErrorRecord] = []

    def analyze(self) -> Tuple[bool, List[SemanticErrorRecord], SymbolTable]:
        """Performs full semantic analysis on the provided AST."""
        self.errors.clear()
        self.symbol_table = SymbolTable()
        
        if self.ast:
            self._visit(self.ast)
            
        is_success = len(self.errors) == 0
        return is_success, self.errors, self.symbol_table

    def _add_error(self, message: str, line: int, column: int) -> None:
        self.errors.append(SemanticErrorRecord(message, line, column))

    def _visit(self, node: ASTNode) -> Optional[str]:
        """Dispatcher method that delegates node handling and returns expression type if applicable."""
        method_name = f"_visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node: ASTNode) -> None:
        raise NotImplementedError(f"No semantic analyzer visit method for node type '{node.__class__.__name__}'")

    # AST Node Visitors
    def _visit_ProgramNode(self, node: ProgramNode) -> None:
        self.symbol_table.enter_scope()  # Scope 0: Global Scope
        for stmt in node.statements:
            self._visit(stmt)
        self.symbol_table.exit_scope()

    def _visit_VarDeclNode(self, node: VarDeclNode) -> None:
        # Check initializer if present BEFORE declaring (prevents self-referential initialization)
        is_initialized = False
        if node.initializer is not None:
            init_type = self._visit(node.initializer)
            if init_type is not None:
                # Type Compatibility Matrix Check
                if node.type_name == "int" and init_type == "float":
                    self._add_error(
                        f"Type mismatch: cannot assign 'float' expression to 'int' variable '{node.name}'",
                        node.line, node.column
                    )
                else:
                    is_initialized = True

        # Attempt declaration in current scope
        declared_ok = self.symbol_table.declare(
            name=node.name,
            data_type=node.type_name,
            line=node.line,
            column=node.column,
            is_initialized=is_initialized
        )
        if not declared_ok:
            self._add_error(
                f"Duplicate declaration: variable '{node.name}' is already declared in the current scope",
                node.line, node.column
            )

    def _visit_AssignNode(self, node: AssignNode) -> None:
        sym = self.symbol_table.lookup(node.name)
        val_type = self._visit(node.value)

        if sym is None:
            self._add_error(
                f"Undeclared variable '{node.name}': must be declared before assignment",
                node.line, node.column
            )
            return

        if val_type is not None:
            # Type Compatibility Check
            if sym.data_type == "int" and val_type == "float":
                self._add_error(
                    f"Type mismatch: cannot assign 'float' expression to 'int' variable '{node.name}'",
                    node.line, node.column
                )
            else:
                self.symbol_table.mark_initialized(node.name)

    def _visit_IfNode(self, node: IfNode) -> None:
        cond_type = self._visit(node.condition)
        if cond_type is not None and cond_type not in ("int", "float"):
            self._add_error("Condition in 'if' statement must evaluate to a numeric expression", node.line, node.column)

        # Scoped then-block
        self.symbol_table.enter_scope()
        for stmt in node.then_block:
            self._visit(stmt)
        self.symbol_table.exit_scope()

        # Scoped else-block
        if node.else_block is not None:
            self.symbol_table.enter_scope()
            for stmt in node.else_block:
                self._visit(stmt)
            self.symbol_table.exit_scope()

    def _visit_WhileNode(self, node: WhileNode) -> None:
        cond_type = self._visit(node.condition)
        if cond_type is not None and cond_type not in ("int", "float"):
            self._add_error("Condition in 'while' statement must evaluate to a numeric expression", node.line, node.column)

        # Scoped while-body
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self._visit(stmt)
        self.symbol_table.exit_scope()

    def _visit_PrintNode(self, node: PrintNode) -> None:
        self._visit(node.expr)

    # Expression Evaluators (returns 'int', 'float', or None)
    def _visit_VarRefNode(self, node: VarRefNode) -> Optional[str]:
        sym = self.symbol_table.lookup(node.name)
        if sym is None:
            self._add_error(f"Undeclared variable '{node.name}': variable used before declaration", node.line, node.column)
            return None

        if not sym.is_initialized:
            self._add_error(f"Variable '{node.name}' used before initialization", node.line, node.column)

        return sym.data_type

    def _visit_LiteralNode(self, node: LiteralNode) -> str:
        return node.data_type

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> Optional[str]:
        return self._visit(node.operand)

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> Optional[str]:
        left_type = self._visit(node.left)
        right_type = self._visit(node.right)

        if left_type is None or right_type is None:
            return None

        # Relational operators always return boolean result ('int': 0 or 1)
        if node.op in (">", "<", ">=", "<=", "==", "!="):
            return "int"

        # Modulo operator requires both operands to be integer
        if node.op == "%":
            if left_type != "int" or right_type != "int":
                self._add_error(
                    f"Modulo operator '%' requires integer operands, found '{left_type}' and '{right_type}'",
                    node.line, node.column
                )
                return None
            return "int"

        # Division always results in real float division
        if node.op == "/":
            return "float"

        # Standard arithmetic (+, -, *) type promotion
        if left_type == "float" or right_type == "float":
            return "float"
        return "int"