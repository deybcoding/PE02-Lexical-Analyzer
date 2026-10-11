"""
Unit tests for the Variable / Symbol Table (Member 3 Deliverable).
"""

import unittest

from lexer import tokenize
from variable_table import build_variable_table


class TestVariableTable(unittest.TestCase):
    def test_declaration_without_value(self):
        tokens = tokenize("STR msg1 INT count")
        self.assertEqual(
            build_variable_table(tokens), [("msg1", "STR"), ("count", "INT")]
        )

    def test_declaration_with_value(self):
        tokens = tokenize("INT num IS 0 INT res IS 0")
        self.assertEqual(build_variable_table(tokens), [("num", "INT"), ("res", "INT")])

    def test_sample_program(self):
        code = (
            "IOL\n"
            "    INT num IS 0 INT res IS 0\n"
            "    STR msg1 STR msg2 STR msg3\n"
            "    BEG msg1 BEG msg2\n"
            "    BEG msg3\n"
            "    NEWLN PRINT msg1\n"
            "    INTO res IS MULT num num\n"
            "    PRINT res\n"
            "LOI"
        )
        self.assertEqual(
            build_variable_table(tokenize(code)),
            [
                ("num", "INT"),
                ("res", "INT"),
                ("msg1", "STR"),
                ("msg2", "STR"),
                ("msg3", "STR"),
            ],
        )

    def test_duplicates_keep_first_declaration(self):
        tokens = tokenize("INT x STR x")
        self.assertEqual(build_variable_table(tokens), [("x", "INT")])

    def test_ignores_non_declarations(self):
        tokens = tokenize("x IS 5 BEG y PRINT z INTO w IS 1 INT STR INT 42 INT IS")
        self.assertEqual(build_variable_table(tokens), [])

    def test_type_keyword_at_end_of_input(self):
        self.assertEqual(build_variable_table(tokenize("INT")), [])

    def test_declarations_survive_lexical_errors(self):
        tokens = tokenize("INT x IS 5 @\nSTR y $$")
        self.assertEqual(build_variable_table(tokens), [("x", "INT"), ("y", "STR")])

    def test_empty_input(self):
        self.assertEqual(build_variable_table([]), [])


if __name__ == "__main__":
    unittest.main()
