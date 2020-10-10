#!/usr/bin/env python3
# coding: utf-8

#################################################
# My attempt to see if real-time feedback is possible.
#
# As of Jun10 - NO 
#################################################
from rnutils import *

import datetime
import os
import sys
import time
import yesno

class BzlProc:
  def __init__(self):
    self.dir = os.path.basename(get_pwd())

  def __str__(self):
    return f"{prog}: folder={self.dir}"

  def bzl(self, cmds, message):
    m = getoutput_from_run(cmds, logf, show_cmd = True, show_output = True, show_result = True, show_error = True)
    if m['returncode'] != 0:
      write_log(logf, f"{message} failed={m['returncode']}")
      sys.exit(1)
    
    return m
    
  def tst(self):
    tee_log(logf, "---=== Starting test ===---")
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

### End of BzlProc class






#######
# 
# @__priv__


start = time.time();
prog = get_prog(__file__)
logf = open(get_next_logname(prog), "w")

if __name__ == "__main__":
  bp = BzlProc()

  bp.bzl("./tst", 'wrapper script')
