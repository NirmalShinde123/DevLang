"""
ast_nodes.py - Abstract Syntax Tree (AST) node definitions for DevLang.
Provides clean dataclass structures with tree formatting methods.
"""

from dataclasses import dataclass, field
from typing import Union, Optional, List


@dataclass
class ASTNode:
    line: int
    column: int

    def dump(self, indent: int = 0) -> str:
        """Returns a human-readable hierarchical tree string representation of the AST."""
        prefix = "  " * indent
        return f"{prefix}{self.__class__.__name__}"


@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        result = [f"{prefix}ProgramNode"]
        for stmt in self.statements:
            result.append(stmt.dump(indent + 1))
        return "\n".join(result)


@dataclass
class VarDeclNode(ASTNode):
    type_name: str
    name: str
    initializer: Optional[ASTNode] = None

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        init_str = f"\n{self.initializer.dump(indent + 2)}" if self.initializer else ""
        return f"{prefix}VarDeclNode({self.type_name} {self.name}){init_str}"


@dataclass
class AssignNode(ASTNode):
    name: str
    value: ASTNode

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}AssignNode({self.name} =)\n{self.value.dump(indent + 1)}"


@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        result = [
            f"{prefix}IfNode",
            f"{prefix}  Condition:",
            self.condition.dump(indent + 2),
            f"{prefix}  Then:"
        ]
        for stmt in self.then_block:
            result.append(stmt.dump(indent + 2))

        if self.else_block is not None:
            result.append(f"{prefix}  Else:")
            for stmt in self.else_block:
                result.append(stmt.dump(indent + 2))

        return "\n".join(result)


@dataclass
class WhileNode(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        result = [
            f"{prefix}WhileNode",
            f"{prefix}  Condition:",
            self.condition.dump(indent + 2),
            f"{prefix}  Body:"
        ]
        for stmt in self.body:
            result.append(stmt.dump(indent + 2))
        return "\n".join(result)


@dataclass
class PrintNode(ASTNode):
    expr: ASTNode

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}PrintNode\n{self.expr.dump(indent + 1)}"


@dataclass
class BinaryOpNode(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return (f"{prefix}BinaryOpNode('{self.op}')\n"
                f"{self.left.dump(indent + 1)}\n"
                f"{self.right.dump(indent + 1)}")


@dataclass
class UnaryOpNode(ASTNode):
    op: str
    operand: ASTNode

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}UnaryOpNode('{self.op}')\n{self.operand.dump(indent + 1)}"


@dataclass
class LiteralNode(ASTNode):
    value: Union[int, float]
    data_type: str  # 'int' or 'float'

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}LiteralNode({self.value}: {self.data_type})"


@dataclass
class VarRefNode(ASTNode):
    name: str

    def dump(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}VarRefNode({self.name})"