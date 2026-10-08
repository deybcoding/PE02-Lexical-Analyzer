"""
Unit tests for the Lexer Core (Member 1 Deliverable).
"""

import unittest
from lexer import (
    Token,
    Lexer,
    tokenize,
    INT_LIT,
    IDENT,
    ERR_LEX,
    KEYWORDS,
)


class TestLexer(unittest.TestCase):

    def test_integer_literals(self):
        code = "0 42 9999"
        tokens = tokenize(code)
        self.assertEqual(len(tokens), 3)

        self.assertEqual(tokens[0].name, INT_LIT)
        self.assertEqual(tokens[0].lexeme, "0")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)

        self.assertEqual(tokens[1].name, INT_LIT)
        self.assertEqual(tokens[1].lexeme, "42")
        self.assertEqual(tokens[1].line, 1)
        self.assertEqual(tokens[1].column, 3)

        self.assertEqual(tokens[2].name, INT_LIT)
        self.assertEqual(tokens[2].lexeme, "9999")
        self.assertEqual(tokens[2].line, 1)
        self.assertEqual(tokens[2].column, 6)

    def test_keywords(self):
        code = "DEFINE INTO IS"
        tokens = tokenize(code)
        self.assertEqual(len(tokens), 3)

        # Keyword token name must match the keyword itself
        self.assertEqual(tokens[0].name, "DEFINE")
        self.assertEqual(tokens[0].lexeme, "DEFINE")

        self.assertEqual(tokens[1].name, "INTO")
        self.assertEqual(tokens[1].lexeme, "INTO")

        self.assertEqual(tokens[2].name, "IS")
        self.assertEqual(tokens[2].lexeme, "IS")

    def test_identifiers(self):
        code = "myVar count _temp x1"
        tokens = tokenize(code)
        self.assertEqual(len(tokens), 4)

        for tok, lex in zip(tokens, ["myVar", "count", "_temp", "x1"]):
            self.assertEqual(tok.name, IDENT)
            self.assertEqual(tok.lexeme, lex)

    def test_error_lexemes(self):
        code = "@ # 123abc $"
        tokens = tokenize(code)
        self.assertEqual(len(tokens), 4)

        self.assertEqual(tokens[0].name, ERR_LEX)
        self.assertEqual(tokens[0].lexeme, "@")

        self.assertEqual(tokens[1].name, ERR_LEX)
        self.assertEqual(tokens[1].lexeme, "#")

        # Starting with digits and followed by letters is a lexical error
        self.assertEqual(tokens[2].name, ERR_LEX)
        self.assertEqual(tokens[2].lexeme, "123abc")

        self.assertEqual(tokens[3].name, ERR_LEX)
        self.assertEqual(tokens[3].lexeme, "$")

    def test_line_and_column_tracking(self):
        code = "DEFINE num\nIS 42\n  ERR@\nINTO result"
        tokens = tokenize(code)

        # Line 1: DEFINE (1, 1), num (1, 8)
        self.assertEqual(tokens[0].name, "DEFINE")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)

        self.assertEqual(tokens[1].name, IDENT)
        self.assertEqual(tokens[1].lexeme, "num")
        self.assertEqual(tokens[1].line, 1)
        self.assertEqual(tokens[1].column, 8)

        # Line 2: IS (2, 1), 42 (2, 4)
        self.assertEqual(tokens[2].name, "IS")
        self.assertEqual(tokens[2].line, 2)
        self.assertEqual(tokens[2].column, 1)

        self.assertEqual(tokens[3].name, INT_LIT)
        self.assertEqual(tokens[3].lexeme, "42")
        self.assertEqual(tokens[3].line, 2)
        self.assertEqual(tokens[3].column, 4)

        # Line 3: ERR (3, 3), @ (3, 6)
        self.assertEqual(tokens[4].name, IDENT)
        self.assertEqual(tokens[4].lexeme, "ERR")
        self.assertEqual(tokens[4].line, 3)
        self.assertEqual(tokens[4].column, 3)

        self.assertEqual(tokens[5].name, ERR_LEX)
        self.assertEqual(tokens[5].lexeme, "@")
        self.assertEqual(tokens[5].line, 3)
        self.assertEqual(tokens[5].column, 6)

        # Line 4: INTO (4, 1), result (4, 6)
        self.assertEqual(tokens[6].name, "INTO")
        self.assertEqual(tokens[6].line, 4)
        self.assertEqual(tokens[6].column, 1)

        self.assertEqual(tokens[7].name, IDENT)
        self.assertEqual(tokens[7].lexeme, "result")
        self.assertEqual(tokens[7].line, 4)
        self.assertEqual(tokens[7].column, 6)

    def test_empty_and_whitespace_input(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   \t\n\r\n   "), [])

    def test_custom_keywords(self):
        custom_kw = {"CUSTOM_CMD", "SPECIAL"}
        tokens = tokenize("CUSTOM_CMD normalIdent", keywords=custom_kw)
        self.assertEqual(tokens[0].name, "CUSTOM_CMD")
        self.assertEqual(tokens[1].name, IDENT)


if __name__ == "__main__":
    unittest.main()
