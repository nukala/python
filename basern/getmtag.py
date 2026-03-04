#!/usr/bin/env python3
# coding: utf-8

import sys

def is_windows() -> bool:
  """
  Returns True if system is a Windows machine
  """
  # platform.system shows Windows, CYGWIN_NT-* etc!

  return sys.platform in ("win32", "cygwin", "Windows")


class GetMtag:
  def __init__(self):
    if sys.platform.startswith('freebsd'):
      self.mtag = "unix"
    elif sys.platform.startswith('linux'):
      self.mtag = "unix"
    elif sys.platform.startswith('aix'):
      self.mtag = "unix"
    elif is_windows():
      self.mtag = "PC"
    elif sys.platform.startswith('darwin'):
      self.mtag = "MacOS"
    else:
      self.mtag = None

    if self.mtag == None:
      raise OSError(f"unknown os ${sys.platform}")

  def to_string(self):
    return str(self.mtag)

if __name__ == "__main__":
  gm = GetMtag()
  # so = 12102749; to remove trailing \r
  print(f"{gm.to_string()}", end = "")

