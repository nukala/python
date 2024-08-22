#!/usr/bin/env python3 
# coding: utf-8 

from basern.rnutils import *
from argparse import ArgumentParser


"""
"""
#To return a shorter version of pwd. 
# if > 3 return 3 dirnames
# if 2 return those two
# else return entire
#
#Works in C: drive and many other folders.
#
#TODO: p3 C\:/data/ravi/home/mine/rnpydev/basern/smpwd.py  | sed 's/\//-/g' <<< with args and new-line

if __name__ == "__main__":
  parser = ArgumentParser(prog='smpwd', description='return a FS-separated pwd of specified elements')
  parser.add_argument("-s", "--size", "-n", "--num", type=int, default=3, dest="num",
                      help="Number of folders to recurse")
  parser.add_argument("-v", "--verbose", action="count", default=0
                      , help="verbose, supports -vv for more verbose"
                      , dest="verbose")
  parser.add_argument("-nl", "--new_line", action="store_true", dest="newline"
                      , help="terminate with a new line")
  parser.add_argument("-p", "-sep", "--separator", type=str, dest="separator"
                      , help="path element separator")
  parsed = parser.parse_args()
  if parsed.verbose >= 1:
    print(f"parsed arguments = {parsed}")
      
  end=''
  if parsed.newline:
    end = os.linesep
  print(f"{short_pwd(parsed.num, parsed.separator, parsed.verbose)}", end=end)
