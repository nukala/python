#!/usr/bin/env python3
# coding: utf-8

### MAY NOT WORK DUE TO MESSED UP IMPORTS
from rnutils import *
from ugtcln import check_ussh

import os
import subprocess as sp
import sys
import time


def do_make(tgt, logf, env = None):
  # TODO - figure out how to append to list , type(tgt) == list?
  myenv = dict(os.environ)
  if env != None:
    myenv.update(env)
  theenv = dict(myenv, V = "1", VERBOSE = "1", SHDEBUG="true")

  cmd = "make"
  print(f"tail -f {get_pwd()}{os.sep}{logf.name} in a different terminal")
  stat = do_run([cmd, tgt],
           logf,
		   show_output = True,
           special_env = theenv)
  return stat


def make_targets(targets, logf, special_env = None):
  ans = {}
  stat = None
  for tgt in targets:
    tee_log(logf, f"making {tgt}")
    stat = do_make(tgt, logf)
    ans['status'] = stat
    ans['target'] = tgt
    if stat.returncode is not 0:
      break

    # success !!!
    tee_log(logf, f"build {tgt} success")
    do_nap(5, logf)
  # end-loop on targets

  tee_log(logf, f"make targets returning [{ans}]")
  return ans


##########
# To capture logs into a {TARGET}.log format
# Force verbosity too

def main():
  start = time.time()
  tgt = None
  if len(sys.argv) >= 2:
    tgt = sys.argv[1]

  if tgt == None:
    print(f"{prog}: required argument \"target\" not specified");
    return 1

  lognm = None
  if len(sys.argv) >= 3:
    lognm = sys.argv[2]

  if lognm == None:
    lognm = get_next_logname(f"{tgt}.log")
  print(f"Using log={lognm}, for target={tgt}")
  logf = open(lognm, "w")
  log_started_message(logf, prog)
  stat = do_make(tgt, logf)
  print(f"{prog}: make {tgt} returned = {stat.returncode}")
  return stat.returncode




##########
#

prog = get_prog(__file__)

if __name__ == "__main__" :
  sys.exit(main())
