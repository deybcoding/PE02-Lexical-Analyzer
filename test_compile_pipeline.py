"""
Tests that the diagnostics and variable table modules are wired into the compile flow.
"""

import unittest

import error_diagnostics
import variable_table
from controller import CompilerController


class TestCompilePipeline(unittest.TestCase):
    def test_controller_loads_diagnostics_modules(self):
        c = CompilerController()
        self.assertIs(c.collect_errors, error_diagnostics.collect_errors)
        self.assertIs(c.format_error, error_diagnostics.format_error)
        self.assertIs(c.build_variable_table, variable_table.build_variable_table)

    def test_compile_populates_errors_and_variables(self):
        result = CompilerController().compile_code(
            "INT num IS 0\nSTR msg\nINTO num IS 5 @\nPRINT $$ msg"
        )
        self.assertEqual(result.variables, [("num", "INT"), ("msg", "STR")])
        self.assertEqual(len(result.errors), 2)
        self.assertIn("'@'", result.errors[0])
        self.assertIn("line 3", result.errors[0])
        self.assertIn("'$$'", result.errors[1])
        self.assertIn("line 4", result.errors[1])


if __name__ == "__main__":
    unittest.main()
