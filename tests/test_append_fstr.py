import shutil
import unittest
from basern.hl import append_to_file
from pathlib import Path



# python -m unittest tests/test_append_fstr.py
class TestAppendToFile(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        # Mock Path.home() so tests don't touch the real filesystem
        self.home_patch = patch(
            "pathlib.Path.home",
            return_value=Path(self.temp_dir.name)
        )
        self.home_patch.start()

    def tearDown(self):
        self.home_patch.stop()
        self.temp_dir.cleanup()
        #print(f"cleaned up [{self.temp_dir}]")    

    def test_creates_file(self):
        append_to_file("test.txt", "hello")

        file_path = (
            Path(self.temp_dir.name)
            / "tmp"
            / "default"
            / "test.txt"
        )

        self.assertTrue(file_path.exists())

    def test_appends_content(self):
        append_to_file("test.txt", "first")
        append_to_file("test.txt", "second")

        file_path = (
            Path(self.temp_dir.name)
            / "tmp"
            / "default"
            / "test.txt"
        )

        self.assertEqual(
            file_path.read_text(encoding="utf-8"),
            "first\nsecond\n"
        )

    def test_append_oneline(self):
        append_to_file("test.txt", "sample")

        file_path = (
            Path(self.temp_dir.name)
            / "tmp"
            / "default"
            / "test.txt"
        )

        self.assertEqual(
            file_path.read_text(encoding="utf-8"),
            "sample\n"
        )

    def test_creates_subfolder(self):
        append_to_file(
            "test.txt",
            "hello",
            subfolder="images"
        )

        file_path = (
            Path(self.temp_dir.name)
            / "tmp"
            / "images"
            / "test.txt"
        )

        self.assertTrue(file_path.exists())

    def test_strips_trailing_newlines(self):
        append_to_file("test.txt", "hello\n\n")

        file_path = (
            Path(self.temp_dir.name)
            / "tmp"
            / "default"
            / "test.txt"
        )

        self.assertEqual(
            file_path.read_text(encoding="utf-8"),
            "hello\n"
        )

    def test_strips_trailing_spaces(self):
        append_to_file("test.txt", "hello   ")

        file_path = (
            Path(self.temp_dir.name)
            / "tmp"
            / "default"
            / "test.txt"
        )

        read_back = file_path.read_text(encoding="utf-8")
#        print(f"Got back = [{read_back}]")
        self.assertEqual(
            read_back,
            "hello\n"
        )

    def test_unicode_content(self):
        append_to_file("test.txt", "你好 🌍 ")

        file_path = (
            Path(self.temp_dir.name)
            / "tmp"
            / "default"
            / "test.txt"
        )

        assert file_path.read_text(encoding="utf-8") == "你好 🌍\n"

if __name__ == '__main__':
    unittest.main()
