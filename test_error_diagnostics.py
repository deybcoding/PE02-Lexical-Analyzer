"""
Unit tests for Error Diagnostics (Deliverable).
"""

import unittest

import error_diagnostics as ed
from lexer import ERR_LEX, tokenize


class TestErrorDiagnostics(unittest.TestCase):
    def test_collect_errors_only_returns_err_lex(self):
        tokens = tokenize("DEFINE x\nx IS 5 @\n123abc")
        errors = ed.collect_errors(tokens)
        self.assertEqual([t.lexeme for t in errors], ["@", "123abc"])
        self.assertTrue(all(t.name == ERR_LEX for t in errors))

    def test_collect_errors_empty_when_clean(self):
        self.assertEqual(ed.collect_errors(tokenize("DEFINE x AS INT")), [])
        self.assertEqual(ed.collect_errors([]), [])

    def test_format_error_has_unknown_word_and_line(self):
        token = tokenize("\n\nx IS 5 @")[-1]
        message = ed.format_error(token)
        self.assertIn("'@'", message)
        self.assertIn("line 3", message)

    def test_format_errors_in_source_order(self):
        messages = ed.format_errors(tokenize("x IS 5 @\n$$ y\n9z"))
        self.assertEqual(len(messages), 3)
        self.assertIn("'@'", messages[0])
        self.assertIn("line 1", messages[0])
        self.assertIn("'$$'", messages[1])
        self.assertIn("line 2", messages[1])
        self.assertIn("'9z'", messages[2])
        self.assertIn("line 3", messages[2])

    def test_error_summary(self):
        self.assertEqual(ed.error_summary(tokenize("DEFINE x")), ed.NO_ERRORS_MESSAGE)
        self.assertEqual(ed.error_summary(tokenize("@ #")), "2 lexical error(s) found.")


if __name__ == "__main__":
    unittest.main()
