"""
CMSC 129 - Programming Exercise 02: Lexical Analysis
Member 3: Variable / Symbol Table

Deliverable:
- Scan the token stream for variable declarations
- Extract the variable name and type
- Return (name, type) rows for the Table of Variables in the UI

IOL declaration forms (see the language specification):
    data_type var_name
    data_type var_name IS value
where data_type is INT or STR, e.g. "INT num IS 0" and "STR msg1".
"""

from typing import List, Tuple

from lexer import IDENT, Token

TYPE_NAMES = ("INT", "STR")


def build_variable_table(tokens: List[Token]) -> List[Tuple[str, str]]:
    variables: List[Tuple[str, str]] = []
    seen = set()
    for i, token in enumerate(tokens[:-1]):
        if token.name not in TYPE_NAMES:
            continue
        name_token = tokens[i + 1]
        if name_token.name != IDENT:
            continue
        if name_token.lexeme in seen:
            continue
        seen.add(name_token.lexeme)
        variables.append((name_token.lexeme, token.name))
    return variables
