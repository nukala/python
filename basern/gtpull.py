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
import argparse

import mtime
import gtclnr


def get_tmp_dir(subdir = None):
  home_dir = os.environ['HOME'] + os.sep + 'tmp'
  if subdir is not None:
    home_dir += os.sep + subdir

  os.makedirs(home_dir, exist_ok = True)
  return home_dir

def fetch_forcibly(logf = None, verbose = False):
  """
  " Fetches tags forcibly
  """
  stat = do_run(["git", "fetch", "--all", "--force", "--multiple", "--tags"]
                , logf, show_result = True, show_cmd = verbose)
  tee_log(logf, f"{prog}: fetch={stat.returncode}, elapsed={round(time.time()-start, 2)} seconds",
         do_print = False)

  return stat.returncode


def do_git_fetch(logf = None, verbose = False):
  """
  " Fetches from the repository, including tags, pruning delegated to clnr
  """
  stat = do_run(['git', 'fetch', '--all', '--tags', '--prune', '--prune-tags' ], logf,
                show_result = True, show_cmd = verbose)
  tee_log(logf, f"{prog}: fetch={stat.returncode}, elapsed={round(time.time()-start, 2)} seconds",
         do_print = False)

  # if failure, ask to run fetch --force manually
  if stat.returncode != 0:
    return fetch_forcibly(logf, verbose)

  return stat.returncode


def do_git_pull(logf):
  """
  Performs git pull
  If successful, asks and cleans up the logfile
  """
  #https://blog.sffc.xyz/post/185195398930/why-you-should-use-git-pull-ff-only
  stat = do_run(['git', 'pull', '--no-commit', '--ff-only'], logf, show_result = False)
  tee_log(logf, f"{prog}: pull={stat.returncode}, elapsed={round(time.time()-start, 2)} seconds", do_print = False)
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

def after_tasks(logf, idxTs, objTs, root, do_clean = False):
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
  #fn = "objects"
  fn = "FETCH_HEAD"
  lsl = getoutput_from_run(['ls', '-ltrd', git_path(root, 'index'), git_path(root, fn)],
                         None, show_output = False, show_result = False)
  return lsl['stdout']


def git_path(root, path):
  return root + os.sep + path


def main(args):
  parser = argparse.ArgumentParser(
              description = "Perform git pull, writes the log and offers to interactively cleanup")
  parser.add_argument("-c", "--clean", "-cln", action = "store_true", dest = "clean"
                      , help = "Perform gtclnr if required.")
  parser.add_argument("-rm", "--rmlog", dest="rmlog", action="store_true"
                      , help = "remove logs from: pull and clean (if-enabled)")
  parser.add_argument("-ll", "--lesslog", action = "store_true", dest="lesslog"
                      , help = "less the_log_file on screen", default = False)
  parser.add_argument("-v", "--verbose", action = "count", default = 0
                      , help = "verbose, supports -vv for more verbose"
                      , dest = "verbose")
  args = parser.parse_args();
  do_clean = args.clean;
  if args.verbose >= 1:
    print(f"{args}")


  logf = None
  tee_log(logf, f"branch = [{get_gitbranch(None)}]")
  root = get_gitroot(None)
  if root is None :
    tee_log(logf, f"No git root in {get_pwd()} or its parent folders, failing")
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
  do_git_fetch(logf, args.verbose)
  ret = do_git_pull(logf)
  if ret == 0:
     # only upon success!
    after_tasks(logf, idxTs, objTs, root, do_clean)
  logf.close()

  if args.lesslog == True:
    do_run(['less', '-G', logf.name], None, show_cmd = False, show_result = False)

  if args.rmlog == True:
    if args.verbose >= 2:
      print(f"  removing logfile={logf.name}")
    os.remove(logf.name)
  elif yes_no(f'remove {logf.name} (y/n): ') == 0:
    os.remove(logf.name)
  else:
    do_run(f"echo {logf.name} | tr -d \"\n\" | pbcopy", None, show_cmd = False, show_result = False)

  return ret


######################################################################
# TODO:  so=2998832 talks about:
#           git fetch --prune --prune-tags; git fetch --all --tags; git pull
# way to cat logs if --rm is enabled:
#  grep -e change -e deletion -e ' | ' /Users/ravinukala/tmp/git/gtpull-03151227.log
#
# TODO: do not remove log upon error
#       branch aware pull
######################################################################
start = time.time()
prog = get_prog(__file__)

if __name__ == "__main__":
  sys.exit(main(sys.argv))
