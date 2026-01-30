########################################################################
# WIP - To copy command line args (all of them) into clipboard in a platform neutral way
#
########################################################################

# copy_to_clipboard in gtpull
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
# To help test:  mkdir -p a/b/c/d/e/f/g/h/i/j/k/l/m/n/op/q/r/s/t/u/v/w/x/y/z


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
  parser.add_argument("-r", "--reversed", action="store_true", dest="reversed"
                      , help="Reverse the folder names .../x/y/z becomes z/y/x/...")
  parsed = parser.parse_args()
  if parsed.verbose >= 1:
    print(f"parsed arguments = {parsed}")
      
  end=''
  if parsed.newline:
    end = os.linesep
  print(f"{short_dir(get_pwd(), parsed.num, parsed.separator, parsed.verbose, parsed.reversed)}", end=end)
