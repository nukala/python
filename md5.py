#!/usr/bin/env python3
# coding: utf-8

###############################################################################
# WIP - due to mmap
#     - yucky way in which files are passed.
#        illegal arguments like -xxx are now considered files and then no help
#     - add option to ls -ltr also 
#        l ~/desktop/jan31-wu2axis-p1,2.pdf /mnt/c/download/cloud/OneDrive/trip/jan31-wu2axis-p1,2.pdf /mnt/c/download/cloud/Dropbox/trip/jan31-wu2axis-p1,2.pdf /mnt/c/Users/ravi/Box/trip/jan31-wu2axis-p1,2.pdf | sed 's/-[rwx].*None //g'; check numeric and print all elems after?. VERIFY ON mac
###############################################################################

from argparse import ArgumentParser

import hashlib
import mmap
import os
import platform

class Md5:

  def __init__(self):
    self.BLOCK_SZ = 8192
    self.parsed = None
    self.unknown_args = None

  def process_block(self, fname):
    hasher = hashlib.md5()
    with open(fname, "rb") as ff:
      hunk = ff.read(self.BLOCK_SZ)
      while len(hunk) > 0:
        hasher.update(hunk)
        hunk = ff.read(self.BLOCK_SZ)

    return hasher.hexdigest()

  # TODO: work in progress, there is a permission error while mapping
  def process_mmap(self, fname):
    hasher = hashlib.md5()
    with open(fname, "rb") as ff:
      mm = mmap.mmap(ff.fileno(), 0)
      hunk = mm.read(self.BLOCK_SZ)
      while len(hunk) > 0:
        hasher.update(hunk)
        hunk = mm.read(self.BLOCK_SZ)

    return hasher.hexdigest()

  def process_inline(self, file_name: str, verbose: int = 0):
    if verbose > 0:
      print(f"inline: Input filename=[{file_name}]")
    adjusted = file_name
    if platform.system() == 'Windows':
      from basern.rnutils import adjust_winpath
      adjusted = adjust_winpath(file_name, verbose)

    if not os.path.exists(adjusted):
      print(f"No such file \"{adjusted}\" \n")
      return

    with open(adjusted, "rb") as ff:
      digest = hashlib.file_digest(ff, "md5")

    return digest.hexdigest()

  def parse_args(self, args=None):
    parser = ArgumentParser(prog = 'md5',
                            description="To generate md5 sum of specified files in a platform agnostic way.")
    parser.add_argument('-v', '--verbose', action = 'count', default = 0, dest = "verbose",
                        help = "Enable verbosity")
    parser.add_argument('-s', '--short', action='store_true', default = False, dest = "short",
            help="Short output, no filename, no CRLF or LF")
    parser.add_argument("-nl", "--new_line", action="store_true", dest="newline",
                        help="terminate with a new line")
    parser.add_argument('--mmap', "--memory_map", action='store_true', default = False,
                        dest = "use_mmap", help="Use memory mapped files. DOES NOT WORK")
    parser.add_argument('--block', "--use_block", action='store_true', default = False,
                        dest = "use_block", help="Use slower hashlib based operations")

    self.parsed, self.unknown_args = parser.parse_known_args(args)

    if self.parsed.short and len(self.unknown_args) > 1:
      raise Exception(f"Short={self.parsed.short} and unknown_args{self.unknown_args}"
                      f".len={len(self.unknown_args)} are not compatible"
                      f"\nONLY one file_name is allowed!")


###### end of md5 class

if __name__ == "__main__":
  # fname = sys.argv[1]
  msum = Md5()

  msum.parse_args()

  # preparation to help measure time spent
  for fname in msum.unknown_args:
    the_hash = 'unknown'
    try:
      if msum.parsed.use_block:
        the_hash = msum.process_block(fname)
      elif msum.parsed.use_mmap:
        the_hash = msum.process_mmap(fname)
      else:
        the_hash = msum.process_inline(fname, msum.parsed.verbose)

      end=""
      if msum.parsed.newline:
        end="\n"
      if msum.parsed.short:
        print(f"{the_hash}", end=f"{end}")
      else:
        print(f"{the_hash}\t{fname}")
    except (OSError, PermissionError) as e:
      print(f"{e}\n")
      if msum.parsed.verbose > 1:
        import traceback
        traceback.print_exc()
      print("\n")
      pass
