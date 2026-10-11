# Tests for the tokenized-code display and .tkn formatter.

import unittest

from formatter import format_tokens
from lexer import tokenize


class TestFormatter(unittest.TestCase):
    def test_formats_token_names_by_source_line(self):
        tokens = tokenize("IOL\n  INT count IS 7\n  PRINT count\nLOI")
        self.assertEqual(
            format_tokens(tokens),
            "IOL\nINT IDENT IS INT_LIT\nPRINT IDENT\nLOI\n",
        )

    def test_preserves_empty_lines_between_tokens(self):
        self.assertEqual(
            format_tokens(tokenize("INT x\n\nPRINT x")),
            "INT IDENT\n\nPRINT IDENT\n",
        )

    def test_empty_token_stream_is_empty_text(self):
        self.assertEqual(format_tokens([]), "")

    def test_lexical_errors_are_formatted_as_token_names(self):
        self.assertEqual(format_tokens(tokenize("x @")), "IDENT ERR_LEX\n")


if __name__ == "__main__":
    unittest.main()