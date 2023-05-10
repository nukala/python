#!/usr/bin/env python3
# coding: utf-8

from rnutils import *

import datetime
import os
import sys
import time
import yesno

class GoFmt:
  def __init__(self):
    self.dir = os.path.basename(get_pwd())

  def __str__(self):
    return f"{prog}: folder={self.dir}"

  def do_fmt(self, oldval, newval):
    cmd = f"""gofmt -w -r '"{oldval}" -> "{newval}"' ."""
    m = getoutput_from_run(cmd, logf, show_result = True)
    return m

  def bzl(self, cmds, message):
    m = getoutput_from_run(cmds, logf, show_cmd = True, show_output = True, show_result = True, show_error = True)
    if m['returncode'] != 0:
      write_log(logf, f"{message} failed={m['returncode']}")
      sys.exit(1)
    
    return m
    
  # --explain requires a file-name
  # WARNING: --verbose_explanations has no effect when --explain=<file> is not enabled
  def bld(self):
    tee_log(logf, "Starting build")
    cmds = [ 'bazel', 'build', "--show_result", "5", "--worker_verbose", "--verbose_failures", "..." ]
    return self.bzl(cmds, "Initial bazel build")

  def tst(self):
    tee_log(logf, "Starting test")
    # bazel test --verbose_test_summary --nocache_test_results --allow_analysis_failures --build --show_progress --worker_verbose --announce --keep_going --logging=6 --show_timestamps --test_keep_going --test_output=streamed
    cmds = [ "bazel", "test",
"--allow_analysis_failures",
"--build",
"--keep_going",
"--logging", "6",
"--nocache_test_results",
"--show_progress",
"--show_result", "5",
"--show_timestamps",
"--test_keep_going",
"--test_output=streamed",
"--test_summary=detailed",
"--test_verbose_timeout_warnings",
"--verbose_failures",
"--worker_verbose",
"..." ]
    return self.bzl(cmds, "Initial test")

  # only gazelle 
  def gzl(self, lognm = None):
    tee_log(logf, "Starting gazelle")
    glogf = logf
    if lognm != None:
       glogf = open(get_next_logname(lognm), "w")
    m = getoutput_from_run("gazelle", logf, show_cmd = True, show_result = True, show_output = True, show_error = True)
    if m['returncode'] != 0:
      print(f"gazelle failed={m['returncode']}")
      sys.exit(1)

    return m

  # only setup-gopath
  def sg(self, lognm = None):
    tee_log(logf, "Starting setup-gopath")
    sglogf = logf
    if lognm != None:
      sglogf = open(get_next_logname(lognm), "w")

    m = getoutput_from_run("setup-gopath ...", logf, show_cmd = True, show_result = True, show_output = True, show_error = True)
    if m['returncode'] != 0:
      print(f"setup_gopath failed={m['returncode']}")
      sys.exit(1)

    return m


  # to tie both peices - gzl and sg
  def gzlsg(self):
    m = self.gzl()

    if yesno.yes_no('gazelle done, proceed to setup-gopath ? ') == 0:
      m = self.sg()

    return m['returncode']

  # all known renames for flipr effort
  def do_gofmts(self):
    pfx = "code.uber.internal"
    self.do_fmt(f"{pfx}/go-common.git/client/flipr", f"{pfx}/rt/flipr-client-go.git/flipr")
    self.do_fmt(f"{pfx}/go/fliprfx.git", f"{pfx}/rt/flipr-client-go.git/fliprfx")
    self.do_fmt(f"{pfx}/go-common.git/client/flipr", f"{pfx}/rt/flipr-client-go.git/flipr")
    self.do_fmt(f"{pfx}/go-common.git/client/flipr/test", f"{pfx}/rt/flipr-client-go.git/test")
    self.do_fmt(f"{pfx}/go-common.git/client/flipr/gen-go/flipr", f"{pfx}/rt/flipr-client-go.git/gen-go/flipr")
    self.do_fmt(f"mock/{pfx}/go-common.git/client/flipr/fliprmock", f"mock/{pfx}/rt/flipr-client-go.git/flipr/fliprmock")

### End of GoFmt class






#######
# 
# @__priv__

def mk_zip(zipfn):
  zipfn = f"{befsub(logf.name)}.zip"
  #cmd = f"zip -9r {zipfn} $(git status -s | grep ' M' | awk ' { print \\\$2 } ')"
  print(f"{zipfn}")
  #do_run(cmd, logf, show_cmd = True, show_result = True)


start = time.time();
prog = get_prog(__file__)
logf = open(get_next_logname(prog), "w")

if __name__ == "__main__":
  gf = GoFmt()

#  gf.bld()
#  gf.tst()
#  gf.gzlsg()

  gf.do_gofmts()

  gf.gzl()
  gf.sg()

  mod_ctr = get_num_modifications(logf)


  print(f"There are {mod_ctr} changes {elapsed_seconds(start)}")
