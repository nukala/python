#!/usr/bin/env python3
# coding: utf-8
import sys
import traceback
from argparse import ArgumentParser

import send2trash

from basern.getmtag import GetMtag
from basern.rnutils import do_run
from basern.rnutils import is_exists
from basern.yesno import bool_yesno
from ghsv import dbgln


#######################################################
# Remove files by sending to "RecycleBin" or "Trash", hence the acronym
#
# Soon:
#  verify actual deletion
#  directory support
#  argparse and help
# https://github.com/arsenetar/send2trash/blob/master/send2trash/__main__.py
# for filename in args.files:
#  cleanup (real) rbt?
#######################################################

class Rbt:
    verbose: int = 0
    skip_listing: bool = False
    interactive: bool = False
    args: list = None
    parser : ArgumentParser = None

    def __str__(self):
      return f"verbosity={self.verbose}, skip_listing={self.skip_listing}, interactive={self.interactive}, tag={self.mtag}"

    @staticmethod
    def do_list(fn: str, verbosity: int = 0):
      cmd = f"ls -ltr \"{fn}\" "
      dbgln(f"Executing [{cmd}]", 2, verbosity)
      do_run(cmd, logf=None, show_result=False)

    def __init__(self):
      self.mtag = GetMtag().to_string()
      self.separator = False

    def populate_cli_args(self, parsed):
        """
        Populate various fields from `parsed` into `self`
        """
        if parsed.verbose:
            self.verbose = parsed.verbose
        if parsed.skip_listing is not None:
            self.skip_listing = parsed.skip_listing
        if parsed.interactive is not None:
            self.interactive = parsed.interactive
        if parsed.separator is not None:
            self.separator = parsed.separator

        dbgln(f"parsed=[{parsed}],\n self={str(self)}"
                f"\n args={self.args}\n", 2, self.verbose)

    def post_process_cli_args(self):
      """
      Post-processing of CLI args
      """

      # post-processing
      if self.interactive:
        self.skip_listing = False
        dbgln(f"Force skip_listing={self.skip_listing}, due to interactive", 1, self.verbose)

    def parse_args(self, args=None):
      parser = ArgumentParser(description="Send file[s] to RecycleBin_or_Trash")
      parser.add_argument("-v", dest="verbose", action="count",
                          help="Print deleted files, vvv makes it verbosity=3 and so on")
      parser.add_argument('--verbose', type=int, default=0, dest="verbose",
                          help="Enable verbosity by specifying a number")
      parser.add_argument("-nl", "--no-list", dest="skip_listing", action="store_true",
                          help="Do not `ls -l` that file.")
      parser.add_argument("-s", "--separator", dest="separator", action="store_true",
                          help="Add an extra line separator after rbt'ing. ")
      parser.add_argument("-i", "--interactive", dest="interactive", action="store_true",
                          help="ask and then recycle/trash")
      parsed, self.args = parser.parse_known_args()

      self.parser = parser
      self.populate_cli_args(parsed)
      self.post_process_cli_args()

    def remove(self, fn:str, verbose:int = 0):
      from basern.rnutils import adjust_winpath
      if verbose > 0:
        print(f" pre-adjust=[{fn}]", end = '')
      fn = adjust_winpath(fn)
      if verbose > 0:
        print(f", adjusted=[{fn}]")
      if not is_exists(fn):
        if fn.startswith("-"):
          print(f"filename that startswith dash({arg}), not supported")
          rbt.parser.print_help()
        else:
          sys.stderr.write(f" File \"{fn}\" does not exist?\n")
        return False
      do_remove: bool = True
      if not self.skip_listing:
        self.do_list(fn, self.verbose)
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
        if self.verbose >= 2:
          traceback.print_exception(e)
        return False
      
      return True
    
    def show_success(self, fn):
      if self.mtag == "MacOS":
        print(f"Trashed \"{fn}\"")
      elif self.mtag == "PC":
        print(f"Sent {fn} to \"Recycle Bin\"")
      else: 
        print(f"rbt'd {fn} for mtag={self.mtag} - NOT SUPPORTED")
      if self.separator:
         print(f"")  


if __name__ == "__main__":    
  rbt = Rbt()

  rbt.parse_args()
  dbgln(f"Files = [{rbt.args}]\n", 1, rbt.verbose)
  for i, arg in enumerate(rbt.args):
    if rbt.remove(arg, rbt.verbose):
      rbt.show_success(arg)
    if (len(rbt.args) - i) > 1:
      print(f"")
