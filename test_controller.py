import os
import tempfile
import unittest

import file_io
from controller import (
    CompilerController,
    CompileResult,
    compile_source,
)
from lexer import ERR_LEX


class TestController(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.src = os.path.join(self.dir, "sample.io")
        with open(self.src, "w") as f:
            f.write("DEFINE x AS INT\nx IS 5 @\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_open_file_loads_source(self):
        c = CompilerController()
        self.assertEqual(c.open_file(self.src), "DEFINE x AS INT\nx IS 5 @\n")
        self.assertEqual(c.source_path, self.src)

    def test_new_file_clears_state(self):
        c = CompilerController()
        c.compile_code(c.open_file(self.src))
        self.assertEqual(c.new_file(), "")
        self.assertIsNone(c.source_path)
        self.assertIsNone(c.tkn_path)
        self.assertIsNone(c.show_tokenized_code())

    def test_compile_saves_tkn_next_to_source(self):
        c = CompilerController()
        result = c.compile_code(c.open_file(self.src))
        expected = os.path.join(self.dir, "sample.tkn")
        self.assertEqual(result.tkn_path, expected)
        self.assertTrue(os.path.exists(expected))
        self.assertEqual(c.show_tokenized_code(), result.tokenized_code)

    def test_compile_new_file_uses_given_tkn_path(self):
        c = CompilerController()
        c.new_file()
        target = os.path.join(self.dir, "custom.tkn")
        result = c.compile_code("x IS 1", target)
        self.assertEqual(result.tkn_path, target)
        self.assertTrue(os.path.exists(target))

    def test_compile_without_path_does_not_save(self):
        c = CompilerController()
        result = c.compile_code("x IS 1")
        self.assertIsNone(result.tkn_path)
        self.assertEqual(c.show_tokenized_code(), result.tokenized_code)

    def test_compile_passes_tokens_to_modules(self):
        seen = {}

        def fmt(tokens):
            seen["fmt"] = tokens
            return "FORMATTED"

        def errs(tokens):
            seen["errs"] = tokens
            return [t for t in tokens if t.name == ERR_LEX]

        def vars_(tokens):
            seen["vars"] = tokens
            return [("x", "INT")]

        c = CompilerController(
            format_tokens=fmt,
            collect_errors=errs,
            format_error=lambda t: f"bad {t.lexeme} line {t.line}",
            build_variable_table=vars_,
        )
        result = c.compile_code(c.open_file(self.src))

        self.assertIs(seen["fmt"], result.tokens)
        self.assertIs(seen["errs"], result.tokens)
        self.assertIs(seen["vars"], result.tokens)
        self.assertEqual(result.tokenized_code, "FORMATTED")
        self.assertEqual(result.errors, ["bad @ line 2"])
        self.assertEqual(result.variables, [("x", "INT")])
        self.assertEqual(file_io.load_tokens(result.tkn_path), "FORMATTED")

    def test_default_error_messages(self):
        c = CompilerController()
        result = c.compile_code("x IS 5 @\n$$ y")
        self.assertEqual(len(result.errors), 2)
        self.assertIn("'@'", result.errors[0])
        self.assertIn("line 1", result.errors[0])
        self.assertIn("'$$'", result.errors[1])
        self.assertIn("line 2", result.errors[1])

    def test_compile_source_helper(self):
        result = compile_source("DEFINE x\n@")
        self.assertIsInstance(result, CompileResult)
        self.assertEqual(len(result.tokens), 3)
        self.assertTrue(result.has_errors)
        self.assertIsNone(result.tkn_path)

    def test_save_file_requires_path(self):
        c = CompilerController()
        with self.assertRaises(file_io.FileIOError):
            c.save_file("x")
        saved = c.save_file("x", os.path.join(self.dir, "new"))
        self.assertTrue(saved.endswith("new.io"))
        self.assertEqual(c.source_path, saved)


if __name__ == "__main__":
    unittest.main()
