"""
proc_utils.py

Utility helpers for adjusting the current process's scheduling priority.
"""

from __future__ import annotations

from typing import Tuple


# paste old-code and ask claude for doc-changes and tests
class ProcUtils:
    """Namespace for process-related utility functions."""

    @staticmethod
    def lower_priority(verbose: int = 0) -> Tuple[int, int]:
        """
        Lower the priority of the *current process* to the lowest
        practical level for its platform.

        On Windows this sets the process priority class to
        ``IDLE_PRIORITY_CLASS``. On POSIX systems (Linux/macOS) it sets
        the "niceness" to 19, the maximum value on most systems, which
        corresponds to the *lowest* scheduling priority (on POSIX,
        higher nice values mean lower priority - the opposite of
        Windows priority classes).

        This is useful for background/batch jobs that should not
        compete with interactive processes for CPU time.

        Args:
            verbose: If greater than 0, print the old and new
                niceness/priority values to stdout. If 0 (default),
                nothing is printed.

        Returns:
            A tuple ``(old, new)`` with the process's niceness/priority
            value before and after the change, as reported by
            ``psutil.Process.nice()``. On POSIX this is the nice value
            (e.g. 0 -> 19). On Windows it is the raw priority-class
            constant (e.g. ``psutil.NORMAL_PRIORITY_CLASS`` ->
            ``psutil.IDLE_PRIORITY_CLASS``).

        Raises:
            psutil.AccessDenied: If the OS denies permission to change
                the process priority (rare for *lowering* priority,
                but possible depending on platform/sandboxing).
            psutil.NoSuchProcess: If the process no longer exists by
                the time the priority change is attempted (extremely
                unlikely for the current process).

        Example:
            >>> ProcUtils.lower_priority(verbose=1)
            old niceness=[0], current=[19]
            (0, 19)
        """
        import psutil

        p = psutil.Process()
        old = p.nice()
        if psutil.WINDOWS:
            p.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            # On Unix/Linux/macOS, higher nice values mean lower priority (19 is max low)
            p.nice(19)
        new = p.nice()
        if verbose > 0:
            print(f"old niceness=[{old}], current=[{new}]")
        return old, new
