"""
CMSC 129 - Programming Exercise 02: Lexical Analysis
Main Program Entry Point (PE02.py)

Work Distribution:
- Member 1: Lexer Core / Scanner (Implemented in lexer.py)
- Member 2: Compiler UI / Controller / File I/O
- Member 3: Error Diagnostics & Variable Table
- Member 4: Token Formatter, Documentation, QA, Packaging
"""

from lexer import tokenize, Token, INT_LIT, IDENT, ERR_LEX, KEYWORDS


if __name__ == "__main__":
    # Ready for integration by Member 2 (UI / Controller)
    print("CMSC 129 - PE02: Lexical Analyzer")
    print("Member 1 (Lexer Core) loaded.")
