#!/usr/bin/env python3
# coding: utf-8

import sys
import os

def ent_int(prompt):
  if prompt != None and len(prompt) > 0:
    print(prompt, end = '')
  sys.stdout.flush()
  try:
    sys.stdin.readline().strip()
    return 0
  except KeyboardInterrupt:
    cmd = f"kill -USR1 {os.getppid()}"
    #print(f"executing [{cmd}]")
    os.system(cmd)
    return 1


if __name__ == "__main__" :
  if len(sys.argv) > 1:
    prompt = sys.argv[1]
  else:
    prompt = "Enter or ^C "

  ent_int(prompt)
  sys.exit(0)
