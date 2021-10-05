#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from yesno import *
from os import *

"""
Given a hardcoded other dir, compares all files in this folder (not using MF) to the other_dir 
 if sums match, interactively cleans up here
"""

class mflstr:
  def __init__ (self) :
    self.non_exist = 0
    self.no_match = 0
    self.logf = None
    #int(duks['stdout'].split()[0])
    self.pre_clean = duks(".", self.logf)
    here = get_pwd(False)
    print(f"here={here}")
    sfx = here.split('books\\')[1]
    print(f"sfx=[{sfx}]")
    self.oth_dir = "C:/filre/books/" + sfx.replace("\\", "/")
    self.post_clean = 0
    print(f"here={here}, other={self.oth_dir}")

  def done(self) :
    if self.post_clean == 0:
      self.post_clean = duks(".", self.logf)
    print(f"missing={self.non_exist}, unmatched={self.no_match}")
    print(f"pre  {self.pre_clean} KB")
    print(f"post {self.post_clean} KB")
    saved =  self.pre_clean - self.post_clean
    if saved > 0:
      print(f"saved {saved} KB")

  #
  # TODO: write search from m5 and replace mfmp.sh
  #
  def search_md5_wip(self, fn):
    cmd = ['grep']
    parts = fn.replace(".pdf", "").replace("-", "").split()
    for (i, p) in enumerate(parts):
      cmd.append('-i')
      cmd.append(parts[i])
    cmd.append('C:/filre/books.md5')
    #cmd.append('|')
    #cmd.append('sort')
    print(f"{cmd}")
    do_run(cmd, self.logf, show_cmd = True, show_result = True)
    return 1

  def run(self, fn = "Java™ Idioms.pdf"):
    othfn = f"{self.oth_dir}/{fn}"
    if os.path.exists(othfn) != True:
      #print(f"Other file={othfn} does not exist\n")
      self.non_exist = self.non_exist + 1
      #search_md5_wip(fn)
      return 1

    stat = getoutput_from_run(['md5sum', othfn, fn], self.logf, show_cmd = False, show_output = False, show_result = False)
    out = stat['stdout'].split('\n')
    if len(out) != 2:
      print(f"{out}")
      print(f"Unexpected number of sums={len(out)}, leaving alone")
      return 1

    md_sep = ' *'
    sum0 = out[0].split(md_sep)[0]
    sum1 = out[1].split(md_sep)[0]
    #print(f"sum0={sum0}\nsum1={sum1} {sum0 == sum1}")

    if sum0 == sum1:
      print(f"sums match\n\t{out[0]}\n\t{out[1]}")
      stat = do_run(['rm', '-i', f"./{fn}"], self.logf)
      print("")
      return stat.returncode
    else:
      self.no_match = self.no_match + 1
      print(f"Sums mismatch ({sum0} != {sum1})\n  >>>{fn}<<<\n")
      do_run(['ls', '-ltrd', fn, othfn], self.logf, show_result = 0)
      here_size = os.path.getsize(fn)
      oth_size = os.path.getsize(othfn)
      if here_size < oth_size:
        do_run(['rm', '-i', fn], self.logf, show_result = 0)

    #for i, s in enumerate(out):
    #  ary = s.split(' *')
    #  print(f"len={len(ary)}")
    #  print(f"sum=[{ary[0]}], file=[{ary[1]}]")
    return 1

def list_files(dir, logf) :
  files = []
  for (path, dirname, fns) in walk(dir):
    files.extend(fns)

  return files

def main() :
  lstr = mflstr()

  dir = "."

  try:
    #lstr.run()
    fils = list_files(dir, lstr.logf)
    for (i, fil) in enumerate(fils):
      #print(f"{fil}")
      lstr.run(fil)
  except KeyboardInterrupt:
    print("")
  lstr.done()

  # does not work : resource in use
  #if len(list_files(dir, lstr.logf)) == 0:
#    here = get_pwd(False)
#    bsnm = os.path.basename(here)
#    do_run(['rm', '-ri', f"../{bsnm}"], lstr.logf)

if __name__ == "__main__" :
  sys.exit(main())
