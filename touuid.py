#!/usr/bin/env python3.11
# coding: utf-8

import os

import sys
import uuid


class ToUUID:
  def __init__(self, arg):
    self.uuid = uuid.UUID(arg)

  def to_string(self):
    return str(self.uuid)

if __name__ == "__main__":
  tu = ToUUID(sys.argv[1])
  print(f"{tu.to_string()}")

