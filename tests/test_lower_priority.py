"""
Tests for proc_utils.lower_priority / ProcUtils.lower_priority

Run with:
    pip install pytest psutil --break-system-packages   # if not already installed
    pytest -v test_proc_utils.py
"""

from unittest.mock import MagicMock, patch

import psutil
import pytest

from basern.proc_utils import ProcUtils

lower_priority = ProcUtils.lower_priority

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_fake_process(nice_sequence):
    """
    Build a MagicMock standing in for a psutil.Process instance whose
    .nice() calls return successive values from `nice_sequence` when
    called with no arguments, and simply record the value when called
    with an argument (acting as a setter).
    """
    fake = MagicMock()
    state = {"seq": list(nice_sequence)}

    def nice(*args):
        if args:
            # setter call - just record, don't advance the getter sequence
            fake.nice.set_calls.append(args[0])
            return None
        return state["seq"].pop(0)

    fake.nice.set_calls = []
    fake.nice.side_effect = nice
    return fake


# ---------------------------------------------------------------------------
# POSIX branch
# ---------------------------------------------------------------------------

class TestPosixBranch:
    def test_sets_nice_to_19(self):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority()
        assert fake_process.nice.set_calls == [19]

    def test_returns_old_and_new_values(self):
        fake_process = make_fake_process([5, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            old, new = lower_priority()
        assert (old, new) == (5, 19)

    def test_does_not_touch_idle_priority_class(self):
        # IDLE_PRIORITY_CLASS is a Windows-only attribute; make sure the
        # POSIX branch never references it even if it doesn't exist.
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process), \
             patch.object(psutil, "IDLE_PRIORITY_CLASS", create=True,
                           new=MagicMock(side_effect=AssertionError(
                               "IDLE_PRIORITY_CLASS should not be touched on POSIX"))):
            lower_priority()  # should not raise


# ---------------------------------------------------------------------------
# Windows branch
# ---------------------------------------------------------------------------

class TestWindowsBranch:
    def test_sets_idle_priority_class(self):
        fake_process = make_fake_process([32, 64])  # arbitrary sentinel ints
        with patch("psutil.WINDOWS", True), \
             patch("psutil.IDLE_PRIORITY_CLASS", 64, create=True), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority()
        assert fake_process.nice.set_calls == [64]

    def test_returns_old_and_new_values(self):
        fake_process = make_fake_process([32, 64])
        with patch("psutil.WINDOWS", True), \
             patch("psutil.IDLE_PRIORITY_CLASS", 64, create=True), \
             patch("psutil.Process", return_value=fake_process):
            old, new = lower_priority()
        assert (old, new) == (32, 64)

    def test_does_not_use_posix_value_19(self):
        fake_process = make_fake_process([32, 64])
        with patch("psutil.WINDOWS", True), \
             patch("psutil.IDLE_PRIORITY_CLASS", 64, create=True), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority()
        assert 19 not in fake_process.nice.set_calls


# ---------------------------------------------------------------------------
# Verbosity behaviour
# ---------------------------------------------------------------------------

class TestVerbosity:
    def test_verbose_prints_old_and_new(self, capsys):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority(verbose=1)
        out = capsys.readouterr().out
        assert "old niceness=[0]" in out
        assert "current=[19]" in out

    def test_verbose_higher_than_one_also_prints(self, capsys):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority(verbose=5)
        assert capsys.readouterr().out != ""

    def test_default_verbose_prints_nothing(self, capsys):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority()
        assert capsys.readouterr().out == ""

    def test_verbose_zero_prints_nothing(self, capsys):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority(verbose=0)
        assert capsys.readouterr().out == ""

    def test_negative_verbose_prints_nothing(self, capsys):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority(verbose=-1)
        assert capsys.readouterr().out == ""


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------

class TestErrorPropagation:
    def test_access_denied_propagates(self):
        fake_process = MagicMock()
        fake_process.nice.side_effect = [0, psutil.AccessDenied()]
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            with pytest.raises(psutil.AccessDenied):
                lower_priority()

    def test_no_such_process_propagates(self):
        fake_process = MagicMock()
        fake_process.nice.side_effect = [0, psutil.NoSuchProcess(pid=1234)]
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            with pytest.raises(psutil.NoSuchProcess):
                lower_priority()


# ---------------------------------------------------------------------------
# Static method / call-signature sanity checks
# ---------------------------------------------------------------------------

class TestCallable:
    def test_is_callable_as_staticmethod(self):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            result = ProcUtils.lower_priority()
        assert result == (0, 19)

    def test_module_level_alias_matches_staticmethod(self):
        assert lower_priority is ProcUtils.lower_priority

    def test_accepts_verbose_as_keyword(self):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority(verbose=0)  # should not raise

    def test_accepts_verbose_as_positional(self):
        fake_process = make_fake_process([0, 19])
        with patch("psutil.WINDOWS", False), \
             patch("psutil.Process", return_value=fake_process):
            lower_priority(0)  # should not raise


# ---------------------------------------------------------------------------
# Real (unmocked) integration test - actually lowers this test process's
# priority. Safe because *lowering* priority never requires elevated
# permissions on any platform.
# ---------------------------------------------------------------------------

class TestRealIntegration:
    def test_real_process_priority_is_lowered(self):
        p = psutil.Process()
        starting = p.nice()

        old, new = lower_priority()

        assert old == starting
        if psutil.WINDOWS:
            assert new == psutil.IDLE_PRIORITY_CLASS
        else:
            assert new == 19

    def test_real_call_is_idempotent(self):
        # Calling it twice in a row should be harmless and land on the
        # same lowest-priority value both times.
        _, new1 = lower_priority()
        _, new2 = lower_priority()
        assert new1 == new2


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))