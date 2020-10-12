#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from yesno import *
from gtpull import *


class gtclnr:
  logf = None
  def __init__(self):
    self.root = get_gitroot()   
    #print(f"ctor logf={self.logf}, type={type(self.logf)}")

  def git_gc_prune(self, logf = None, num_days = 21):
    """
    Performs - git gc --prune={num_days}.days.ago --no-quiet
    """
    stat = do_run(['git', 'gc', '--no-quiet', f'--prune={num_days}.days.ago'], logf,
                show_cmd = False, show_result = True)
    #tee_log(logf, '\n')

    return stat.returncode


  def git_prune_remote_origin(self, logf = None):
    """
    Performs - git remote prune origin
    """
    stat = do_run(['git', 'remote', 'prune', 'origin'], logf, show_cmd = False, show_result = True)
    #tee_log(logf, '\n')

    return stat.returncode


  def git_fetch_prune(self, logf = None):
    """
    Performs - git fetch prune verbose --prune-tags removed
    git fetch --prune --prune-tags --auto-gc
    """
    stat = do_run(['git', 'fetch', '--prune', '--prune-tags', '--auto-gc'], logf, show_cmd = False, show_result = True)
    #tee_log(logf, '\n')

    return stat.returncode


  def shallow_clean(self, logf = None, num_days = 21):
    result = 0

    if bool_yesno(f'\nShallow cleanup (y/n) [n]? '):
      result = self.git_gc_prune(logf = logf, num_days = num_days)
      result = self.git_prune_remote_origin(logf = logf)
      result = self.git_fetch_prune(logf = logf)

    return result

  def deep_clean(self, logf = None):
    result = 0
    if bool_yesno('\ndeep clean (y/n) [n]? '):
      # dont send logf, long-lived task has no feedback
      stat = do_run(['time', 'gtclean'], None, show_cmd = False, show_result = True)
      result = stat.returncode

    return result



# end of gtclnr

def main():
  clnr = gtclnr()

  clnr.shallow_clean()
  clnr.deep_clean()

if __name__ == "__main__":
  sys.exit(main())
