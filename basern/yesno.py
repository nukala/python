#!/usr/bin/env python3
# coding: utf-8

import sys

__debug=False

def yes_no(to_ask = None):
  pmpt = "Yes_or_No ?" if to_ask is None else to_ask

  try:
    v = input(pmpt).upper()
    if len(v) <= 0:
      return 1
    if v[0] == 'Y':
      return 0
    else:
      return 1
  except KeyboardInterrupt:
    print("")
    return 1


def bool_yesno(to_ask):
  ret = yes_no(to_ask)
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
  if __debug:
    print(f"Answer = {ans}, 0 means YES")
  sys.exit(ans)
