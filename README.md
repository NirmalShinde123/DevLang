# DevLang Compiler & IDE Platform

**DevLang** is a custom, statically-typed, imperative programming language engineered to demonstrate the end-to-end architecture of modern compilers. Designed with an educational and research focus, DevLang processes high-level code through a multi-stage compilation pipeline—spanning Lexical Analysis, Recursive Descent Parsing, Scoped Semantic Analysis, and Intermediate Three-Address Code (TAC) Generation.

The platform provides a flexible multi-mode setup, allowing developers and evaluators to interact with the language via a **Desktop Tkinter Interface**, a **Flask Web API with Backend Pipeline**, or a zero-dependency **Browser-Based Standalone IDE**.

---

## 🗂️ Complete Directory Structure

```text
DevLang/
│
├── main.py                   # Core Compiler CLI Driver
├── lexer.py                  # Lexical Analyzer (Regex-based Tokenizer)
├── tokens.py                 # Token Class Definitions and Type Enum
├── parser.py                 # Recursive Descent Parser & AST Constructor
├── grammar.py                # Formal Grammar Definition Loader
├── ast_nodes.py              # Abstract Syntax Tree Node Classes
├── semantic_analyzer.py      # Type Checking & Scope Validation Engine
├── symbol_table.py           # Scoped Symbol Table & Identifier Resolution
├── tac_generator.py          # Intermediate Code Generator (Three-Address Code)
├── error_handler.py          # Error Classes & Line/Col Reporting Framework
│
├── gui.py                    # Desktop GUI (Tkinter Native App)
├── app.py                    # Flask Web Server Backend API
│
├── templates/                # Server-rendered Web Pages
│   └── index.html            # Web IDE connected to Python Flask Backend
│
├── browser-version/          # Standalone Option (No Backend Required)
│   └── index.html            # Single-File JavaScript-based Engine
│
├── examples/                 # Sample Programs (.dvl)
│   ├── valid_program1.dvl    # Multi-variable Math & Logic
│   ├── valid_program2.dvl    # Nested Loops & Control Flow
│   ├── lexical_error.dvl     # Unrecognized symbol test
│   ├── syntax_error.dvl      # Missing semicolon / bracket mismatch
│   └── semantic_error.dvl    # Type mismatch & Undefined Variable test
│
├── grammar.txt               # Formal EBNF Grammar Specification
├── requirements.txt          # Python Dependencies
└── README.md                 # Complete System Manual & Project Documentation
```

---

## ⚙️ Compiler Architecture & Pipeline Stages

DevLang translates high-level source code into Intermediate Representation (TAC) across five distinct compiler phases:

```text
  [ Source Code (.dvl) ]
            │
            ▼
   ┌─────────────────┐
   │ Lexical Analyzer│ ──> Token Stream (Type, Value, Line, Column)
   └─────────────────┘
            │
            ▼
   ┌─────────────────┐
   │ Syntax Analyzer │ ──> Abstract Syntax Tree (AST)
   └─────────────────┘
            │
            ▼
   ┌─────────────────┐
   │ Semantic Engine │ <──> Scoped Symbol Table (Scope Stack)
   └─────────────────┘
            │
            ▼
   ┌─────────────────┐
   │  TAC Generator  │ ──> Three-Address Code (Quadruples / Triples)
   └─────────────────┘
```

### 1. Lexical Analysis (`lexer.py`, `tokens.py`)
The Lexer converts the raw input string into a stream of strongly-typed `Token` objects. It tracks exact row and column position for accurate error reporting. It handles:
- Reserved keywords (`START`, `END`, `int`, `float`, `if`, `else`, `while`, `print`).
- Arithmetic, relational, and logical operators.
- Strip comments (`//`) and whitespace gracefully.

### 2. Syntax Analysis & Parsing (`parser.py`, `ast_nodes.py`)
Implemented using a Predictive **Recursive Descent Parser** following an LL(1) non-ambiguous context-free grammar.
- Validates formal program structures.
- Constructs a concrete Abstract Syntax Tree (AST) representing statements, binary operations, conditional branches, and loop nodes.

### 3. Semantic Analysis & Symbol Table (`semantic_analyzer.py`, `symbol_table.py`)
Performs contextual checks over the AST using a nested **Scoped Symbol Table**:
- **Scope Resolution:** Supports global and localized block scopes (e.g., inside `{}` blocks).
- **Declaration Checking:** Throws errors for double variable declarations within the same scope or usage of uninitialized/undeclared variables.
- **Type Checking:** Enforces static typing rules between `int` and `float` variables and flags invalid implicit conversions.

### 4. Intermediate Code Generation (`tac_generator.py`)
Translates the validated AST into **Three-Address Code (TAC)** instructions utilizing temporary variables (`t1`, `t2`, ...) and conditional control-flow labels (`L1`, `L2`, ...).

---

## 🔤 Language Specifications

### Syntax & Program Structure
Every valid DevLang file must start with the keyword `START` and conclude with `END`.

```devlang
START
    int x = 10;
    float y = 20.5;
    
    if (x < 15) {
        float result = x + y;
        print(result);
    }
END
```

### Supported Data Types & Literals
- **`int`**: Whole numbers (e.g., `42`, `-7`).
- **`float`**: Decimal numeric values (e.g., `3.1415`, `0.5`).

### Supported Operators
- **Arithmetic:** `+`, `-`, `*`, `/`, `%`
- **Relational:** `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Assignment:** `=`

---

## 🚀 How to Run DevLang

You can run DevLang using three primary deployment modes depending on your requirement:

### Option 1: Standalone Web IDE (No Setup / Zero Backend)
A pure client-side implementation of the compiler pipeline written entirely in JavaScript.
1. Navigate to `browser-version/` folder.
2. Double-click `index.html` to launch it directly in Chrome, Edge, Firefox, or Safari.
3. Write/load code and click **Compile All** to see Lexer, Parser, Symbol Table, and TAC outputs instantaneously.

### Option 2: Flask Web Application (Python Backend API)
Runs the Python-based compiler pipeline as a RESTful web service.
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run Flask server:
   ```bash
   python app.py
   ```
3. Open your browser at `http://127.0.0.1:5000`.

### Option 3: Native Desktop GUI (Tkinter)
For a standalone desktop application experience:
```bash
python gui.py
```

### Option 4: Command Line Interface (CLI)
To run compiler pipeline directly in terminal:
```bash
python main.py examples/valid_program1.dvl
```

---

## 🧪 Error Handling & Diagnostics

DevLang provides detailed contextual error logs identifying exact Line and Column locations for three categories of failure:

1. **Lexical Error:** Invalid characters (e.g., unrecognized special symbols `@`, `#`).
2. **Syntax Error:** Unexpected tokens, missing semicolons `;`, or unclosed brackets `{}`.
3. **Semantic Error:** Type mismatches, redeclaring existing variables, or accessing out-of-scope identifiers.

---

## 📄 License & Academic Attribution
Developed as an educational compiler design project to demonstrate key principles of programming language translation and parsing algorithms.