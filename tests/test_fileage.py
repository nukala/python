from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import Mock, patch
from datetime import date, datetime, timedelta
from pathlib import Path

from basern.rnutils import (
     is_file_older_than_today,
     delete_if_older_than_today,
)


#please write me some python code
#==
#Given a filename, if exists check its modified date and created date. Pick the largest. Check if today's date is different from the filename. Return True if older, False if same or newer or missing file as one function
#if different, delete the file as another function invoking the prior method
#use type-safe code and community preferences. functions should be 10-20 lines long, mocks for file-time manipulations
#pls also write unit tests with unittest as one class. Also cleanup any test related artifacts

class FileAgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def _create_file(self, name: str) -> Path:
        path = Path(self.temp_dir.name) / name
        path.write_text("test", encoding="utf-8")
        return path

    def _set_file_date(self, path: Path, target_date: date) -> None:
        timestamp = datetime.combine(
            target_date,
            datetime.min.time(),
        ).timestamp()

        os.utime(path, (timestamp, timestamp))

    def test_missing_file_returns_false(self) -> None:
        path = Path(self.temp_dir.name) / "missing.txt"

        self.assertFalse(is_file_older_than_today(path))
        self.assertFalse(delete_if_older_than_today(path))

    def test_today_file_returns_false(self) -> None:
        path = self._create_file("today.txt")

        self.assertFalse(is_file_older_than_today(path))
        self.assertFalse(delete_if_older_than_today(path))
        self.assertTrue(path.exists())

    def _mock_set_file_timestamps(self, create_stamp: datetime, modify_stamp: datetime = None):
        if not modify_stamp:
                modify_stamp = create_stamp
        mock_stat = Mock()

        mock_stat.st_ctime = create_stamp.timestamp()
        mock_stat.st_mtime = modify_stamp.timestamp()
        return mock_stat

    def test_old_file_mtime_before_ctime_returns_true(self) -> None:
        path = self._create_file("old.txt")
        #self._set_file_date(path, date.today() - timedelta(days=2))
        mock_stat = self._mock_set_file_timestamps(datetime.today() - timedelta(days=2),  
                                    datetime.today() - timedelta(days=3))

        #print(f"path=[{path}]")
        with patch("pathlib.Path.stat", return_value = mock_stat):
            self.assertTrue(is_file_older_than_today(path))

    def test_old_file_mtime_after_ctime_returns_true(self) -> None:
        path = self._create_file("mod_after_crt.txt")
        crt_ts = datetime.now() - timedelta(days=3)
        mod_ts = datetime.now() - timedelta(hours=24)
        #print(f"crt_ts={crt_ts}, mod_ts={mod_ts}")
        mock_stat = self._mock_set_file_timestamps(crt_ts, mod_ts)

        #print(f"path=[{path}]")
        with patch("pathlib.Path.stat", return_value = mock_stat):
            self.assertTrue(is_file_older_than_today(path))

    def test_old_file_is_deleted(self) -> None:
        path = self._create_file("delete_me.txt")
        #self._set_file_date(path, date.today() - timedelta(days=2))

        mock_stat = self._mock_set_file_timestamps(datetime.today() - timedelta(days=2),  
                                    datetime.today() - timedelta(days=3))

        #print(f"path=[{path}]")
        with patch("pathlib.Path.stat", return_value = mock_stat):
            self.assertTrue(delete_if_older_than_today(path))

        self.assertFalse(path.exists())

    def test_today_file_is_not_deleted(self) -> None:
        path = self._create_file("keep_me.txt")

        self.assertFalse(delete_if_older_than_today(path))
        self.assertTrue(path.exists())
