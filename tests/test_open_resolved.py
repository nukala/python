import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch, mock_open
from basern.rnutils import open_resolved

class TestOpenResolved(unittest.TestCase):

    # ── Cross-platform ───────────────────────────────────────────────────────

    def test_binary_read_default_mode(self):
        """Default mode is 'rb', returns bytes."""
        mock_file = mock_open(read_data=b"hello bytes")
        with patch("builtins.open", mock_file), \
             patch("os.stat"):
            with open_resolved("some/file.txt") as f:
                data = f.read()
            self.assertEqual(data, b"hello bytes")
            mock_file.assert_called_once_with(
                Path("some/file.txt"), mode="rb", encoding=None
            )

    def test_text_read_mode(self):
        """mode='r' with encoding returns text."""
        mock_file = mock_open(read_data="hello text")
        with patch("builtins.open", mock_file), \
             patch("os.stat"):
            with open_resolved("some/file.txt", mode="r", encoding="utf-8") as f:
                data = f.read()
            self.assertEqual(data, "hello text")
            mock_file.assert_called_once_with(
                Path("some/file.txt"), mode="r", encoding="utf-8"
            )

    def test_write_mode(self):
        """mode='w' opens for writing."""
        mock_file = mock_open()
        with patch("builtins.open", mock_file), \
             patch("os.stat"):
            with open_resolved("some/file.txt", mode="w", encoding="utf-8") as f:
                f.write("data")
            mock_file.assert_called_once_with(
                Path("some/file.txt"), mode="w", encoding="utf-8"
            )

    def test_returns_context_manager(self):
        """open_resolved result is usable as a context manager."""
        mock_file = mock_open(read_data=b"data")
        with patch("builtins.open", mock_file), \
             patch("os.stat"):
            cm = open_resolved("some/file.txt")
            self.assertTrue(hasattr(cm, "__enter__"))
            self.assertTrue(hasattr(cm, "__exit__"))

    def test_file_not_found_raises(self):
        """OSError propagates when file does not exist."""
        with patch("builtins.open", side_effect=FileNotFoundError("not found")), \
             patch("os.stat"):
            with self.assertRaises(FileNotFoundError):
                open_resolved("ghost/file.txt")

    # ── Platform branching ───────────────────────────────────────────────────

    def test_non_windows_skips_resolve(self):
        """On non-Windows platforms, resolve_with_cygpath is never called."""
        mock_file = mock_open(read_data=b"data")
        with patch("sys.platform", "darwin"), \
             patch("builtins.open", mock_file), \
             patch("basern.rnutils.adjust_winpath") as mock_adjust:
            with open_resolved("some/file.txt"):
                pass
            mock_adjust.assert_not_called()

    def test_win32_calls_resolve(self):
        """On win32, resolve_with_cygpath is called before open."""
        mock_file = mock_open(read_data=b"data")
        resolved  = Path("C:\\real\\file.txt")
        with patch("sys.platform", "win32"), \
             patch("builtins.open", mock_file), \
             patch("resolve_with_cygpath", return_value=resolved) as mock_resolve:
            with open_resolved("some/file.txt"):
                pass
            mock_resolve.assert_called_once_with("some/file.txt")
            mock_file.assert_called_once_with(
                resolved, mode="rb", encoding=None
            )

    def test_cygwin_calls_resolve(self):
        """On cygwin, resolve_with_cygpath is called before open."""
        mock_file = mock_open(read_data=b"data")
        resolved  = Path("/cygdrive/c/real/file.txt")
        with patch("sys.platform", "cygwin"), \
             patch("builtins.open", mock_file), \
             patch("resolve_with_cygpath", return_value=resolved) as mock_resolve:
            with open_resolved("some/file.txt"):
                pass
            mock_resolve.assert_called_once_with("some/file.txt")
            mock_file.assert_called_once_with(
                resolved, mode="rb", encoding=None
            )

    def test_linux_skips_resolve(self):
        """On linux, resolve_with_cygpath is never called."""
        mock_file = mock_open(read_data=b"data")
        with patch("sys.platform", "linux"), \
             patch("builtins.open", mock_file), \
             patch("resolve_with_cygpath") as mock_resolve:
            with open_resolved("some/file.txt"):
                pass
            mock_resolve.assert_not_called()

    def test_cygwin_symlink_resolved_before_open(self):
        """Resolved path — not original — is what gets passed to open()."""
        original  = "dir1/yy/file.txt"
        resolved  = Path("C:\\real\\xx\\file.txt")
        mock_file = mock_open(read_data=b"content")

        with patch("sys.platform", "win32"), \
             patch("resolve_with_cygpath", return_value=resolved), \
             patch("builtins.open", mock_file):
            with open_resolved(original, "rb") as f:
                data = f.read()

        self.assertEqual(data, b"content")
        mock_file.assert_called_once_with(resolved, mode="rb", encoding=None)

    def test_cygpath_failure_propagates(self):
        """CalledProcessError from resolve_with_cygpath propagates."""
        with patch("sys.platform", "win32"), \
             patch("basern.rnutils.resolve_with_cygpath",
                   side_effect=subprocess.CalledProcessError(1, "cygpath")):
            with self.assertRaises(subprocess.CalledProcessError):
                open_resolved("dir1/yy/file.txt")


if __name__ == "__main__":
    unittest.main(verbosity=2)