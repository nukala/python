#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from yesno import yes_no
from yesno import bool_yesno

import datetime
import os
import sys
import getopt
import time
import subprocess

import mtime
import gtclnr


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
  #https://blog.sffc.xyz/post/185195398930/why-you-should-use-git-pull-ff-only
  stat = do_run(['git', 'pull', '--no-commit', '--ff-only'], logf, show_result = False)
  tee_log(logf, f"{prog} = {stat.returncode}, elapsed={round(time.time()-start, 2)} seconds", do_print = False)
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

def after_tasks(logf, idxTs, objTs, root): 
  if do_clean == False:
    #print(f"{prog}: after_tasks - returning because flag={do_clean}")
    return

  oldest = min(idxTs, objTs)
  wkago = datetime.datetime.now() - datetime.timedelta(days=7)
  result = 0
  # oldest < wkago.timestamp()
  if (oldest < wkago.timestamp()) :
    tee_log(logf, f"\noldest={datetime.datetime.fromtimestamp(oldest)} && wkago={wkago}")

    clnr = gtclnr.gtclnr(logf)
    clnr.show_preclean_size(logf)
    if (clnr.shallow_clean(logf) == 0) :
      clnr.deep_clean(logf)
      clnr.show_savings(logf)
  else:
    tee_log(logf, f"oldest={datetime.datetime.fromtimestamp(oldest)} is NEWER-THAN wkago={wkago}")

  return result


def show_gitlast_changes(root, logf = None):
  lsl = getoutput_from_run(['ls', '-ltrd', git_path(root, 'index'), git_path(root, 'objects')],
                         None, show_output = False, show_result = False)
  return lsl['stdout']


def git_path(root, path):
  return root + os.sep + path

def main(argv):
  global do_clean

  try:
    opts, args = getopt.getopt(argv, "hc", ["clean"])
  except getopt.GetoptError:
    print(f"{prog} -c    -- to run gtclnr ")
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
       print(f"{prog} -n")
       sys.exit()
    elif opt in ('-c', "--c", "--clean"):
      do_clean = True
  
  root = get_gitroot(None)
  if root is None :
    print(f"No git root in {get_pwd()} or its parent folders, failing")
    return 1

  lf = get_long_filename(prog)
  log = get_tmp_dir("git") + os.sep + get_long_filename(prog)
  logf = open(log, "w")
  log_started_message(logf, prog)
  write_log(logf, f"{prog}: {get_pwd()}")

  last_changes = show_gitlast_changes(root, logf)
  tee_log(logf, f"{last_changes}", do_print = False)

  idxTs = mtime.modification_timestamp(git_path(root, 'index'))
  objTs = mtime.modification_timestamp(git_path(root, 'objects'))

  ret = do_git_pull(logf)
  if ret == 0:
     # only upon success!
    after_tasks(logf, idxTs, objTs, root)
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
do_clean = False
prog = get_prog(__file__)

if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
