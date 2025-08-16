#!/usr/bin/env python3
# coding: utf-8

from argparse import ArgumentParser
import traceback

#######################################################
# Remove files by sending to "RecycleBin" or "Trash", hence the acronym
#
# Soon:
#  verify actual deletion
#  directory support 
#  argparse and help
    #https://github.com/arsenetar/send2trash/blob/master/send2trash/__main__.py

    # for filename in args.files:
#  cleanup (real) rbt?
#######################################################

from basern.getmtag import GetMtag
from basern.rnutils import do_run
from basern.yesno import bool_yesno
from basern.rnutils import is_exists

import sys
import send2trash

class Rbt:
    verbosity: int = 0
    lsl: bool = False
    interactive: bool = False
    # mtag: str = None
    # parser: ArgumentParser = None
    args = None

    def __init__(self):
      self.mtag = GetMtag().to_string()
      # self.parsed = None
      # self.args = None
      # values from CLI
      # self.verbosity = 0
      # self.lsl = False
      # self.interactive = False

    def parse_args(self, args=None):
      ### BROKEN!
      parser = ArgumentParser(description="Tool to send files to trash")
      parser.add_argument("-v", "--verbose", dest="verbosity", action="count", help="Print deleted files")
      parser.add_argument("-l", "--list", dest="lsl", action="store_true", help="List the file details (ls -ltr equiv)")
      parser.add_argument("-i", "--interactive", dest="interactive", action="store_true", help="ask and then recycle/trash")
      parsed, self.args = parser.parse_known_args()

      # population
      if parsed.verbosity is not None:
        self.verbosity = parsed.verbosity
      if parsed.lsl is not None:
        self.lsl = parsed.lsl
      if parsed.interactive is not None:
        self.interactive = parsed.interactive

      if self.verbosity >= 2:
        print(f"parser=[{parsed}],\n verbosity={self.verbosity}, lsl={self.lsl}"
              f", interactive={self.interactive}, tag={self.mtag}"
              f"\n args={self.args}\n\n")

      # post-processing
      if self.interactive:
        self.lsl = True
        if self.verbosity > 1:
          print(f"Force lsl={self.lsl}, due to interactive")

    @staticmethod
    def do_list(fn: str):
      #print(f"Write code to ls -l {fn}")
      do_run(f"ls -ltr {fn}", logf=None, show_result=False)

      pass

    def remove(self, fn:str):
      if not is_exists(fn):
        print(f" File \"{fn}\" does not exist?")
        return False
      do_remove: bool = True
      if self.lsl:
        self.do_list(fn)
      if self.interactive:
        do_remove = bool_yesno(f"Remove [{fn}] (y/n) [n] ")
      try:
        if do_remove:
          send2trash.send2trash(fn)
        else:
          print(f"did not remove file=[{fn}]")
          return False
      except Exception as e:
        print(f"{fn} encountered {str(e)}")
        if self.verbosity >= 2:
          traceback.print_exception(e)
        return False
      
      return True
    
    def show_success(self, fn):
      if self.mtag == "MacOS":
        print(f"Trashed \"{fn}\"\n")
      elif self.mtag == "PC":
        print(f"Sent {fn} to \"Recycle Bin\"")
      else: 
        print(f"rbt'd {fn} for mtag={self.mtag} - NOT SUPPORTED")
    
if __name__ == "__main__":    
  rbt = Rbt()

  rbt.parse_args()
  if rbt.verbosity >= 1:
    print(f"Files = [{rbt.args}]\n")
  for arg in rbt.args:
    if rbt.remove(arg):
      rbt.show_success(arg)

  print("")
