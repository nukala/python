#!/usr/bin/env python3.11
# coding: utf-8

import os

import sys
import uuid


class ToUUID:
  def __init__(self, arg):
    self.uuid = uuid.UUID(arg)
    self.dashed = str(self.uuid)
    self.cleaned = arg.replace("-", "")

  def with_dashes(self):
    return self.dashed

  def no_dashes(self):
    return self.cleaned

if __name__ == "__main__":
  tu = ToUUID(sys.argv[1])
  print(f"_sourceCategory=prod/core/* ( {tu.with_dashes()} OR {tu.no_dashes()} ) ")

