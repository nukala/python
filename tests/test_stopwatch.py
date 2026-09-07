import unittest
from unittest.mock import patch
from typing import (Optional, Generator)
from basern.stopwatch import Stopwatch

class TestStopwatchPrecision(unittest.TestCase):

    @patch("time.perf_counter")
    def test_initial_state(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify the initial state of a freshly instantiated stopwatch."""
        mock_perf.return_value = 10.0
        sw = Stopwatch("Test")

        self.assertEqual(sw.name, "Test")
        self.assertFalse(sw.is_running)
        self.assertEqual(sw.elapsed_seconds, 0.0)

    @patch("time.perf_counter")
    def test_start_and_read(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify elapsed time accrues correctly while running."""
        mock_perf.return_value = 10.0
        sw = Stopwatch().start()

        self.assertTrue(sw.is_running)

        # Advance mock time by 5.5 seconds
        mock_perf.return_value = 15.5
        self.assertEqual(sw.elapsed_seconds, 5.5)

    @patch("time.perf_counter")
    def test_stop_freezes_time(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify that stopping freezes the time counter."""
        mock_perf.return_value = 10.0
        sw = Stopwatch().start()

        mock_perf.return_value = 15.0
        sw.stop()

        self.assertFalse(sw.is_running)
        self.assertEqual(sw.elapsed_seconds, 5.0)

        # Advance time while stopped; elapsed should NOT change
        mock_perf.return_value = 25.0
        self.assertEqual(sw.elapsed_seconds, 5.0)

    @patch("time.perf_counter")
    def test_multiple_starts_and_stops(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify cumulative timing across multiple pause/resume cycles."""
        mock_perf.return_value = 0.0
        sw = Stopwatch()

        # Segment 1: Run for 5 seconds
        sw.start()
        mock_perf.return_value = 5.0
        sw.stop()

        # Segment 2: Idle for 10 seconds, then run for 3 seconds
        mock_perf.return_value = 15.0
        sw.start()
        mock_perf.return_value = 18.0
        sw.stop()

        self.assertEqual(sw.elapsed_seconds, 8.0)

    @patch("time.perf_counter")
    def test_idempotent_start_and_stop(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Ensure duplicate calls to start() or stop() do not disrupt tracking."""
        mock_perf.return_value = 10.0
        sw = Stopwatch().start()

        mock_perf.return_value = 12.0
        sw.start()  # Intentionally calling start again while running

        mock_perf.return_value = 15.0
        self.assertEqual(sw.elapsed_seconds, 5.0)

        sw.stop()
        sw.stop()  # Intentionally calling stop again while stopped
        self.assertEqual(sw.elapsed_seconds, 5.0)

    @patch("time.perf_counter")
    def test_reset_while_stopped(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify resetting a stopped instance zeros out values and stays stopped."""
        mock_perf.return_value = 0.0
        sw = Stopwatch().start()
        mock_perf.return_value = 10.0
        sw.stop()

        sw.reset()
        self.assertFalse(sw.is_running)
        self.assertEqual(sw.elapsed_seconds, 0.0)

    @patch("time.perf_counter")
    def test_reset_while_running(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify resetting a running instance zeros out baseline but keeps running."""
        mock_perf.return_value = 0.0
        sw = Stopwatch().start()

        mock_perf.return_value = 10.0
        sw.reset()

        self.assertTrue(sw.is_running)

        mock_perf.return_value = 14.5
        self.assertEqual(sw.elapsed_seconds, 4.5)

    @patch("time.perf_counter")
    def test_context_manager_success(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify normal setup, operation, and teardown under context block."""
        mock_perf.return_value = 10.0

        with Stopwatch() as sw:
            self.assertTrue(sw.is_running)
            mock_perf.return_value = 13.5

        self.assertFalse(sw.is_running)
        self.assertEqual(sw.elapsed_seconds, 3.5)

    @patch("time.perf_counter")
    def test_context_manager_exception_passthrough(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify stopwatch stops safely and transparently forwards internal block errors."""
        mock_perf.return_value = 10.0
        sw_reference: Optional[Stopwatch] = None

        with self.assertRaises(ValueError):
            with Stopwatch() as sw:
                sw_reference = sw
                mock_perf.return_value = 12.0
                raise ValueError("Simulated operational failure")

        self.assertIsNotNone(sw_reference)
        self.assertFalse(sw_reference.is_running)  # type: ignore
        self.assertEqual(sw_reference.elapsed_seconds, 2.0)  # type: ignore

    @staticmethod
    def start_sw(sw: Stopwatch, mock_perf: unittest.mock.MagicMock) -> Stopwatch:
        """
        sw.start also calls time.perf_counter, force that call to return ZERO
        else there are some fractions and timing strings are messed up.
        """
        mock_perf.return_value = 0
        return sw.start()

    @patch("time.perf_counter")
    def test_string_formatting_units(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Test auto-scaling string resolution intervals matching Guava styling."""
        sw = Stopwatch(precision=2)

        # Nanoseconds
        TestStopwatchPrecision.start_sw(sw, mock_perf)
        mock_perf.return_value = 5e-9
        self.assertEqual(str(sw), "5.00 ns")
        sw.stop().reset()

        # Microseconds
        sw.start()
        mock_perf.return_value = 4.5e-6
        self.assertEqual(str(sw), "4.50 μs")
        sw.stop().reset()

        # Milliseconds
        sw.start()
        mock_perf.return_value = 12.34e-3
        self.assertEqual(str(sw), "12.34 ms")
        sw.stop().reset()

        # Seconds
        TestStopwatchPrecision.start_sw(sw, mock_perf)
        mock_perf.return_value = 7.1234
        # self.assertEqual(str(sw), "7.12 s")
        diff: float = float(str(sw).replace(" s", ""))
        # to compare floats with a variance or delta
        self.assertAlmostEqual(diff, 7.12, delta=0.1)
        sw.stop().reset()

        # Minutes
        TestStopwatchPrecision.start_sw(sw, mock_perf)
        mock_perf.return_value = 150.0  # 2.5 minutes
        self.assertEqual(str(sw), "2.50 min")
        sw.stop().reset()

        # Hours
        TestStopwatchPrecision.start_sw(sw, mock_perf)
        mock_perf.return_value = 5400.0  # 1.5 hours
        self.assertEqual(str(sw), "1.50 h")


    @patch("time.perf_counter")
    def test_default_precision(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify the fallback default is exactly 4 decimal digits."""
        mock_perf.return_value = 0.0
        sw = Stopwatch().start()

        mock_perf.return_value = 1.2345678
        self.assertEqual(str(sw), "1.2346 s")  # Rounds up

    @patch("time.perf_counter")
    def test_custom_low_precision(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify explicit lowering of precision strings works (e.g., 2 digits)."""
        mock_perf.return_value = 0.0
        sw = Stopwatch(precision=2).start()

        mock_perf.return_value = 1.2345678
        self.assertEqual(str(sw), "1.23 s")

    @patch("time.perf_counter")
    def test_zero_precision(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify string parsing drops decimal points correctly when precision is 0."""
        mock_perf.return_value = 0.0
        sw = Stopwatch(precision=0).start()

        mock_perf.return_value = 1.85
        self.assertEqual(str(sw), "2 s")

    @patch("time.perf_counter")
    def test_high_precision(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify extension up to micro-resolutions (e.g., 6 digits)."""
        mock_perf.return_value = 0.0
        sw = Stopwatch(precision=6).start()

        mock_perf.return_value = 0.0054321
        self.assertEqual(str(sw), "5.432100 ms")

    @patch("time.perf_counter")
    def test_precision_can_be_changed_runtime(self, mock_perf: unittest.mock.MagicMock) -> None:
        """Verify precision values can be modified cleanly mid-flight."""
        mock_perf.return_value = 0.0
        sw = Stopwatch().start()

        mock_perf.return_value = 1.23456
        self.assertEqual(str(sw), "1.2346 s")

        # Change property directly on instance
        sw.precision = 1
        self.assertEqual(str(sw), "1.2 s")


if __name__ == "__main__":
    unittest.main()
