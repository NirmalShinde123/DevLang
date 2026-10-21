"""
main.py - Main Entry Point and Pipeline Orchestrator for DevLang Compiler.
Coordinates Lexer, Parser, Semantic Analyzer, and TAC Generator without duplicating logic.
Provides a clean API (compile_devlang) for CLI and GUI interfaces.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from lexer import Lexer, Token
from parser import Parser
from ast_nodes import ProgramNode
from semantic_analyzer import SemanticAnalyzer
from symbol_table import SymbolTable
from tac_generator import TACGenerator
from error_handler import ErrorHandler, ErrorType, CompilerError


@dataclass
class CompilationResult:
    """Encapsulates the complete result state of a compilation run."""
    success: bool
    failed_phase: Optional[str] = None
    tokens: List[Token] = field(default_factory=list)
    ast: Optional[ProgramNode] = None
    ast_representation: str = ""
    symbol_table_dump: str = ""
    tac_instructions: List[str] = field(default_factory=list)
    error_report: str = ""
    errors: List[CompilerError] = field(default_factory=list)

    def print_summary(self) -> None:
        """Prints a human-readable summary of the compilation pipeline."""
        print("=" * 60)
        print("               DEVLANG COMPILATION SUMMARY")
        print("=" * 60)
        
        if self.success:
            print("STATUS: Compilation Succeeded!\n")
            print("--- TOKENS GENERATED ---")
            print(f"Total tokens: {len(self.tokens)}")
            for tok in self.tokens:
                print(f"  {tok}")
            
            print("\n--- ABSTRACT SYNTAX TREE (AST) ---")
            print(self.ast_representation)
            
            print("--- SYMBOL TABLE ---")
            print(self.symbol_table_dump)
            
            print("--- THREE ADDRESS CODE (TAC) ---")
            for line in self.tac_instructions:
                print(f"  {line}")
        else:
            print(f"STATUS: Compilation Failed at Phase [{self.failed_phase}]\n")
            print(self.error_report)
        print("=" * 60)


def compile_devlang(source_code: str) -> CompilationResult:
    """
    Main orchestration entry point for DevLang compiler.
    Executes pipeline: Source -> Lexer -> Parser -> Semantic Analyzer -> TAC Generator.
    Stops compilation upon encountering phase errors.
    """
    error_handler = ErrorHandler()

    # PHASE 1: LEXICAL ANALYSIS
    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()
    if lex_errors:
        for err in lex_errors:
            error_handler.add_error(ErrorType.LEXICAL, err.message, err.line, err.column)
        return CompilationResult(
            success=False,
            failed_phase="LEXICAL_ANALYSIS",
            tokens=tokens,
            error_report=error_handler.format_errors(),
            errors=error_handler.errors
        )

    # PHASE 2: SYNTAX ANALYSIS (PARSING)
    parser = Parser(tokens)
    ast, parse_errors = parser.parse()
    if parse_errors or ast is None:
        for err in parse_errors:
            error_handler.add_error(ErrorType.SYNTAX, err.message, err.line, err.column)
        return CompilationResult(
            success=False,
            failed_phase="SYNTAX_ANALYSIS",
            tokens=tokens,
            error_report=error_handler.format_errors(),
            errors=error_handler.errors
        )

    ast_repr = str(ast)

    # PHASE 3: SEMANTIC ANALYSIS & SYMBOL TABLE
    analyzer = SemanticAnalyzer(ast)
    sem_success, sem_errors, symbol_table = analyzer.analyze()
    st_dump = symbol_table.dump()

    if not sem_success:
        for err in sem_errors:
            error_handler.add_error(ErrorType.SEMANTIC, err.message, err.line, err.column)
        return CompilationResult(
            success=False,
            failed_phase="SEMANTIC_ANALYSIS",
            tokens=tokens,
            ast=ast,
            ast_representation=ast_repr,
            symbol_table_dump=st_dump,
            error_report=error_handler.format_errors(),
            errors=error_handler.errors
        )

    # PHASE 4: THREE ADDRESS CODE (TAC) GENERATION
    tac_gen = TACGenerator(ast)
    tac_instructions = tac_gen.generate()

    return CompilationResult(
        success=True,
        tokens=tokens,
        ast=ast,
        ast_representation=ast_repr,
        symbol_table_dump=st_dump,
        tac_instructions=tac_instructions
    )


if __name__ == "__main__":
    sample_code = """START
int a = 10;
int b = 20;
int c = a + b * 2;
print(c);
END"""
    print("Running DevLang Compiler Pipeline on Default Sample...")
    result = compile_devlang(sample_code)
    result.print_summary()