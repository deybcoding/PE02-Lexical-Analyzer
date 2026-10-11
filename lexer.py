"""
CMSC 129 - Programming Exercise 02: Lexical Analysis
Member 1: Lexer Core / Scanner

Deliverable:
- Token constants (INT_LIT, IDENT, ERR_LEX, and keywords)
- Character-by-character scanner
- Line and column tracking
- Recognition of integers, identifiers, keywords, and error lexemes
- Token list with name, lexeme, line, column
"""

from typing import List, Optional, Set


# ==========================================
# 1. Token Constants
# ==========================================

INT_LIT = "INT_LIT"
IDENT = "IDENT"
ERR_LEX = "ERR_LEX"

# Standard / core keywords for the custom programming language.
# The token name for each keyword is the keyword string itself.
DEFAULT_KEYWORDS: Set[str] = {
    "IOL",
    "LOI",
    "INT",
    "STR",
    "IS",
    "INTO",
    "BEG",
    "PRINT",
    "NEWLN",
    "ADD",
    "SUB",
    "MULT",
    "DIV",
    "MOD",
}

# Active keyword set (can be extended or customized if needed)
KEYWORDS: Set[str] = set(DEFAULT_KEYWORDS)


def set_keywords(custom_keywords: Set[str]) -> None:
    """Updates the recognized keywords set."""
    global KEYWORDS
    KEYWORDS = set(custom_keywords)


def add_keywords(*words: str) -> None:
    """Adds additional keywords to the recognized set."""
    global KEYWORDS
    for word in words:
        KEYWORDS.add(word)


def is_letter(char: Optional[str]) -> bool:
    return char is not None and ("a" <= char <= "z" or "A" <= char <= "Z")


def is_digit(char: Optional[str]) -> bool:
    return char is not None and "0" <= char <= "9"


# ==========================================
# 2. Token Data Structure
# ==========================================

class Token:
    """
    Represents a recognized token from the source code.
    Attributes:
        name (str): Token name (e.g. 'INT_LIT', 'IDENT', 'ERR_LEX', or keyword name).
        lexeme (str): The actual raw text matched from the input source.
        line (int): 1-based line number where the token starts.
        column (int): 1-based column number where the token starts.
    """

    def __init__(self, name: str, lexeme: str, line: int, column: int):
        self.name: str = name
        self.lexeme: str = lexeme
        self.line: int = line
        self.column: int = column

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
        }

    def __repr__(self) -> str:
        return f"Token({self.name!r}, {self.lexeme!r}, line={self.line}, col={self.column})"

    def __str__(self) -> str:
        return f"<{self.name}, {self.lexeme}> at Line {self.line}, Col {self.column}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False
        return (
            self.name == other.name
            and self.lexeme == other.lexeme
            and self.line == other.line
            and self.column == other.column
        )


# ==========================================
# 3. Lexer Core (Character-by-Character Scanner)
# ==========================================

class Lexer:
    """
    Character-by-character scanner for the custom programming language.
    """

    def __init__(self, source_code: str, keywords: Optional[Set[str]] = None):
        self.source: str = source_code
        self.length: int = len(source_code)
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.keywords: Set[str] = keywords if keywords is not None else KEYWORDS

    def _peek(self) -> Optional[str]:
        """Returns the current character without advancing."""
        if self.pos < self.length:
            return self.source[self.pos]
        return None

    def _peek_next(self) -> Optional[str]:
        """Returns the next character without advancing."""
        if self.pos + 1 < self.length:
            return self.source[self.pos + 1]
        return None

    def _advance(self) -> Optional[str]:
        """Consumes and returns the current character, updating line and column."""
        if self.pos >= self.length:
            return None

        char = self.source[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        elif char == "\r":
            # Handle Windows \r\n newline sequence: if followed by \n, let \n handle line increment
            if self._peek() == "\n":
                pass
            else:
                self.line += 1
                self.column = 1
        else:
            self.column += 1

        return char

    def _is_delimiter(self, char: Optional[str]) -> bool:
        return char is None or char.isspace()

    def _consume_rest_of_word(self, lexeme_chars: List[str]) -> None:
        while not self._is_delimiter(self._peek()):
            lexeme_chars.append(self._advance())

    def _scan_number(self, start_line: int, start_col: int) -> Token:
        """
        Scans an integer literal. If the digits are not immediately followed by
        whitespace (e.g. '123abc'), the whole word is scanned as an ERR_LEX.
        """
        lexeme_chars = []
        while is_digit(self._peek()):
            lexeme_chars.append(self._advance())

        if not self._is_delimiter(self._peek()):
            self._consume_rest_of_word(lexeme_chars)
            return Token(ERR_LEX, "".join(lexeme_chars), start_line, start_col)

        return Token(INT_LIT, "".join(lexeme_chars), start_line, start_col)

    def _scan_identifier_or_keyword(self, start_line: int, start_col: int) -> Token:
        """
        Scans an identifier or keyword: a letter followed by letters or digits.
        A word containing any other character is scanned as an ERR_LEX.
        """
        lexeme_chars = []
        while is_letter(self._peek()) or is_digit(self._peek()):
            lexeme_chars.append(self._advance())

        if not self._is_delimiter(self._peek()):
            self._consume_rest_of_word(lexeme_chars)
            return Token(ERR_LEX, "".join(lexeme_chars), start_line, start_col)

        lexeme = "".join(lexeme_chars)

        # Keyword tokens are the keyword names themselves
        if lexeme in self.keywords:
            return Token(lexeme, lexeme, start_line, start_col)

        return Token(IDENT, lexeme, start_line, start_col)

    def _scan_error(self, start_line: int, start_col: int) -> Token:
        """
        Scans an unknown word (up to the next whitespace) as an ERR_LEX token.
        """
        lexeme_chars = []
        self._consume_rest_of_word(lexeme_chars)
        return Token(ERR_LEX, "".join(lexeme_chars), start_line, start_col)

    def tokenize(self) -> List[Token]:
        """
        Scans the entire source code character by character and returns
        the list of recognized tokens.
        """
        tokens: List[Token] = []

        while self.pos < self.length:
            char = self._peek()

            # Ignore whitespace characters (spaces, tabs, newlines)
            if char.isspace():
                self._advance()
                continue

            start_line = self.line
            start_col = self.column

            # Integer literals
            if is_digit(char):
                tokens.append(self._scan_number(start_line, start_col))
            # Identifiers or keywords
            elif is_letter(char):
                tokens.append(self._scan_identifier_or_keyword(start_line, start_col))
            # Unknown / Error lexemes
            else:
                tokens.append(self._scan_error(start_line, start_col))

        return tokens


# ==========================================
# 4. Helper Function
# ==========================================

def tokenize(source_code: str, keywords: Optional[Set[str]] = None) -> List[Token]:
    """
    Convenience function to scan and tokenize source code.
    Returns:
        List[Token]: list of recognized tokens with name, lexeme, line, column.
    """
    lexer = Lexer(source_code, keywords)
    return lexer.tokenize()
