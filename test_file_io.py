import os
import tempfile
import unittest

import file_io


class TestFileIO(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_source_rejects_non_io(self):
        path = os.path.join(self.dir, "a.txt")
        open(path, "w").close()
        with self.assertRaises(file_io.FileIOError):
            file_io.load_source(path)

    def test_load_source_missing_file(self):
        with self.assertRaises(file_io.FileIOError):
            file_io.load_source(os.path.join(self.dir, "missing.iol"))

    def test_save_and_load_source_roundtrip(self):
        path = file_io.save_source(os.path.join(self.dir, "prog"), "DEFINE x\r\n")
        self.assertTrue(path.endswith(".iol"))
        self.assertEqual(file_io.load_source(path), "DEFINE x\r\n")

    def test_default_source_path_is_unique(self):
        first = file_io.default_source_path(self.dir)
        self.assertEqual(first, os.path.join(self.dir, "untitled.iol"))
        open(first, "w").close()
        self.assertEqual(
            file_io.default_source_path(self.dir),
            os.path.join(self.dir, "untitled1.iol"),
        )

    def test_token_path_for(self):
        self.assertEqual(file_io.token_path_for("/a/b/prog.iol"), "/a/b/prog.tkn")

    def test_save_tokens_appends_extension(self):
        path = file_io.save_tokens(os.path.join(self.dir, "out"), "IDENT x\n")
        self.assertTrue(path.endswith(".tkn"))
        self.assertEqual(file_io.load_tokens(path), "IDENT x\n")


if __name__ == "__main__":
    unittest.main()
