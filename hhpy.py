#!/usr/bin/env python3
# coding: utf-8

import os

try:
  import readline
except ImportError:
  # fallback to Windows, customize later
  from pyreadline3 import Readline
  readline = Readline()

###########################################################################
# To show the history in python buffer
# readline.clear_history()
#
# import importlib; importlib.reload(hhpy)
###########################################################################


# /// script
# dependencies = [
#    "readline; sys_platform != 'win32'",
#    "pyreadline3; sys_platform == 'win32'",
# ]
# ///

def show_history():
  lst = list()
  print(f" found {readline.get_current_history_length()} history items")
  for i in range(readline.get_current_history_length()):
    item = readline.get_history_item(i)
    if item in lst:
      pass
    else:
      lst.append(item)

    num = 0
    for item in lst:
      print(f"{num}:  {item}")
      num+=1
    print(f"current_length = {readline.get_current_history_length()}, unique={len(lst)}")


if __name__ == "__main__":
  show_history()
