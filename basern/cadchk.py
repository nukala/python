#!/usr/bin/env python3
# coding: utf-8

import json
import tempfile
import os
import sys
import rnutils

from pathlib import Path

####################################################################
# Show the diffs among the CAD (Cookie-Auto-Delete addon) expressions
#   -> easy way to confirm if there are differences
#
####################################################################

def make_expr_file(inpfn, pfx = "tmp-"):
  print("Processing " + inpfn + ", pfx=" + pfx)
  if not os.path.isfile(inpfn):
    raise Exception('no such file: ' + inpfn)

  exps = []
  with open(inpfn, "r") as rf:
    data = json.load(rf)
    for d in data['default']:
      exp = d['expression']
      exps.append(exp)

  # Generate a temporary file-object that will deleteOnExit
  # returning name or closing the temp-file unlinks in filesystem
  tmpff = tempfile.NamedTemporaryFile(prefix = pfx, suffix = ".cdchk", delete = False)
  #print("Found " + str(len(exps)) + " items in " + inpfn)
  ss = os.linesep.join(exps) + os.linesep
  tmpff.write(ss.encode())
  tmpff.flush()
  #print("    wrote into [" + tmpff.name + "]")
  return tmpff

boxFN = str(os.environ['BOXDIR']) + os.sep + "CAD-Expressions.json"

##########
##

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("Requires a file to compare boxdir version against.")
    print("Optionally 2nd paramter is boxfile")
    sys.exit(2)

  ff = make_expr_file(sys.argv[1])
  if len(sys.argv) > 2:
    boxFN = sys.argv[2]
#    print(f"Using boxFN={boxFN}")

  bff = make_expr_file(boxFN, pfx = "box-")

  #os.system('ls -ltrd ' + ff + " " + bff)

  # -U is context around a diff, 0 is very minimal
  try:
    rnutils.do_run(f"sort -o {ff.name} {ff.name}", None, show_result = False)
    rnutils.do_run(f"sort -o {bff.name} {bff.name}", None, show_result = False)
    rnutils.tee_log(None, "\n")

    stat = rnutils.do_run("git diff --no-index -w -U1 " + ff.name + " " + bff.name, None, show_result = False)
    if stat.returncode == 0:
      print(f">>> NO DIFFERENCES")

    print(f"Removing {ff.name} and {bff.name}")
    os.remove(ff.name)
    os.remove(bff.name)
  except:
    pass
