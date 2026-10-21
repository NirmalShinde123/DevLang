"""
grammar.py - Formal Context-Free Grammar (CFG) specification for DevLang.
Serves as the structural reference for the Recursive Descent Parser.
"""

DEVLANG_GRAMMAR = """
Program         ::= "START" StatementList "END" ;

StatementList   ::= Statement* ;

Statement       ::= VarDeclStmt
                  | AssignStmt
                  | IfStmt
                  | WhileStmt
                  | PrintStmt ;

VarDeclStmt     ::= Type IDENTIFIER ( "=" Expression )? ";" ;

AssignStmt      ::= IDENTIFIER "=" Expression ";" ;

IfStmt          ::= "if" "(" Expression ")" "{" StatementList "}" ( "else" "{" StatementList "}" )? ;

WhileStmt       ::= "while" "(" Expression ")" "{" StatementList "}" ;

PrintStmt       ::= "print" "(" Expression ")" ";" ;

Type            ::= "int" | "float" ;

Expression      ::= RelationalExpr ;

RelationalExpr  ::= AdditiveExpr ( RelOp AdditiveExpr )* ;

RelOp           ::= ">" | "<" | ">=" | "<=" | "==" | "!=" ;

AdditiveExpr    ::= MultiplicativeExpr ( AddOp MultiplicativeExpr )* ;

AddOp           ::= "+" | "-" ;

MultiplicativeExpr ::= Factor ( MulOp Factor )* ;

MulOp           ::= "*" | "/" | "%" ;

Factor          ::= IDENTIFIER
                  | INT_LITERAL
                  | FLOAT_LITERAL
                  | "(" Expression ")"
                  | "-" Factor ;
"""

# Operator Precedence and Associativity Table
OPERATOR_PRECEDENCE = {
    "unary_-": {"precedence": 1, "associativity": "Right-to-Left"},
    "*":       {"precedence": 2, "associativity": "Left-to-Right"},
    "/":       {"precedence": 2, "associativity": "Left-to-Right"},
    "%":       {"precedence": 2, "associativity": "Left-to-Right"},
    "+":       {"precedence": 3, "associativity": "Left-to-Right"},
    "-":       {"precedence": 3, "associativity": "Left-to-Right"},
    ">":       {"precedence": 4, "associativity": "Left-to-Right"},
    "<":       {"precedence": 4, "associativity": "Left-to-Right"},
    ">=":      {"precedence": 4, "associativity": "Left-to-Right"},
    "<=":      {"precedence": 4, "associativity": "Left-to-Right"},
    "=="":      {"precedence": 4, "associativity": "Left-to-Right"},
    "!=":      {"precedence": 4, "associativity": "Left-to-Right"},
}