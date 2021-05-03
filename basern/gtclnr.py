#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from gtpull import *


class gtclnr:
  logf = None
  def __init__(self, logf = None):
    self.root = get_gitroot()   
    self.pre_clean = 0
    self.post_clean = 0
    #print(f"ctor logf={self.logf}, type={type(self.logf)}")

  def git_gc_prune(self, logf = None, num_days = 21):
    """
    Performs - git gc --prune={num_days}.days.ago --no-quiet
    """
    tee_log(logf, '  >>> starting GC (slow)')

    stat = do_run(['git', 'gc', '--no-quiet', '--aggressive', f'--prune={num_days}.days.ago'], logf,
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


  # git repack "${gtOpt}" -a -d --depth=250 --window=250
  # echo " >>> repacking and pruning "; git repack "${gtOpt}" -ad; git prune-packed
  def git_repack(self, logf = None):
    """
    Performs repack -ad hence automatically run prune-packed
    """
    tee_log(logf, '  >>> zip & prune')
    stat = do_run(['git', 'repack', '-a', '-d', '--depth=250', '--window=250'],
                  logf, show_cmd = False, show_result = True)

    return stat.returncode
  
  def git_fetch_prune(self, logf = None):
    """
    Performs - git fetch prune verbose --prune-tags removed
    git fetch --prune --prune-tags --auto-gc
    """
    stat = do_run(['git', 'fetch', '--prune', '--prune-tags', '--auto-gc'], logf, show_cmd = False, show_result = True)
    #tee_log(logf, '\n')

    return stat.returncode


  def shallow_clean(self, logf = None):
    result = 1

    if self.pre_clean == 0:
      self.pre_clean = self.get_gitroot_size(logf = logf)
    result = self.git_prune_remote_origin(logf = logf)
    result = self.git_fetch_prune(logf = logf)

    return result

  # missing cli-commands:
  # gtOpt=-q
  # git clean
  # git branch --merged | grep -v -e \\* -e develop -e trunk -e master | xargs -n 1 git branch -dv
  #
  def deep_clean(self, logf = None, num_days = 21):
    result = 1

    # dont send logf, long-lived task has no feedback
    stat = do_run(['time', 'gtclean'], None, show_cmd = False, show_result = True)
    result = stat.returncode
    
    if result != 0:
      tee_log(logf, "")
      result = self.git_gc_prune(logf = logf, num_days = num_days)
      result = self.git_repack(logf = logf)
    self.post_clean = self.get_gitroot_size(logf = logf)
    tee_log(logf, f"post-clean size={self.post_clean} KB")

    return result

  def show_savings(self, logf = None):
    if self.pre_clean > 0 and self.post_clean > 0:
      sv = self.pre_clean - self.post_clean
      pct = (sv * 100.0) / self.pre_clean
      tee_log(logf, f"Cleaning saved {pct:.2f}% or {sv}/{self.pre_clean} KB.")

  def get_gitroot_size(self, logf = None):
    duks = getoutput_from_run(['du', '-ks', f'{self.root}'], logf, show_result = False)
    result = int(duks['stdout'].split()[0])
    return result

  def show_preclean_size(self, logf = None):
    if self.pre_clean == 0:
      self.pre_clean = self.get_gitroot_size(logf = logf)
    tee_log(logf, f"pre-clean size={self.pre_clean} KB")


# end of gtclnr

def main():
  clnr = gtclnr()

  clnr.show_preclean_size()
  clnr.shallow_clean()
  clnr.deep_clean()
  clnr.show_savings()

if __name__ == "__main__":
  sys.exit(main())
