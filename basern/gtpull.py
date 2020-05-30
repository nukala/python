#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from yesno import yes_no

import os
import sys
import time
import subprocess


def get_tmp_dir(subdir = None):
  dir = os.environ['HOME'] + os.sep + 'tmp'
  if subdir is not None:
    dir += os.sep + subdir

  os.makedirs(dir, exist_ok = True)
  return dir


def do_git_pull(logf):
  """
  Performs git pull
  If successful, asks and cleans up the logfile
  """
  stat = do_run(['git', 'pull', '--no-commit'], logf, show_result = False)
  tee_log(logf, f"{prog} = {stat.returncode}, elapsed={round(time.time()-start, 2)} seconds")
  #logf.close()

  if stat.returncode != 0:
    #stat = do_run(['more', logf.name], logf, show_result = False, show_output = True)
    subprocess.run(['less', logf.name])
    print(f"see - {logf.name}")
  else:
    print(f"{os.linesep}")
    do_run(['grep', 'file.* changed', logf.name], None, show_result = False)
    do_run(['tail', '-5', logf.name], None, show_cmd = False, show_result = False)
    logf.close()
    if yes_no(f'remove {logf.name} (y/n): ') == 0:
      os.remove(logf.name)

  return stat.returncode

# echo "[$(l -s ~/tmp/git/gtpull-05190229.log | awk ' { print $1 } ')]" then
#    > grep 'files changed' ~/tmp/git/gtpull-05190229.log

def after_tasks():
  stat = ask_then_run(['time', 'gtclean'], None, show_result = True)

def show_gitlast_changes(logf = None):
  m = getoutput_from_run(['ls', '-ltrd', git_path('index'), git_path('objects')], logf, show_result = False)
  return m['stdout']

def git_path(path):
  return root + os.sep + path

def main():
  lf = get_long_filename(prog)
  log = get_tmp_dir("git") + os.sep + get_long_filename(prog)
  logf = open(log, "w")
  log_started_message(logf, prog)
  write_log(logf, f"{prog}: {get_pwd()}")

  last_changes = show_gitlast_changes(logf)
  tee_log(logf, last_changes)

  ret = do_git_pull(logf)
  if ret == 0:
     # only upon success!
     after_tasks()
  return ret


######################################################################
# TODO: add recommended actions from stack=40486, etc
# TODO git remote prune origin if pull fails
# TODO argparse; then add --less-log option to force show log, then remove upon success
######################################################################
start = time.time()
root = get_gitroot(None)
prog = get_prog(__file__)

if __name__ == "__main__":
  sys.exit(main())
