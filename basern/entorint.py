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


#############
# Some shell scripts usually ask - "To continue hit enter, else Control-C to interrupt" kind of messages.
#
# With the new bash upgrade, SIGINT kills the bash shell. I have not found a easy way to suppress that. 
# This is an attempt using python
#

if __name__ == "__main__" :
  if len(sys.argv) > 1:
    prompt = sys.argv[1]
  else:
    prompt = "Enter or ^C "

  stat = ent_int(prompt)
  sys.exit(stat)
