#!/usr/bin/env python3.11
# coding: utf-8

#######################################################
# Remove files by sending to "RecycleBin" or "Trash", hence the acronym
#
# Soon:
#  verify actual deletion
#  directory support 
#  argparse and help
    #https://github.com/arsenetar/send2trash/blob/master/send2trash/__main__.py
    # parser = ArgumentParser(description="Tool to send files to trash")
    # parser.add_argument("files", nargs="+")
    # parser.add_argument("-v", "--verbose", action="store_true", help="Print deleted files")
    # args = parser.parse_args(args)
    # for filename in args.files:
#  cleanup (real) rbt?
#######################################################
import sys
import send2trash
import os

class Rbt:
    def __init__(self):
      pass

    def remove(self, fn):
      try:
        send2trash.send2trash(fn)
      except Exception as e:
        print(f"{fn} encountered {str(e)}")
      
      return True
    
if __name__ == "__main__":    
  rbt = Rbt()
  for arg in sys.argv[1:]:
    print(f"rbt'ing {arg}")
    rbt.remove(arg)

  print("")
