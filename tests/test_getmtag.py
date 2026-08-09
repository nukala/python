from basern.getmtag import is_win64, is_windows, is_win32

"""Unit tests for is_win64().

These tests are fully parameterized and use mocking so they do not depend on
the actual host architecture.  They cover the two possible outcomes of the
startswith("64") check plus a few edge-case strings.
"""
#grok
from unittest.mock import patch

import pytest

@pytest.mark.parametrize(
    "arch_string, expected",
    [
        # ------------------------------------------------------------------
        # Positive cases – architecture string begins with "64"
        # ------------------------------------------------------------------
        pytest.param("64bit", True, id="64bit"),
        pytest.param("64", True, id="exactly-64"),
        pytest.param("64bit-WindowsPE", True, id="64bit-with-suffix"),
        pytest.param("64anything", True, id="64-prefix-any-suffix"),

        # ------------------------------------------------------------------
        # Negative cases – architecture string does NOT begin with "64"
        # ------------------------------------------------------------------
        pytest.param("32bit", False, id="32bit"),
        pytest.param("32", False, id="exactly-32"),
        pytest.param("x86_64", False, id="x86_64-does-not-start-with-64"),
        pytest.param("arm64", False, id="arm64-does-not-start-with-64"),
        pytest.param("", False, id="empty-string"),
        pytest.param("bit64", False, id="64-not-at-start"),
        pytest.param(" 64bit", False, id="leading-whitespace"),
    ],
)
def test_is_win64(arch_string: str, expected: bool) -> None:
    """Verify that is_win64() returns the correct boolean for a given
    architecture string returned by platform.architecture().

    Parameters
    ----------
    arch_string:
        The first element of the tuple that platform.architecture() is
        mocked to return.
    expected:
        The boolean value that is_win64() is expected to produce.
    """
    with patch("platform.architecture", return_value=(arch_string, "")):
        assert is_win64() is expected


"""Unit tests for is_windows() and is_win32().

These tests are fully parameterized and mock sys.platform so they do not
depend on the host operating system.
"""
# ---------------------------------------------------------------------------
# is_windows()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "platform_value, expected",
    [
        # Positive cases – values that must return True
        pytest.param("win32", True, id="win32"),
        pytest.param("cygwin", True, id="cygwin"),
        pytest.param("Windows", True, id="Windows"),

        # Negative cases – values that must return False
        pytest.param("linux", False, id="linux"),
        pytest.param("linux2", False, id="linux2"),
        pytest.param("darwin", False, id="darwin"),
        pytest.param("darwin19", False, id="darwin19"),
        pytest.param("aix", False, id="aix"),
        pytest.param("freebsd", False, id="freebsd"),
        pytest.param("", False, id="empty-string"),
        pytest.param("win64", False, id="win64-not-in-tuple"),
        pytest.param("Win32", False, id="wrong-case"),
        pytest.param("CYGWIN", False, id="cygwin-wrong-case"),
    ],
)
def test_is_windows(platform_value: str, expected: bool) -> None:
    """Verify is_windows() returns the correct boolean for a given sys.platform.

    Parameters
    ----------
    platform_value:
        The value that sys.platform is mocked to return.
    expected:
        The boolean value that is_windows() is expected to produce.
    """
    with patch("sys.platform", platform_value):
        assert is_windows() is expected


# ---------------------------------------------------------------------------
# is_win32()  (currently just an alias of is_windows())
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "platform_value, expected",
    [
        # Positive cases
        pytest.param("win32", True, id="win32"),
        pytest.param("cygwin", True, id="cygwin"),
        pytest.param("Windows", True, id="Windows"),

        # Negative cases
        pytest.param("linux", False, id="linux"),
        pytest.param("darwin", False, id="darwin"),
        pytest.param("", False, id="empty-string"),
        pytest.param("win64", False, id="win64-not-in-tuple"),
    ],
)
def test_is_win32(platform_value: str, expected: bool) -> None:
    """Verify is_win32() returns the same result as is_windows() for a given
    sys.platform value.

    Parameters
    ----------
    platform_value:
        The value that sys.platform is mocked to return.
    expected:
        The boolean value that is_win32() is expected to produce.
    """
    with patch("sys.platform", platform_value):
        assert is_win32() is expected


def test_is_win32_calls_is_windows() -> None:
    """is_win32() should simply delegate to is_windows()."""
    with patch("basern.getmtag.is_windows", return_value=True) as mock_is_windows:
        result = is_win32()
        mock_is_windows.assert_called_once_with()
        assert result is True