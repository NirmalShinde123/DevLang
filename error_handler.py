"""
error_handler.py - Centralized Error Management for DevLang.
Provides formatted error reporting for Lexical, Syntax, and Semantic phases.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ErrorType(Enum):
    LEXICAL = "LEXICAL_ERROR"
    SYNTAX = "SYNTAX_ERROR"
    SEMANTIC = "SEMANTIC_ERROR"


@dataclass
class CompilerError:
    error_type: ErrorType
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return (f"[{self.error_type.value}] Line {self.line}, "
                f"Column {self.column}: {self.message}")


class ErrorHandler:
    def __init__(self):
        self.errors: List[CompilerError] = []

    def add_error(self, error_type: ErrorType, message: str, line: int, column: int) -> None:
        """Registers a new error in the compiler error log."""
        self.errors.append(CompilerError(error_type, message, line, column))

    def has_errors(self) -> bool:
        """Returns True if any errors have been logged."""
        return len(self.errors) > 0

    def clear(self) -> None:
        """Clears all logged errors."""
        self.errors.clear()

    def format_errors(self) -> str:
        """Returns a beginner-friendly formatted report of all recorded errors."""
        if not self.errors:
            return "No errors detected."

        output = ["=" * 60, "           DEVLANG COMPILATION ERROR REPORT", "=" * 60]
        for idx, err in enumerate(self.errors, 1):
            output.append(f"Error #{idx}:")
            output.append(f"  Phase   : {err.error_type.value}")
            output.append(f"  Location: Line {err.line}, Column {err.column}")
            output.append(f"  Details : {err.message}")
            output.append("-" * 60)
        return "\n".join(output)