#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from domk import *

import os
import subprocess as sp
import sys
import time

def upgrade_toml(lib, libVer, logf = None):
  tomlfn = "Gopkg.toml"
  tomlf = open(tomlfn, "a")

  tee_log(logf, f"updating {tomlfn}")
  tomlf.write(f"{os.linesep}###{os.linesep}")
  tomlf.write(f"[[override]]{os.linesep}")
  tomlf.write(f"  name = \"{lib}\"{os.linesep}")
  tomlf.write(f"  version = \"{libVer}\"{os.linesep}")
  tomlf.close()

  # now show the diffs
  tee_log(logf, f"Changes in {tomlfn}")
  os.system(f"git diff -w {tomlfn}")
  do_run([ "git", "diff", "-w", tomlfn ], logf, inpt = "q")
  #sp.run(, stdout = logf, stderr = logf, text = True, inpt = "q")

  nap = 10
  tee_log(logf, f"Napping for {nap} seconds -- interrupt if needed")
  do_nap(10, logf)

def get_val(k):
  try:
    return vals[k]
  except KeyError:
    return None

#   name = "github.com/gogo/protobuf" version = "=1.2.1"
vals = {
  "scg": { "lib": "code.uber.internal/infra/schemaless-client-go.git", "ver" : "=0.20.0", "msg" : "schemaless-client-go.git" },
  "tmg": { "lib": "code.uber.internal/infra/tenancy-middleware.git", "ver" : "v6.0.0", "msg" : "tenancy middleware" },
  "tcg": { "lib": "code.uber.internal/infra/tenancy-client-go.git", "ver": "v4.2.0", "msg": "tenancy client" },
  "pb" : { "lib": "github.com/gogo/protobuf", "ver": "=1.2.1", "msg": "gogo.Protobuf update is a bit scary. Lookout"},
  "ctf" : { "lib": "code.uber.internal/infra/ctf.git", "ver": "=1.8.5", "msg": "ctf "},
  "yarpc" : { "lib": "go.uber.org/yarpc", "ver": "=1.42.0", "msg": "yarpc update. pls be careful" },
  "jfx" : { "lib": "code.uber.internal/go/jaegerfx.git", "ver": "^1.7.0", "msg": "jaegerfx" },
  "yfx" : { "lib": "code.uber.internal/go/yarpcfx.git", "ver": "=1.26.0", "msg": "yarpcfx, again be cautious" },
  "crbrs" : { "lib": "code.uber.internal/devexp/cerberus.git", "ver": "=1.10.0", "msg": "cerberus version" },
}


def get_next_logf(pfx):
  nextLog = get_mmdd_filename(pfx)
  if (is_exists(nextLog)):
    nextLog = get_long_filename(pfx)

  print(f"next log name={nextLog}")

  if is_exists(nextLog):
    r = os.system(f"ls -ltr {nextLog}")
    print(f"Removing {nextLog} = {r}")
    do_nap(5)
    os.remove(nextLog)

  logf = open(nextLog, "w")
  return logf


#########
# 
# @__priv__

def main():
  start = time.time()
  kk = None
  if len(sys.argv) >= 2:
    kk = sys.argv[1]

  if get_val(kk) is None:
    print(f"key={kk} has not been created yet. Known keys:")
    print(f"     {','.join(vals.keys())}")
    return 1

  logf = get_next_logf(kk)

  # show current status FIRST
  stat = do_run([ "git", "status"], logf, inpt = "q")

  do_nap(10, logf)
  lib = vals[kk]['lib']
  libVer = vals[kk]['ver']
  tee_log(logf, f"Upgrade of {lib}")
  #stat = sp.run([ "./sf"],
  #tee_log(logf, "nap=5"); time.sleep(5)
  stat = do_run([ "./go-build/dep", "ensure", "-update", f"{lib}"], logf)

  if stat.returncode == 0:
    tee_log(logf, f"Raw upgrade of {lib} SUCCESS !!!")
    tee_log(logf, f"no need to modify toml")
  else:
    upgrade_toml(lib, libVer, logf)

    tee_log(logf, f"Upgrading after override in toml")
    stat = sp.run([ "./go-build/dep", "ensure", "-update", f"{lib}"],
             stdout = logf, stderr = logf, text = True, inpt = "0")
    tee_log(logf, "From start to upgrade-after-override consumed {round(time.time() - start,2)}")

    if not stat.returncode == 0:
      tee_log(logf, f"Manual intervention needed for {lib}")
      return 1
    else:
      tee_log(logf, f"Override of {lib}v{libVer} update successful")
  # raw upgrade failed

  # append to environment for verbosity
  targets = [ "bins", "test", "vet", "jenkins"]
  ans = make_targets(targets, logf)

  # wrapping up...
  tee_log(logf, f"[make {ans['target']}] returned={ans['status'].returncode}")
  tee_log(logf, f"Elapsed time {round(time.time() - start, 2)}")
  print(f"Logs written to {logf.name}")
  logf.close()
  return 0



##########
#
if __name__ == "__main__" :
  sys.exit(main())
