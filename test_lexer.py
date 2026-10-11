"""
Unit tests for the Lexer Core (Member 1 Deliverable).
"""

import unittest
from lexer import (
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
        code = "INT INTO IS"
        tokens = tokenize(code)
        self.assertEqual(len(tokens), 3)

        # Keyword token name must match the keyword itself
        self.assertEqual(tokens[0].name, "INT")
        self.assertEqual(tokens[0].lexeme, "INT")

        self.assertEqual(tokens[1].name, "INTO")
        self.assertEqual(tokens[1].lexeme, "INTO")

        self.assertEqual(tokens[2].name, "IS")
        self.assertEqual(tokens[2].lexeme, "IS")

    def test_identifiers(self):
        code = "myVar count temp x1"
        tokens = tokenize(code)
        self.assertEqual(len(tokens), 4)

        for tok, lex in zip(tokens, ["myVar", "count", "temp", "x1"]):
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
        code = "INT num\nIS 42\n  ERR @\nINTO result"
        tokens = tokenize(code)

        # Line 1: INT (1, 1), num (1, 5)
        self.assertEqual(tokens[0].name, "INT")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)

        self.assertEqual(tokens[1].name, IDENT)
        self.assertEqual(tokens[1].lexeme, "num")
        self.assertEqual(tokens[1].line, 1)
        self.assertEqual(tokens[1].column, 5)

        # Line 2: IS (2, 1), 42 (2, 4)
        self.assertEqual(tokens[2].name, "IS")
        self.assertEqual(tokens[2].line, 2)
        self.assertEqual(tokens[2].column, 1)

        self.assertEqual(tokens[3].name, INT_LIT)
        self.assertEqual(tokens[3].lexeme, "42")
        self.assertEqual(tokens[3].line, 2)
        self.assertEqual(tokens[3].column, 4)

        # Line 3: ERR (3, 3), @ (3, 7)
        self.assertEqual(tokens[4].name, IDENT)
        self.assertEqual(tokens[4].lexeme, "ERR")
        self.assertEqual(tokens[4].line, 3)
        self.assertEqual(tokens[4].column, 3)

        self.assertEqual(tokens[5].name, ERR_LEX)
        self.assertEqual(tokens[5].lexeme, "@")
        self.assertEqual(tokens[5].line, 3)
        self.assertEqual(tokens[5].column, 7)

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
        custom_kw = {"CUSTOM", "SPECIAL"}
        tokens = tokenize("CUSTOM normalIdent", keywords=custom_kw)
        self.assertEqual(tokens[0].name, "CUSTOM")
        self.assertEqual(tokens[1].name, IDENT)

    def test_iol_keywords(self):
        words = "IOL LOI INT STR IS INTO BEG PRINT NEWLN ADD SUB MULT DIV MOD"
        for tok in tokenize(words):
            self.assertIn(tok.lexeme, KEYWORDS)
            self.assertEqual(tok.name, tok.lexeme)

    def test_keywords_are_case_sensitive(self):
        self.assertEqual([t.name for t in tokenize("print Print")], [IDENT, IDENT])

    def test_sample_iol_program(self):
        code = "IOL\n  INT num IS 0\n  BEG num\n  INTO num IS MULT num 2\n  PRINT num\nLOI"
        self.assertEqual(
            [t.name for t in tokenize(code)],
            [
                "IOL",
                "INT", IDENT, "IS", INT_LIT,
                "BEG", IDENT,
                "INTO", IDENT, "IS", "MULT", IDENT, INT_LIT,
                "PRINT", IDENT,
                "LOI",
            ],
        )

    def test_define_is_not_an_iol_keyword(self):
        self.assertEqual(tokenize("DEFINE")[0].name, IDENT)

    def test_underscore_is_not_allowed_in_identifiers(self):
        for word in ["_temp", "x_1", "my_var"]:
            tokens = tokenize(word)
            self.assertEqual(len(tokens), 1)
            self.assertEqual(tokens[0].name, ERR_LEX)
            self.assertEqual(tokens[0].lexeme, word)

    def test_unknown_word_is_one_error_lexeme(self):
        tokens = tokenize("INT x@ IS 5 abc$def 12#")
        self.assertEqual(
            [(t.name, t.lexeme) for t in tokens],
            [
                ("INT", "INT"),
                (ERR_LEX, "x@"),
                ("IS", "IS"),
                (INT_LIT, "5"),
                (ERR_LEX, "abc$def"),
                (ERR_LEX, "12#"),
            ],
        )
        self.assertEqual(tokens[4].column, 13)

    def test_non_ascii_letters_and_digits_are_errors(self):
        self.assertEqual([t.name for t in tokenize("caf\u00e9 \u00b2")], [ERR_LEX, ERR_LEX])

    def test_spec_sample_program(self):
        code = (
            "IOL\n"
            "\tINT num IS 0 INT res IS 0\n"
            "\tSTR msg1 STR msg2 STR msg3\n"
            "\tBEG msg1 BEG msg2\n"
            "\tBEG msg3\n"
            "\tNEWLN PRINT msg1\n"
            "\tNEWLN\n"
            "\tINTO res IS MULT num num\n"
            "\tPRINT msg2\n"
            "\tPRINT MULT num 2\n"
            "\tNEWLN\n"
            "\tPRINT msg3\n"
            "\tPRINT res\n"
            "LOI\n"
        )
        tokens = tokenize(code)
        self.assertNotIn(ERR_LEX, [t.name for t in tokens])
        self.assertEqual(tokens[0].name, "IOL")
        self.assertEqual(tokens[-1].name, "LOI")
        self.assertEqual(tokens[-1].line, 14)


if __name__ == "__main__":
    unittest.main()
