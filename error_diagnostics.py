"""
CMSC 129 - Programming Exercise 02: Lexical Analysis
Member 3: Error Diagnostics

Deliverable:
- Collect ERR_LEX tokens from the token stream
- Build console messages with the unknown word and its line number
"""

from typing import List

from lexer import ERR_LEX, Token

NO_ERRORS_MESSAGE = "No lexical errors found."


def collect_errors(tokens: List[Token]) -> List[Token]:
    return [t for t in tokens if t.name == ERR_LEX]


def format_error(token: Token) -> str:
    return f"Lexical Error: Unknown word '{token.lexeme}' at line {token.line}"


def format_errors(tokens: List[Token]) -> List[str]:
    return [format_error(t) for t in collect_errors(tokens)]


def error_summary(tokens: List[Token]) -> str:
    count = len(collect_errors(tokens))
    if count == 0:
        return NO_ERRORS_MESSAGE
    return f"{count} lexical error(s) found."
