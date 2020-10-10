#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from yesno import yes_no
from yesno import bool_yesno

import datetime
import os
import sys
import time
import subprocess

import mtime


def get_tmp_dir(subdir = None):
  dir = os.environ['HOME'] + os.sep + 'tmp'
  if subdir is not None:
    dir += os.sep + subdir

  os.makedirs(dir, exist_ok = True)
  return dir

def git_gc_prune(logf, num_days = 21):
  """
  Performs git gc --prune=now
  git gc --prune=21.days.ago --no-quiet
  """
  stat = do_run(['git', 'gc', '--no-quiet', f'--prune={num_days}.days.ago'], logf,
                show_cmd = True, show_result = True)
  tee_log(logf, '\n')

  return stat.returncode

#           git gc --prune=now; git remote prune origin

def git_prune_remote_origin(logf):
  """
  Performs - git remote prune origin
  """
  stat = do_run(['git', 'remote', 'prune', 'origin'], logf, show_cmd = True, show_result = True)
  tee_log(logf, '\n')

  return stat.returncode


def git_fetch_prune(logf):
  """
  Performs git fetch prune verbose --prune-tags removed
  """
  stat = do_run(['git', 'fetch', '--prune', '--verbose'], logf, show_cmd = True, show_result = True)
  tee_log(logf, '\n')

  return stat.returncode


def do_git_pull(logf):
  """
  Performs git pull
  If successful, asks and cleans up the logfile
  """
  #https://blog.sffc.xyz/post/185195398930/why-you-should-use-git-pull-ff-only
  stat = do_run(['git', 'pull', '--no-commit', '--ff-only'], logf, show_result = False)
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

  return stat.returncode

# echo "[$(l -s ~/tmp/git/gtpull-05190229.log | awk ' { print $1 } ')]" then
#    > grep 'files changed' ~/tmp/git/gtpull-05190229.log

def after_tasks(logf, idxTs, objTs):
  oldest = min(idxTs, objTs)
  wkago = datetime.datetime.now() - datetime.timedelta(days=7)
  if (oldest < wkago.timestamp()) :
    tee_log(logf, f"\noldest={datetime.datetime.fromtimestamp(oldest)} && wkago={wkago}")
    stat = ask_then_run(['time', 'gtclean'], logf, show_result = True)
  else:
    tee_log(logf, f"oldest={datetime.datetime.fromtimestamp(oldest)} is NEWER-THAN wkago={wkago}")

  write_log(logf, 'gtclean and others')
  result = 1
  if bool_yesno(f'\nShallow cleanup (y/n) [n]? '):
    result = git_gc_prune(logf, num_days = 7)
    result = git_prune_remote_origin(logf)
    result = git_fetch_prune(logf)
    
    if bool_yesno('deep clean (y/n) [n]? '):
      stat = do_run(['time', 'gtclean'], None, show_result = True)
      result = stat.returncode

  return result


def show_gitlast_changes(root, logf = None):
  m = getoutput_from_run(['ls', '-ltrd', git_path(root, 'index'), git_path(root, 'objects')],
                         logf, show_result = False)
  return m['stdout']

def git_path(root, path):
  return root + os.sep + path

def main():
  lf = get_long_filename(prog)
  log = get_tmp_dir("git") + os.sep + get_long_filename(prog)
  logf = open(log, "w")
  log_started_message(logf, prog)
  write_log(logf, f"{prog}: {get_pwd()}")

  root = get_gitroot(None)
  last_changes = show_gitlast_changes(root, logf)
  tee_log(logf, last_changes)

  idxTs = mtime.modification_timestamp('.git/index')
  objTs = mtime.modification_timestamp('.git/objects')

  ret = do_git_pull(logf)
  if ret == 0:
     # only upon success!
    after_tasks(logf, idxTs, objTs)
  logf.close()
  if yes_no(f'remove {logf.name} (y/n): ') == 0:
    os.remove(logf.name)

  return ret


######################################################################
# TODO:  so=2998832 talks about:
#           git fetch --prune; git fetch --all; git pull
# TODO argparse; then add --less-log option to force show log, then remove upon success
######################################################################
start = time.time()
prog = get_prog(__file__)

if __name__ == "__main__":
  sys.exit(main())
