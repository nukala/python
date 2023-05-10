#!/usr/bin/env python3
# coding: utf-8

import os
import platform

import sys


class GetMtag:
  def __init__(self):
    if sys.platform.startswith('freebsd'):
      self.mtag = "unix"
    elif sys.platform.startswith('linux'):
      self.mtag = "unix"
    elif sys.platform.startswith('aix'):
      self.mtag = "unix"
    elif sys.platform.startswith('win32'):
      self.mtag = "PC"
    elif sys.platform.startswith('cygwin'):
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
  print(f"{gm.to_string()}")

