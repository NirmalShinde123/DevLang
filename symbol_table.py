"""
symbol_table.py - Symbol Table and Scope Stack Manager for DevLang.
Tracks variable declarations, data types, scope levels, and initialization states.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class Symbol:
    name: str
    data_type: str          # 'int' or 'float'
    is_initialized: bool
    line_declared: int
    column_declared: int
    scope_level: int

    def __repr__(self) -> str:
        return (f"Symbol(name='{self.name}', type='{self.data_type}', "
                f"init={self.is_initialized}, line={self.line_declared}, scope={self.scope_level})")


class SymbolTable:
    def __init__(self):
        # Stack of scopes (each scope is a dictionary mapping identifier name -> Symbol)
        self.scopes: List[Dict[str, Symbol]] = []
        self.current_scope_level: int = -1
        # Historical registry of all declared symbols for inspection/reporting
        self.all_symbols: List[Symbol] = []

    def enter_scope(self) -> None:
        """Pushes a new local scope onto the scope stack."""
        self.scopes.append({})
        self.current_scope_level += 1

    def exit_scope(self) -> None:
        """Pops the current scope off the scope stack."""
        if self.scopes:
            self.scopes.pop()
            self.current_scope_level -= 1

    def declare(self, name: str, data_type: str, line: int, column: int, is_initialized: bool = False) -> bool:
        """
        Inserts a symbol into the current (innermost) scope.
        Returns False if duplicate declaration exists in the same scope.
        """
        if not self.scopes:
            self.enter_scope()

        current_scope = self.scopes[-1]
        if name in current_scope:
            return False  # Duplicate in current scope

        sym = Symbol(
            name=name,
            data_type=data_type,
            is_initialized=is_initialized,
            line_declared=line,
            column_declared=column,
            scope_level=self.current_scope_level
        )
        current_scope[name] = sym
        self.all_symbols.append(sym)
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Traverses the scope stack from innermost scope outward to global scope.
        Returns the Symbol if found, otherwise None.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        """Checks if a symbol is declared in the innermost active scope."""
        if self.scopes and name in self.scopes[-1]:
            return self.scopes[-1][name]
        return None

    def mark_initialized(self, name: str) -> bool:
        """Marks a symbol as initialized in the nearest enclosing scope where it exists."""
        sym = self.lookup(name)
        if sym:
            sym.is_initialized = True
            return True
        return False

    def dump(self) -> str:
        """Returns a human-readable tabular representation of all recorded symbols."""
        header = f"{'Name':<12} | {'Type':<8} | {'Initialized':<12} | {'Line':<6} | {'Scope Level':<10}"
        divider = "-" * len(header)
        rows = [header, divider]
        
        for sym in self.all_symbols:
            init_str = "Yes" if sym.is_initialized else "No"
            rows.append(f"{sym.name:<12} | {sym.data_type:<8} | {init_str:<12} | {sym.line_declared:<6} | {sym.scope_level:<10}")
            
        return "\n".join(rows)