import tempfile
from unittest.mock import patch
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from basern.hl import HideLock

# Tests for cat_to_sysout
class TestCatToSysout(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name) / "test.txt"


    def tearDown(self):
        self.temp_dir.cleanup()

    def test_prints_contents(self):
        f = Path(self.temp_dir.name) / "test.txt"
        f.write_text("hello")

    def test_prints_file_contents(self):
        with open(self.temp_path, "w") as f:
            f.write("hello world")
            filename = f.name

        captured = io.StringIO()

        with redirect_stdout(captured):
            HideLock.cat_to_sysout(filename)

        #print(f"filename = {filename}")
        self.assertEqual(captured.getvalue(), "hello world")

    def test_accepts_path_object(self):
        with open(self.temp_path, "w") as f:
            f.write("abc")
            filename = Path(f.name)

        captured = io.StringIO()

        with redirect_stdout(captured):
            HideLock.cat_to_sysout(filename)

        self.assertEqual(captured.getvalue(), "abc")

    def test_empty_file(self):
        with open(self.temp_path, "w") as f:
            filename = f.name

        captured = io.StringIO()

        with redirect_stdout(captured):
            HideLock.cat_to_sysout(filename)

        self.assertEqual(captured.getvalue(), "")

    def test_multiline_file(self):
        content = "line1\nline2\nline3\n"

        with open(self.temp_path, "w") as f:
            f.write(content)
            filename = f.name

        captured = io.StringIO()

        with redirect_stdout(captured):
            HideLock.cat_to_sysout(filename)

        self.assertEqual(captured.getvalue(), content)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            HideLock.cat_to_sysout("does_not_exist.txt")

    @patch("shutil.copyfileobj")
    def test_uses_copyfileobj(self, mock_copy):
        with open(self.temp_path, "w") as f:
            f.write("hello")
            filename = f.name

        HideLock.cat_to_sysout(filename)

        mock_copy.assert_called_once()

if __name__ == "__main__":
    unittest.main()
