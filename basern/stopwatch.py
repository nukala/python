## google AI
# python equivalent to Stopwatch in guava
# `toString` of `Stopwatch` prints elapsed time in seconds or >60 in minutes and so on, is there an equivalent?
# combine the Stopwatch class with a context manager
# pls convert `Stopwatch` into typed equivalent
# can `Stopwatch` have configurable precision `__str__` with default 4 digit
"""
# The stopwatch starts, runs the block, stops, and prints the result automatically
with Stopwatch("Data Processing"):
    time.sleep(1.2)
    
timer = Stopwatch().start()
# ... do task 1 ...
timer.stop()

# ... do unrelated work ...

timer.start() # Resumes from where it left off
# ... do task 2 ...
timer.stop()

print(f"Total active time: {timer}")
"""

import time
from types import TracebackType
from typing import Optional, Type, Self


class Stopwatch:
    def __init__(self, name: str = "Stopwatch", precision: int = 4) -> None:
        """
        Initializes the stopwatch.

        Args:
            name: The identifying label for logging.
            precision: Number of decimal places to show in __str__ (defaults to 4).
        """
        self.name: str = name
        self.precision: int = precision
        self._start_time: Optional[float] = None
        self._elapsed: float = 0.0
        self._running: bool = False

    def start(self) -> Self:
        """Starts the stopwatch. Has no effect if it is already running."""
        if not self._running:
            self._start_time = time.perf_counter()
            self._running = True
        return self

    def stop(self) -> Self:
        """Stops the stopwatch. Has no effect if it is not running."""
        if self._running:
            assert self._start_time is not None
            self._elapsed += time.perf_counter() - self._start_time
            self._running = False
        return self

    def reset(self) -> Self:
        """Resets the elapsed time to zero. Keeps running state intact."""
        self._elapsed = 0.0
        self._start_time = time.perf_counter() if self._running else None
        return self

    @property
    def is_running(self) -> bool:
        """Returns True if the stopwatch is currently tracking time."""
        return self._running

    @property
    def elapsed_seconds(self) -> float:
        """Returns the total elapsed time in seconds."""
        if self._running:
            assert self._start_time is not None
            return self._elapsed + (time.perf_counter() - self._start_time)
        return self._elapsed

    def __str__(self) -> str:
        """Returns an auto-scaling string representation with configurable precision."""
        s: float = self.elapsed_seconds
        p: int = self.precision

        if s >= 3600:
            return f"{s / 3600:.{p}f} h"
        if s >= 60:
            return f"{s / 60:.{p}f} min"
        if s >= 1:
            return f"{s:.{p}f} s"
        if s >= 1e-3:
            return f"{s * 1e3:.{p}f} ms"
        if s >= 1e-6:
            return f"{s * 1e6:.{p}f} μs"
        return f"{s * 1e9:.{p}f} ns"

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> bool:
        self.stop()
        print(f"[{self.name}] Elapsed time: {self}")
        return False
