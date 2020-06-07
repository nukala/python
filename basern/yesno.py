#!/usr/bin/env python3
# coding: utf-8

import sys
import os

def yes_no(prompt):
  pmpt = prompt
  if prompt == None:
    pmpt = "yes_or_no "

  try:
    v = input(pmpt)
    if len(v) <= 0:
      return 1
    if v[0] == 'y' or v[0] == 'Y':
      return 0
    else:
      return 1
  except KeyboardInterrupt:
    print("")
    return 1


def bool_yesno(prompt):
  ret = yes_no(prompt)
  if ret == 0:
    return True

  return False



############
# Ask for an answer. Again, like in entorint.py, interrupt on a read kills the invoking shell

if __name__ == "__main__" :
  prompt = None
  if len(sys.argv) > 1:
    prompt = sys.argv[1]

  ans = yes_no(prompt)
  #print(f"Answer = {ans}, 0 means YES")
  sys.exit(ans)
