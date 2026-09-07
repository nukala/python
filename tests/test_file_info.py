"""
Unit tests for file_info.py

Run with:
    python -m unittest test_file_info.py -v
or:
    python -m pytest test_file_info.py -v
"""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from basern.file_info import (
    DEFAULT_RECENT_THRESHOLD,
    FileInfo,
    format_ls_line,
    format_mtime,
    format_size,
    get_file_info,
    is_recent,
)


FIXED_NOW = datetime(2024, 6, 15, 12, 0, 0)


class FormatSizeTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_size(0), "0")

    def test_small_size(self):
        self.assertEqual(format_size(42), "42")

    def test_typical_size(self):
        self.assertEqual(format_size(8535747), "8535747")

    def test_large_size(self):
        self.assertEqual(format_size(123456789012), "123456789012")

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            format_size(-1)


class IsRecentTests(unittest.TestCase):
    def test_now_exactly_is_recent(self):
        self.assertTrue(is_recent(FIXED_NOW, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))

    def test_one_second_ago_is_recent(self):
        mtime = FIXED_NOW - timedelta(seconds=1)
        self.assertTrue(is_recent(mtime, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))

    def test_just_under_threshold_is_recent(self):
        mtime = FIXED_NOW - (DEFAULT_RECENT_THRESHOLD - timedelta(seconds=1))
        self.assertTrue(is_recent(mtime, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))

    def test_exactly_at_threshold_is_not_recent(self):
        # boundary is exclusive: delta < threshold, not <=
        mtime = FIXED_NOW - DEFAULT_RECENT_THRESHOLD
        self.assertFalse(is_recent(mtime, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))

    def test_just_over_threshold_is_not_recent(self):
        mtime = FIXED_NOW - (DEFAULT_RECENT_THRESHOLD + timedelta(seconds=1))
        self.assertFalse(is_recent(mtime, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))

    def test_future_mtime_is_not_recent(self):
        mtime = FIXED_NOW + timedelta(days=1)
        self.assertFalse(is_recent(mtime, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))

    def test_far_future_mtime_is_not_recent(self):
        mtime = FIXED_NOW + timedelta(days=3650)
        self.assertFalse(is_recent(mtime, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))

    def test_custom_threshold_12_months(self):
        twelve_months = timedelta(days=365)
        mtime = FIXED_NOW - timedelta(days=200)  # >6mo old, <12mo old
        self.assertFalse(is_recent(mtime, FIXED_NOW, DEFAULT_RECENT_THRESHOLD))
        self.assertTrue(is_recent(mtime, FIXED_NOW, twelve_months))

    def test_custom_threshold_zero_never_recent(self):
        mtime = FIXED_NOW
        self.assertFalse(is_recent(mtime, FIXED_NOW, timedelta(0)))


class FormatMtimeTests(unittest.TestCase):
    def test_recent_shows_time(self):
        mtime = datetime(2024, 4, 29, 18, 41, 0)
        self.assertEqual(format_mtime(mtime, now=FIXED_NOW), "Apr 29 18:41")

    def test_old_shows_year(self):
        mtime = datetime(2019, 4, 29, 18, 41, 0)
        self.assertEqual(format_mtime(mtime, now=FIXED_NOW), "Apr 29  2019")

    def test_single_digit_day_is_space_padded(self):
        mtime = datetime(2024, 6, 5, 9, 5, 0)
        self.assertEqual(format_mtime(mtime, now=FIXED_NOW), "Jun  5 09:05")

    def test_double_digit_day_no_extra_padding(self):
        mtime = datetime(2024, 6, 15, 0, 0, 0)
        self.assertEqual(format_mtime(mtime, now=FIXED_NOW), "Jun 15 00:00")

    def test_midnight_formats_as_00_00(self):
        mtime = datetime(2024, 6, 1, 0, 0, 0)
        self.assertEqual(format_mtime(mtime, now=FIXED_NOW), "Jun  1 00:00")

    def test_one_minute_before_midnight(self):
        mtime = datetime(2024, 6, 1, 23, 59, 0)
        self.assertEqual(format_mtime(mtime, now=FIXED_NOW), "Jun  1 23:59")

    def test_old_year_field_has_two_leading_spaces(self):
        mtime = datetime(2010, 1, 1, 0, 0, 0)
        result = format_mtime(mtime, now=FIXED_NOW)
        self.assertIn("  2010", result)
        self.assertTrue(result.endswith("  2010"))

    def test_future_mtime_shows_year_not_time(self):
        mtime = FIXED_NOW + timedelta(days=30)
        result = format_mtime(mtime, now=FIXED_NOW)
        self.assertTrue(result.endswith(str(mtime.year)))

    def test_default_now_does_not_raise(self):
        # Smoke test that omitting `now` uses datetime.now() without error.
        mtime = datetime.now() - timedelta(days=1)
        result = format_mtime(mtime)
        self.assertIsInstance(result, str)

    def test_custom_threshold_changes_output(self):
        mtime = FIXED_NOW - timedelta(days=200)  # 6mo default = not recent
        default_result = format_mtime(mtime, now=FIXED_NOW)
        twelve_month_result = format_mtime(
            mtime, now=FIXED_NOW, recent_threshold=timedelta(days=365)
        )
        self.assertIn(str(mtime.year), default_result)
        self.assertNotIn(str(mtime.year), twelve_month_result)
        self.assertIn(":", twelve_month_result)

    def test_all_month_abbreviations_recent(self):
        expected = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        now = datetime(2024, 12, 31, 23, 59, 59)
        for month, abbrev in enumerate(expected, start=1):
            mtime = datetime(2024, month, 10, 8, 0, 0)
            result = format_mtime(mtime, now=now)
            self.assertTrue(result.startswith(abbrev), f"{result!r} should start with {abbrev!r}")


class FormatLsLineTests(unittest.TestCase):
    def test_matches_prompt_example_recent(self):
        info = FileInfo(
            name="FILE_NAME",
            size_bytes=8535747,
            mtime=datetime(2024, 4, 29, 18, 41, 0),
        )
        result = format_ls_line(info, now=FIXED_NOW)
        self.assertEqual(result, "8535747 Apr 29 18:41 FILE_NAME")

    def test_matches_prompt_example_old(self):
        info = FileInfo(
            name="FILE_NAME",
            size_bytes=8535747,
            mtime=datetime(2019, 4, 29, 18, 41, 0),
        )
        result = format_ls_line(info, now=FIXED_NOW)
        self.assertEqual(result, "8535747 Apr 29  2019 FILE_NAME")

    def test_zero_byte_file(self):
        info = FileInfo(name="empty.txt", size_bytes=0, mtime=FIXED_NOW)
        result = format_ls_line(info, now=FIXED_NOW)
        self.assertTrue(result.startswith("0 "))

    def test_filename_with_spaces_preserved(self):
        info = FileInfo(
            name="my file.txt", size_bytes=100, mtime=FIXED_NOW
        )
        result = format_ls_line(info, now=FIXED_NOW)
        self.assertTrue(result.endswith("my file.txt"))

    def test_filename_with_special_characters(self):
        info = FileInfo(
            name="report_final(v2)[draft].txt", size_bytes=100, mtime=FIXED_NOW
        )
        result = format_ls_line(info, now=FIXED_NOW)
        self.assertTrue(result.endswith("report_final(v2)[draft].txt"))


class GetFileInfoTests(unittest.TestCase):
    def test_reads_real_file_size_and_name(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "sample.txt"
            content = b"x" * 1234
            file_path.write_bytes(content)

            info = get_file_info(file_path)

            self.assertEqual(info.size_bytes, 1234)
            self.assertEqual(info.name, "sample.txt")
            self.assertIsInstance(info.mtime, datetime)

    def test_reads_real_file_mtime(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "sample.txt"
            file_path.write_bytes(b"data")

            target_mtime = datetime(2020, 3, 14, 9, 26, 53)
            target_epoch = target_mtime.timestamp()
            os.utime(file_path, (target_epoch, target_epoch))

            info = get_file_info(file_path)

            # Compare at second resolution; filesystem/timestamp precision
            # can introduce sub-second float noise.
            self.assertEqual(int(info.mtime.timestamp()), int(target_epoch))

    def test_accepts_string_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "sample.txt"
            file_path.write_bytes(b"abc")

            info = get_file_info(str(file_path))
            self.assertEqual(info.size_bytes, 3)

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "does_not_exist.txt"
            with self.assertRaises(OSError):
                get_file_info(missing)

    def test_end_to_end_line_for_real_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "FILE_NAME"
            file_path.write_bytes(b"x" * 8535747)

            target_mtime = datetime(2024, 4, 29, 18, 41, 0)
            target_epoch = target_mtime.timestamp()
            os.utime(file_path, (target_epoch, target_epoch))

            info = get_file_info(file_path)
            result = format_ls_line(info, now=FIXED_NOW)

            self.assertEqual(result, "8535747 Apr 29 18:41 FILE_NAME")


if __name__ == "__main__":
    unittest.main()