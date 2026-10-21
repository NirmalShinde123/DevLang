"""
tac_generator.py - Three Address Code (TAC) Generator for DevLang.
Traverses the validated AST and emits flat Intermediate Representation (IR) instructions.
"""

from typing import List, Optional
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignNode,
    IfNode, WhileNode, PrintNode, BinaryOpNode,
    UnaryOpNode, LiteralNode, VarRefNode
)


class TACInstruction:
    """Represents a single Three Address Code instruction tuple."""
    def __init__(self, op: str, arg1: Optional[str] = None, arg2: Optional[str] = None, result: Optional[str] = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __str__(self) -> str:
        if self.op == "LABEL":
            return f"{self.result}:"
        elif self.op == "GOTO":
            return f"goto {self.result}"
        elif self.op == "IFFALSE":
            return f"ifFalse {self.arg1} goto {self.result}"
        elif self.op == "PRINT":
            return f"print {self.arg1}"
        elif self.op == "=":
            return f"{self.result} = {self.arg1}"
        elif self.arg2 is not None:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.arg1 is not None:
            return f"{self.result} = {self.op}{self.arg1}"
        return f"{self.op}"


class TACGenerator:
    def __init__(self, ast: ProgramNode):
        self.ast: ProgramNode = ast
        self.instructions: List[TACInstruction] = []
        self.temp_counter: int = 0
        self.label_counter: int = 0

    def new_temp(self) -> str:
        """Allocates a new temporary variable (t1, t2, t3, ...)."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        """Allocates a new jump label (L1, L2, L3, ...)."""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, op: str, arg1: Optional[str] = None, arg2: Optional[str] = None, result: Optional[str] = None) -> TACInstruction:
        """Appends a TAC instruction to the instruction list."""
        instr = TACInstruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr

    def generate(self) -> List[str]:
        """Performs AST traversal and returns a list of formatted TAC string instructions."""
        self.instructions.clear()
        self.temp_counter = 0
        self.label_counter = 0

        if self.ast:
            self._visit(self.ast)

        return [str(instr) for instr in self.instructions]

    def _visit(self, node: ASTNode) -> Optional[str]:
        """Dispatcher method that visits nodes and returns the holding variable/literal string."""
        method_name = f"_visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node: ASTNode):
        raise NotImplementedError(f"No TAC generation visitor defined for AST node type '{node.__class__.__name__}'")

    # AST Statement Visitors
    def _visit_ProgramNode(self, node: ProgramNode) -> None:
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_VarDeclNode(self, node: VarDeclNode) -> None:
        if node.initializer is not None:
            val_place = self._visit(node.initializer)
            self.emit("=", arg1=val_place, result=node.name)

    def _visit_AssignNode(self, node: AssignNode) -> None:
        val_place = self._visit(node.value)
        self.emit("=", arg1=val_place, result=node.name)

    def _visit_PrintNode(self, node: PrintNode) -> None:
        val_place = self._visit(node.expr)
        self.emit("PRINT", arg1=val_place)

    def _visit_IfNode(self, node: IfNode) -> None:
        cond_place = self._visit(node.condition)
        end_label = self.new_label()

        if node.else_block is not None:
            else_label = self.new_label()
            self.emit("IFFALSE", arg1=cond_place, result=else_label)
            for stmt in node.then_block:
                self._visit(stmt)
            self.emit("GOTO", result=end_label)
            self.emit("LABEL", result=else_label)
            for stmt in node.else_block:
                self._visit(stmt)
            self.emit("LABEL", result=end_label)
        else:
            self.emit("IFFALSE", arg1=cond_place, result=end_label)
            for stmt in node.then_block:
                self._visit(stmt)
            self.emit("LABEL", result=end_label)

    def _visit_WhileNode(self, node: WhileNode) -> None:
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit("LABEL", result=start_label)
        cond_place = self._visit(node.condition)
        self.emit("IFFALSE", arg1=cond_place, result=end_label)

        for stmt in node.body:
            self._visit(stmt)

        self.emit("GOTO", result=start_label)
        self.emit("LABEL", result=end_label)

    # AST Expression Visitors (Return operand location string)
    def _visit_LiteralNode(self, node: LiteralNode) -> str:
        return str(node.value)

    def _visit_VarRefNode(self, node: VarRefNode) -> str:
        return node.name

    def _visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        operand_place = self._visit(node.operand)
        temp = self.new_temp()
        self.emit(op=node.op, arg1=operand_place, result=temp)
        return temp

    def _visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_place = self._visit(node.left)
        right_place = self._visit(node.right)
        temp = self.new_temp()
        self.emit(op=node.op, arg1=left_place, arg2=right_place, result=temp)
        return temp