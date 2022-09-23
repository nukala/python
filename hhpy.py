#!/usr/bin/env python3
# coding: utf-8

import os
import readline


###########################################################################
# To show the history in python buffer
# readline.clear_history()
#
# import importlib; importlib.reload(hhpy)
###########################################################################

def show_history():
  lst = list()
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
