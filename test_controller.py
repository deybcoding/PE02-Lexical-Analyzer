import os
import tempfile
import unittest

import file_io
from controller import (
    CompilerController,
    CompileResult,
    compile_source,
    default_format_tokens,
)
from lexer import ERR_LEX, tokenize


class TestController(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.src = os.path.join(self.dir, "sample.iol")
        with open(self.src, "w") as f:
            f.write("IOL\nINT x IS 5 @\nLOI\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_open_file_loads_source(self):
        c = CompilerController()
        self.assertEqual(c.open_file(self.src), "IOL\nINT x IS 5 @\nLOI\n")
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

    def test_default_format_tokens_keeps_line_structure(self):
        code = "IOL\n  INT x IS 5\n\n  PRINT x @\nLOI"
        self.assertEqual(
            default_format_tokens(tokenize(code)),
            "IOL\nINT IDENT IS INT_LIT\n\nPRINT IDENT ERR_LEX\nLOI\n",
        )
        self.assertEqual(default_format_tokens([]), "")

    def test_compile_result_has_summary(self):
        c = CompilerController()
        self.assertEqual(c.compile_code("INT x").summary, "No lexical errors found.")
        self.assertEqual(
            c.compile_code("INT x @ $").summary, "2 lexical error(s) found."
        )

    def test_compile_source_helper(self):
        result = compile_source("DEFINE x\n@")
        self.assertIsInstance(result, CompileResult)
        self.assertEqual(len(result.tokens), 3)
        self.assertTrue(result.has_errors)
        self.assertIsNone(result.tkn_path)

    def test_save_without_work_dir_requires_save_as(self):
        c = CompilerController()
        with self.assertRaises(file_io.FileIOError):
            c.save_file("x")
        saved = c.save_file_as("x", os.path.join(self.dir, "new"))
        self.assertTrue(saved.endswith("new.iol"))
        self.assertEqual(c.source_path, saved)

    def test_new_file_uses_default_filename(self):
        c = CompilerController(work_dir=self.dir)
        self.assertEqual(c.file_name, "untitled.iol")
        saved = c.save_file("IOL LOI")
        self.assertEqual(saved, os.path.join(self.dir, "untitled.iol"))
        self.assertEqual(file_io.load_source(saved), "IOL LOI")
        c.new_file()
        self.assertEqual(c.file_name, "untitled1.iol")

    def test_save_opened_file_writes_same_file(self):
        c = CompilerController(work_dir=self.dir)
        c.open_file(self.src)
        self.assertEqual(c.save_file("IOL LOI"), self.src)
        self.assertEqual(file_io.load_source(self.src), "IOL LOI")

    def test_save_as_switches_to_new_file(self):
        c = CompilerController(work_dir=self.dir)
        c.open_file(self.src)
        other = c.save_file_as("IOL LOI", os.path.join(self.dir, "copy.iol"))
        self.assertEqual(c.file_name, "copy.iol")
        self.assertEqual(c.default_tkn_path(), os.path.join(self.dir, "copy.tkn"))
        self.assertEqual(file_io.load_source(other), "IOL LOI")
        self.assertNotEqual(file_io.load_source(self.src), "IOL LOI")

    def test_compile_new_file_saves_default_tkn(self):
        c = CompilerController(work_dir=self.dir)
        result = c.compile_code("IOL LOI")
        self.assertEqual(result.tkn_path, os.path.join(self.dir, "untitled.tkn"))
        self.assertEqual(file_io.load_tokens(result.tkn_path), "IOL LOI\n")


if __name__ == "__main__":
    unittest.main()
