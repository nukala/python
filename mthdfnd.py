#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from gtpull import getoutput_from_run

import sys
import os
import subprocess
import datetime
import time

# import path to use in `rg` 
impPath = "code.uber.internal/infra/schemaless-client-go"
# package in the importPath above that is of interest
pkgToCheck = "schemaless"
# method to check for that package no matter the alias and import line
mthdToCheck = "New"

"""
To find the impPath in all the files under a folder 
then compute alias to use
then grep-n usages mthdToCheck 
"""


def find_alias(line, default = "schemaless"):
  if contains(line, "/" + pkgToCheck) == True: 
    line = line.replace("import", "").strip()
    line = line.replace('\"', '').replace('\)', '').replace('\(', '')
    #print(f"  after quote,import,strip = [{line}]")

    ### double check
    if not line.endswith(pkgToCheck):
      return None

    sep = None
    if contains(line, " "):
      sep = " "
    elif contains(line, "\t"):
      sep = "\t"
    else:
      return default

    parts = line.split(sep)
    return parts[0]

  return None

def get_alias(fn, show_grep = False):
  if show_grep: 
    subprocess.run(['grep', impPath + ".*/" + pkgToCheck, fn])
  with open(fn, "r") as file:
    for line in file:
      if impPath in line:
        alias = find_alias(line)
        if alias != None:
          return alias

      continue

def main():
  log_started_message(None, prog)
  files = getoutput_from_run(['rg', '-g', '*.go', '-l',
                   impPath + ".*/" + pkgToCheck], None, show_output = False,
		   show_result = False)['stdout'].split(os.linesep)
  #print(f"files={files}.{len(files)}")
  print(f"Examing {len(files)} files")

  matched = 0
  for fn in files:
    #print(f"{fn}")
    alias = get_alias(fn)
    if alias == None:
      continue
    #print(f"{prog}: alias={alias}")

    stat = getoutput_from_run(['grep', '-n', alias + "." + mthdToCheck + "(", fn], None, show_result = False)
    if stat['returncode'] == 0:
      print(f"=== {fn} ===")
      print(f"{stat['stdout']}")
      print(f"--- {fn} ---{os.linesep}")
      matched += 1

  print(f"Examined {len(files)} and found matches in {matched} files, " +
        f"elapsed={round(time.time() - start, 2)} seconds");

#####
# 
# @__priv__

start = time.time()
prog = get_prog(__file__)


def chk(line, name, exp = None):
  print(f"{os.linesep}{name}=[{line}], exp={exp}")
  alias = find_alias(line)
  print(f"      [{name}] = {alias}")
  if exp != None and alias != None:
    if exp != alias:
      raise Exception(f"expected {exp} actual={alias} dont match.")
    

def tst():
   only_line = '"code.uber.internal/infra/schemaless-client-go/schemaless"'
   chk(only_line, "only_line", 'schemaless')

   alias_only = 'foo "code.uber.internal/infra/schemaless-client-go/schemaless"'
   chk(alias_only, "alias_only", 'foo')

   tab_alias_only = 'tab	"code.uber.internal/infra/schemaless-client-go/schemaless"'
   chk(tab_alias_only, "tab_alias_only", 'tab')

   import_line = 'import "code.uber.internal/infra/schemaless-client-go/schemaless"'
   chk(import_line, "import_line", 'schemaless')

   imp_tabs = 'import	foo	"code.uber.internal/infra/schemaless-client-go/schemaless"'
   chk(imp_tabs, 'imp_tabs', 'foo')

   imp_tabs_none = 'import	"code.uber.internal/infra/schemaless-client-go/schemaless"'
   chk(imp_tabs_none, 'imp_tabs_none', 'schemaless')

   docsfx = '"code.uber.internal/infra/schemaless-client-go.git/docstorefx"'
   chk(docsfx, 'docsfx')


if __name__ == "__main__":
  if len(sys.argv) == 1:
    sys.exit(main())
  arg = sys.argv[1]
  if arg == "tst":
    tst()
  else:
    alias = get_alias(arg)
    if alias != None:
      print(f"[{arg}] = {get_alias(arg)}")
