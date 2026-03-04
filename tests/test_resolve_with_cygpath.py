import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from basern.rnutils import resolve_with_cygpath


# ── Platform guards ──────────────────────────────────────────────────────────

is_windows = sys.platform == "win32"
is_cygwin  = sys.platform == "cygwin"

requires_windows = unittest.skipUnless(
    is_windows or is_cygwin,
    "Windows/Cygwin-specific test"
)

# claude: lengthy incognito, 
# Given that I have Python and cygwin bash:
# how do I resolve symlinks ln -s xx yy in code if I want to lookup a file yy/file ?
# show me code and explainations. Feel free to suggest different libraries
# >> file shows symbolic link to xxx
# >> xxd fails is a directory
# >> cmd /c dir shows it is a JUNCTION
# >>> fsutil shows this
# >>> ===
# >>> Reparse Tag Value : 0xa000001d
# >>> Tag value: Microsoft
# >>> Tag value: Name Surrogate
# >>> Reparse Data Length: 0x1a
# >>> Reparse Data:
# >>> cygpath resolves correctly
# 
# Followed by type safe and such

class TestResolveWithCygpath(unittest.TestCase):

    # ── Cross-platform ───────────────────────────────────────────────────────

    def test_regular_file_returned_as_is(self):
        """os.stat() succeeds → path returned unchanged, cygpath not called."""
        p = Path("dir1/file.txt")
        with patch("os.stat"), \
             patch("subprocess.check_output") as mock_cyg:
            result = resolve_with_cygpath(p)
            mock_cyg.assert_not_called()
            self.assertEqual(result, p)

    def test_accepts_string_input(self):
        """str input is accepted and returned as Path."""
        with patch("os.stat"):
            result = resolve_with_cygpath("dir1/file.txt")
            self.assertIsInstance(result, Path)

    def test_accepts_path_input(self):
        """Path input is accepted and returned as Path."""
        with patch("os.stat"):
            result = resolve_with_cygpath(Path("dir1/file.txt"))
            self.assertIsInstance(result, Path)

    def test_cygpath_failure_raises(self):
        """CalledProcessError from cygpath always propagates."""
        reparse_error = OSError()
        reparse_error.winerror = 1920

        with patch("os.stat", side_effect=reparse_error), \
             patch("subprocess.check_output",
                   side_effect=subprocess.CalledProcessError(1, "cygpath")):
            with self.assertRaises(subprocess.CalledProcessError):
                resolve_with_cygpath("yy/file.txt")

    # ── Windows/Cygwin only ──────────────────────────────────────────────────

    @requires_windows
    def test_cygwin_symlink_resolved_via_cygpath(self):
        """winerror 1920 triggers cygpath, returns resolved Path."""
        reparse_error = OSError()
        reparse_error.winerror = 1920

        with patch("os.stat", side_effect=[reparse_error, None]), \
             patch("subprocess.check_output",
                   return_value="C:\\real\\xx\\file.txt") as mock_cyg:
            result = resolve_with_cygpath("dir1/yy/file.txt")
            mock_cyg.assert_called_once_with(
                ["cygpath", "-aw", "dir1/yy/file.txt"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            self.assertEqual(result, Path("C:\\real\\xx\\file.txt"))

    @requires_windows
    def test_cygpath_output_is_stripped(self):
        """Trailing newline from cygpath stdout is stripped."""
        reparse_error = OSError()
        reparse_error.winerror = 1920

        with patch("os.stat", side_effect=[reparse_error, None]), \
             patch("subprocess.check_output",
                   return_value="C:\\real\\xx\\file.txt\n"):
            result = resolve_with_cygpath("yy/file.txt")
            self.assertEqual(result, Path("C:\\real\\xx\\file.txt"))

    @requires_windows
    def test_resolved_path_is_validated(self):
        """After cygpath resolves, os.stat is called again to validate."""
        reparse_error = OSError()
        reparse_error.winerror = 1920
        stat_calls = []

        def stat_side_effect(p):
            stat_calls.append(p)
            if len(stat_calls) == 1:
                raise reparse_error

        with patch("os.stat", side_effect=stat_side_effect), \
             patch("subprocess.check_output",
                   return_value="C:\\real\\xx\\file.txt"):
            resolve_with_cygpath("yy/file.txt")
            self.assertEqual(len(stat_calls), 2)

    @requires_windows
    def test_file_not_found_is_reraised(self):
        """winerror 2 (file not found) is re-raised, cygpath not called."""
        not_found = OSError()
        not_found.winerror = 2

        with patch("os.stat", side_effect=not_found), \
             patch("subprocess.check_output") as mock_cyg:
            with self.assertRaises(OSError):
                resolve_with_cygpath("nonexistent/file.txt")
            mock_cyg.assert_not_called()

    @requires_windows
    def test_permission_error_is_reraised(self):
        """winerror 5 (permission denied) is re-raised, cygpath not called."""
        perm_error = OSError()
        perm_error.winerror = 5

        with patch("os.stat", side_effect=perm_error), \
             patch("subprocess.check_output") as mock_cyg:
            with self.assertRaises(OSError):
                resolve_with_cygpath("protected/file.txt")
            mock_cyg.assert_not_called()

    @requires_windows
    def test_resolved_path_not_found_raises(self):
        """If cygpath resolves but the target doesn't exist, OSError is raised."""
        reparse_error = OSError()
        reparse_error.winerror = 1920
        not_found = OSError()
        not_found.winerror = 2

        with patch("os.stat", side_effect=[reparse_error, not_found]), \
             patch("subprocess.check_output",
                   return_value="C:\\ghost\\file.txt"):
            with self.assertRaises(OSError):
                resolve_with_cygpath("yy/file.txt")

    @requires_windows
    def test_accepts_string_input(self):
        """str input is accepted and returned as Path."""
        with patch("os.stat"):
            result = resolve_with_cygpath("dir1/file.txt")
            self.assertIsInstance(result, Path)


if __name__ == "__main__":
    unittest.main(verbosity=2)