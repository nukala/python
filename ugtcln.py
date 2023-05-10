#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from yesno import bool_yesno

import time
import sys
import os
import time
import subprocess


def num_occurrances(str, sep):
  return str.count(sep)


def has_path(str):
  num = num_occurrances(str, "/")
  if num == 0:
    return False
  
  return True


def check_ussh(prog = ""):
  cmd = "usshcertstatus"
  try:
    stat = subprocess.run([cmd], stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT)
  except FileNotFoundError:
    stat = subprocess.CalledProcessError(0, cmd)

  if stat.returncode != 0:
    raise Exception(f"{prog} -- \"{cmd}\" is unsuccessful, fix that to proceed")

  return stat.returncode


########
#
# @__priv__

pfx = "gitolite@code.uber.internal"

if __name__ == "__main__":
  start = time.time()
  if len(sys.argv) == 1:
    print(f"Requires the name of repo to clone{os.linesep}")
    sys.exit(1)
  repo = sys.argv[1]

  dest = None
  if len(sys.argv) > 2:
    dest = sys.argv[2]

  prog = get_prog(__file__)
  check_ussh(prog)

  logf = open(get_tmp_log(prog), "a")
  #print(f"log is at :{logf.name}"); sys.exit(1)

  hasPath = has_path(repo)
  tee_log(logf, f"{prog}: path=[{repo}] hasPath={hasPath}")

  to = repo
  if not hasPath:
    # or is it os.sep?
    to = os.path.basename(os.getcwd()) + "/" + repo

  tee_log(logf, f"{prog}: Recursively cloning [{to}] into :{dest}:")

  # --progress makes logs unreadable
  cmds = ['git', 'clone', '--verbose', f"{pfx}:{to}", '--recursive']
  if dest is not None:
    cmds.append(dest)

  stat = ask_then_run(cmds, logf)
  if stat.returncode != 0:
    tee_log(logf, f"clone({to} {dest}) failed={stat.returncode}! ")

  tee_log(logf, f"{prog}: clone({to} {dest}) consumed {time.time() - start} seconds")
  logf.close()
  sys.exit(stat.returncode)
