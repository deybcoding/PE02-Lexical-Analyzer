# Format lexer tokens for the tokenized-code view and .tkn output.

from typing import List

from lexer import Token


def format_tokens(tokens: List[Token]) -> str:
    """Return token names grouped by source line, ending with a newline.

    Lexemes and source positions remain available on Token objects; the .tkn
    representation is the compact token-name stream shown by the UI.
    """
    if not tokens:
        return ""

    lines: List[List[str]] = [[] for _ in range(tokens[-1].line)]
    for token in tokens:
        lines[token.line - 1].append(token.name)
    return "\n".join(" ".join(names) for names in lines) + "\n"