from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import (Union)

# claude:
# write me some python code to look up some file information like so
# ===
# 8535747 Apr 29 18:41 FILE_NAME
#
# size in bytes
# modify date and time if within 12 months, else modify date and year
# FILE_NAME
# ===
# use typed methods and parameters
# pls write as many unit tests as possobile

"""
file_info.py

Reproduces the file-info portion of `ls -l` output, e.g.:

    8535747 Apr 29 18:41 FILE_NAME     <- mtime is "recent"
    8535747 Apr 29  2019 FILE_NAME     <- mtime is "old" -> year shown instead of time

Notes on matching real `ls -l`:
  * The byte size column is just the raw size in bytes (no human-readable
    suffixes) -- that's what `-l` alone gives you (`-lh` is the human
    readable variant).
  * GNU coreutils `ls -l` decides between showing "HH:MM" and "YYYY" based
    on whether the file's mtime falls within roughly the last 6 months
    (not 12). This module defaults to 6 months to match real `ls -l`, but
    the threshold is an explicit, overridable parameter -- pass
    `recent_threshold=timedelta(days=365)` if you specifically want a
    12-month cutoff instead.
  * The day-of-month field is space-padded, not zero-padded (i.e. "Apr 9",
    not "Apr 09"), matching strftime's `%e`.
"""


# GNU `ls` uses a ~6 month window. Expressed in days to keep it a pure,
# testable constant (365.25 / 2 ≈ 182.625 -> ls actually uses 15778476
# seconds internally, but 182 days is close enough and easy to reason about).
DEFAULT_RECENT_THRESHOLD: timedelta = timedelta(days=182, hours=15)

PathLike = Union[str, Path]


@dataclass(frozen=True)
class FileInfo:
    """Typed container for the pieces of `ls -l` output we care about."""

    name: str
    size_bytes: int
    mtime: datetime


def get_file_info(path: PathLike,
                  use_absolute: bool = False) -> FileInfo:
    """
    Stat a real file on disk and return a FileInfo describing it.

    Raises FileNotFoundError / OSError the same way pathlib.Path.stat() does
    if the path does not exist or can't be accessed.
    """
    p = Path(path)
    st = p.stat()
    n = p.name if not use_absolute else str(p.absolute())
    return FileInfo(
        name=n,
        size_bytes=st.st_size,
        mtime=datetime.fromtimestamp(st.st_mtime),
    )


def format_size(size_bytes: int) -> str:
    """Format the byte-size column. `ls -l` just prints the raw integer."""
    if size_bytes < 0:
        raise ValueError(f"size_bytes must be non-negative, got {size_bytes}")
    return str(size_bytes)


def _format_month_day(dt: datetime) -> str:
    """
    Cross-platform equivalent of strftime('%b %e'): abbreviated month name
    plus a space-padded (not zero-padded) day-of-month, e.g. "Apr  9" is
    wrong -- real ls gives "Apr  9" as ONE space from %b and the %e field
    itself is 2 chars wide, e.g. " 9". So the result is "Apr" + " " + " 9".
    We build it explicitly since %e is not portable (missing on Windows).
    """
    month = dt.strftime("%b")
    day = f"{dt.day:2d}"  # width-2, space padded, e.g. " 9" or "29"
    return f"{month} {day}"


def is_recent(mtime: datetime, now: datetime, recent_threshold: timedelta) -> bool:
    """
    True if `mtime` falls within `recent_threshold` of `now`, and is not
    in the future. This mirrors `ls -l`'s rule for choosing the time-of-day
    format over the year format.
    """
    delta = now - mtime
    return timedelta(0) <= delta < recent_threshold


def format_mtime(
    mtime: datetime,
    now: datetime | None = None,
    recent_threshold: timedelta = DEFAULT_RECENT_THRESHOLD
) -> str:
    """
    Format a modification time the way `ls -l` does:
      - "Mon DD HH:MM" if mtime is "recent" (see `is_recent`)
      - "Mon DD  YYYY" otherwise (note: two spaces before the year, since
        "HH:MM" and " YYYY" are both rendered as 5-character-wide fields)
    """
    if now is None:
        now = datetime.now()

    month_day = _format_month_day(mtime)

    if is_recent(mtime, now, recent_threshold):
        return f"{month_day} {mtime.strftime('%H:%M')}"
    return f"{month_day}  {mtime.year}"


def format_ls_line(
    info: FileInfo,
    now: datetime | None = None,
    recent_threshold: timedelta = DEFAULT_RECENT_THRESHOLD,
) -> str:
    """
    Produce a full `ls -l`-style info line:
        "SIZE MON DD HH:MM NAME"   or
        "SIZE MON DD  YYYY NAME"
    """
    size = format_size(info.size_bytes)
    when = format_mtime(info.mtime, now=now, recent_threshold=recent_threshold)
    return f"{size} {when} {info.name}"

def format_ls_name(file_name: str,
                   recent_threshold: timedelta = DEFAULT_RECENT_THRESHOLD,
                   use_absolute: bool = True) -> str:
    return format_ls_line(get_file_info(file_name, use_absolute=use_absolute),
                          recent_threshold=recent_threshold)


if __name__ == "__main__":
    import sys

    for arg in sys.argv[1:]:
        print(format_ls_line(get_file_info(arg, use_absolute=True)))