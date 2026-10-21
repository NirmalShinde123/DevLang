"""
gui.py - Professional Tkinter Graphical User Interface for DevLang Compiler.
Integrates directly with main.py and the DevLang backend compiler pipeline.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

# Backend Imports
from main import compile_devlang, CompilationResult
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from tac_generator import TACGenerator
from error_handler import ErrorHandler, ErrorType


SAMPLE_PROGRAMS = {
    "1. Valid Simple Program": """START
int x = 5;
print(x);
END""",

    "2. Complex Arithmetic": """START
int a = 10;
int b = 20;
int c = a + b * 2;
print(c);
END""",

    "3. If-Else Control Flow": """START
int x = 10;
if (x > 5) {
    x = x - 1;
} else {
    x = 0;
}
print(x);
END""",

    "4. While Loop Counter": """START
int count = 3;
while (count > 0) {
    print(count);
    count = count - 1;
}
END""",

    "5. Multiple Variables": """START
int x = 10;
float y = 20.5;
float z = x + y;
print(z);
END""",

    "6. Lexical Error Demo": """START
int @invalid_var = 10;
END""",

    "7. Syntax Error Demo": """START
int a = ;
END""",

    "8. Semantic Error Demo": """START
int x = 10;
float y = 5.5;
x = y;
END"""
}


class DevLangGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DevLang Compiler IDE - Academic Edition")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 700)

        # Apply modern ttk theme styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()

        self.last_result: Optional[CompilationResult] = None

        self._build_layout()

    def _configure_styles(self):
        self.style.configure("TFrame", background="#f4f6f8")
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#f4f6f8", foreground="#2c3e50")
        self.style.configure("Status.TLabel", font=("Consolas", 10, "bold"), background="#ffffff")
        self.style.configure("ActionButton.TButton", font=("Helvetica", 10, "bold"), padding=6)
        self.style.configure("Compile.TButton", font=("Helvetica", 10, "bold"), background="#27ae60", foreground="white")

    def _build_layout(self):
        # Top Header Bar
        header_frame = ttk.Frame(self.root, padding=(10, 10))
        header_frame.pack(fill=tk.X)

        title_label = ttk.Label(header_frame, text="DevLang Compiler Workbench", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)

        # Toolbar Frame
        toolbar_frame = ttk.Frame(self.root, padding=(10, 5))
        toolbar_frame.pack(fill=tk.X)

        # Buttons
        ttk.Button(toolbar_frame, text="▶ Compile All", style="ActionButton.TButton", command=self.on_compile_all).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar_frame, text="1. Lexical Analysis", command=self.on_lexical_analysis).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar_frame, text="2. Syntax Analysis", command=self.on_syntax_analysis).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar_frame, text="3. Generate AST", command=self.on_generate_ast).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar_frame, text="4. Semantic Analysis", command=self.on_semantic_analysis).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar_frame, text="5. Generate TAC", command=self.on_generate_tac).pack(side=tk.LEFT, padx=3)

        # Example Selector & Clear
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        self.example_var = tk.StringVar(value="Load Example...")
        example_combo = ttk.Combobox(toolbar_frame, textvariable=self.example_var, values=list(SAMPLE_PROGRAMS.keys()), state="readonly", width=22)
        example_combo.pack(side=tk.LEFT, padx=3)
        example_combo.bind("<<ComboboxSelected>>", self.on_load_example)

        ttk.Button(toolbar_frame, text="Clear All", command=self.on_clear).pack(side=tk.LEFT, padx=3)

        # Main Split Work Area (PanedWindow)
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Column: Source Code Editor
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=2)

        ttk.Label(left_frame, text="DevLang Source Code", font=("Helvetica", 11, "bold")).pack(anchor=tk.W, pady=(0, 2))
        
        editor_scroll = ttk.Scrollbar(left_frame)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.code_editor = tk.Text(
            left_frame,
            font=("Consolas", 11),
            undo=True,
            wrap=tk.NONE,
            bg="#ffffff",
            fg="#1a1a1a",
            insertbackground="#000000",
            yscrollcommand=editor_scroll.set
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        editor_scroll.config(command=self.code_editor.yview)

        # Default source initialization
        self.code_editor.insert(tk.END, SAMPLE_PROGRAMS["2. Complex Arithmetic"])

        # Right Column: Multi-tab Notebook Visualizer
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Token Table
        self.tab_tokens = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tokens, text="Tokens")
        self._build_token_table()

        # Tab 2: AST View
        self.tab_ast = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ast, text="AST")
        self.ast_text = self._create_scrolled_text(self.tab_ast)

        # Tab 3: Symbol Table
        self.tab_symtable = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_symtable, text="Symbol Table")
        self.symtable_text = self._create_scrolled_text(self.tab_symtable)

        # Tab 4: TAC Output
        self.tab_tac = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tac, text="Intermediate Code (TAC)")
        self.tac_text = self._create_scrolled_text(self.tab_tac)

        # Bottom Panel: Compilation Status and Console Log
        bottom_frame = ttk.Frame(self.root, padding=(10, 5))
        bottom_frame.pack(fill=tk.X)

        # Status Line
        self.status_var = tk.StringVar(value="Ready for compilation.")
        self.status_label = tk.Label(
            bottom_frame,
            textvariable=self.status_var,
            font=("Consolas", 10, "bold"),
            anchor=tk.W,
            bg="#eef2f5",
            fg="#2c3e50",
            padx=10,
            pady=5,
            relief=tk.SUNKEN
        )
        self.status_label.pack(fill=tk.X, pady=(0, 5))

        # Console Log
        ttk.Label(bottom_frame, text="Compiler Diagnostics / Console Output", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        self.console_text = self._create_scrolled_text(bottom_frame, height=7)

    def _build_token_table(self):
        columns = ("#", "Token Type", "Value", "Line", "Column")
        self.token_tree = ttk.Treeview(self.tab_tokens, columns=columns, show="headings")
        
        self.token_tree.heading("#", text="#")
        self.token_tree.heading("Token Type", text="Token Type")
        self.token_tree.heading("Value", text="Value")
        self.token_tree.heading("Line", text="Line")
        self.token_tree.heading("Column", text="Column")

        self.token_tree.column("#", width=40, anchor=tk.CENTER)
        self.token_tree.column("Token Type", width=140, anchor=tk.W)
        self.token_tree.column("Value", width=160, anchor=tk.W)
        self.token_tree.column("Line", width=60, anchor=tk.CENTER)
        self.token_tree.column("Column", width=60, anchor=tk.CENTER)

        tree_scroll = ttk.Scrollbar(self.tab_tokens, orient=tk.VERTICAL, command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=tree_scroll.set)

        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.token_tree.pack(fill=tk.BOTH, expand=True)

    def _create_scrolled_text(self, parent, height=None) -> tk.Text:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        kwargs = {"font": ("Consolas", 10), "bg": "#1e1e1e", "fg": "#d4d4d4", "insertbackground": "#ffffff"}
        if height:
            kwargs["height"] = height

        text_widget = tk.Text(frame, yscrollcommand=scroll.set, **kwargs)
        text_widget.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=text_widget.yview)
        return text_widget

    def _log_console(self, msg: str, clear: bool = False):
        self.console_text.config(state=tk.NORMAL)
        if clear:
            self.console_text.delete("1.0", tk.END)
        self.console_text.insert(tk.END, msg + "\n")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)

    def _update_status(self, text: str, is_error: bool = False):
        self.status_var.set(text)
        if is_error:
            self.status_label.config(bg="#f8d7da", fg="#721c24")
        else:
            self.status_label.config(bg="#d4edda", fg="#155724")

    def _clear_outputs(self):
        # Clear Treeview
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)

        # Clear Text Widgets
        for widget in (self.ast_text, self.symtable_text, self.tac_text):
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.config(state=tk.DISABLED)

        self._log_console("", clear=True)

    # Event Handlers calling Backend
    def on_compile_all(self):
        self._clear_outputs()
        source = self.code_editor.get("1.0", tk.END)
        
        result = compile_devlang(source)
        self.last_result = result

        if result.success:
            self._populate_tokens(result.tokens)
            self._write_text(self.ast_text, result.ast_representation)
            self._write_text(self.symtable_text, result.symbol_table_dump)
            self._write_text(self.tac_text, "\n".join(result.tac_instructions))
            
            self._log_console("✓ Compilation pipeline executed successfully with 0 errors!")
            self._update_status("✓ Compilation Successful - All Phase Pipeline Passed!")
            self.notebook.select(self.tab_tac)
        else:
            if result.tokens:
                self._populate_tokens(result.tokens)
            if result.ast_representation:
                self._write_text(self.ast_text, result.ast_representation)
            if result.symbol_table_dump:
                self._write_text(self.symtable_text, result.symbol_table_dump)

            self._log_console(result.error_report)
            self._update_status(f"✗ Compilation Failed at Phase [{result.failed_phase}]", is_error=True)

    def on_lexical_analysis(self):
        self._clear_outputs()
        source = self.code_editor.get("1.0", tk.END)
        
        lexer = Lexer(source)
        tokens, lex_errs = lexer.tokenize()

        self._populate_tokens(tokens)
        if lex_errs:
            handler = ErrorHandler()
            for err in lex_errs:
                handler.add_error(ErrorType.LEXICAL, err.message, err.line, err.column)
            self._log_console(handler.format_errors())
            self._update_status("✗ Lexical Error Detected!", is_error=True)
        else:
            self._log_console(f"✓ Lexical Analysis Successful: {len(tokens)} tokens generated.")
            self._update_status("✓ Lexical Analysis Completed Successfully")
            self.notebook.select(self.tab_tokens)

    def on_syntax_analysis(self):
        self._clear_outputs()
        source = self.code_editor.get("1.0", tk.END)
        
        lexer = Lexer(source)
        tokens, lex_errs = lexer.tokenize()
        if lex_errs:
            self.on_lexical_analysis()
            return

        self._populate_tokens(tokens)
        parser = Parser(tokens)
        ast, parse_errs = parser.parse()

        if parse_errs or ast is None:
            handler = ErrorHandler()
            for err in parse_errs:
                handler.add_error(ErrorType.SYNTAX, err.message, err.line, err.column)
            self._log_console(handler.format_errors())
            self._update_status("✗ Syntax Error Detected!", is_error=True)
        else:
            self._log_console("✓ Syntax Analysis Successful: Valid parse tree generated.")
            self._update_status("✓ Syntax Analysis Completed Successfully")

    def on_generate_ast(self):
        self.on_syntax_analysis()
        source = self.code_editor.get("1.0", tk.END)
        lexer = Lexer(source)
        tokens, _ = lexer.tokenize()
        parser = Parser(tokens)
        ast, errs = parser.parse()
        
        if ast and not errs:
            self._write_text(self.ast_text, str(ast))
            self.notebook.select(self.tab_ast)

    def on_semantic_analysis(self):
        self._clear_outputs()
        source = self.code_editor.get("1.0", tk.END)
        
        result = compile_devlang(source)
        if result.tokens:
            self._populate_tokens(result.tokens)
        if result.ast_representation:
            self._write_text(self.ast_text, result.ast_representation)

        if result.failed_phase in ("LEXICAL_ANALYSIS", "SYNTAX_ANALYSIS"):
            self._log_console(result.error_report)
            self._update_status(f"✗ Failed at earlier stage: {result.failed_phase}", is_error=True)
            return

        self._write_text(self.symtable_text, result.symbol_table_dump)

        if result.failed_phase == "SEMANTIC_ANALYSIS":
            self._log_console(result.error_report)
            self._update_status("✗ Semantic Error Detected!", is_error=True)
        else:
            self._log_console("✓ Semantic Analysis Successful: Symbol Table generated, scope & type rules verified.")
            self._update_status("✓ Semantic Analysis Completed Successfully")
            self.notebook.select(self.tab_symtable)

    def on_generate_tac(self):
        self.on_compile_all()

    def on_load_example(self, event=None):
        selected = self.example_var.get()
        if selected in SAMPLE_PROGRAMS:
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert(tk.END, SAMPLE_PROGRAMS[selected])
            self._clear_outputs()
            self._update_status(f"Loaded example: {selected}")

    def on_clear(self):
        self.code_editor.delete("1.0", tk.END)
        self._clear_outputs()
        self.status_var.set("Editor cleared.")
        self.status_label.config(bg="#eef2f5", fg="#2c3e50")

    def _populate_tokens(self, tokens):
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        for idx, tok in enumerate(tokens, 1):
            self.token_tree.insert("", tk.END, values=(idx, tok.type.name, repr(tok.value), tok.line, tok.column))

    def _write_text(self, widget: tk.Text, text: str):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = DevLangGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()