#!/usr/bin/env python3
# coding: utf-8

###############################################################################
# WIP - due to mmap
#     - yucky way in which files are passed.
#        illegal arguments like -xxx are now considered files and then no help
###############################################################################

from argparse import ArgumentParser
from glob import glob  

import sys
import hashlib
import mmap

class md5:

  def __init__(self):
    self.BLOCK_SZ = 8192

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

  def process_inline(self, fname):
    with open(fname, "rb") as ff:
      digest = hashlib.file_digest(ff, "md5")
    
    return digest.hexdigest()
  
  def parse_args(self, args=None):
    parser = ArgumentParser(prog = 'md5',
                            description="To generate md5 sum of specified files in a platform agnostic way.")
    parser.add_argument('-v', '--verbose', action='store_true', default = False, dest = "verbose", 
                        help="Enable verbosity")
    parser.add_argument('-s', '--short', action='store_true', default = False, dest = "short",
            help="Short output, no filename")
    parser.add_argument('--mmap', "--memory_map", action='store_true', default = False, 
                        dest = "use_mmap", help="Use memory mapped files. DOES NOT WORK")
    parser.add_argument('--block', "--use_block", action='store_true', default = False, 
                        dest = "use_block", help="Use slower hashlib based operations")

    self.parsed, self.unknown_args = parser.parse_known_args(args)

    if self.parsed.short and len(self.unknown_args) > 0:
      raise Exception(f"Short={self.parsed.short} and unknown_args{self.unknown_args}"
                      ", len={len(self.unknown_args)} are not compatible")


###### end of md5 class

if __name__ == "__main__":
  # fname = sys.argv[1]
  msum = md5()

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
        the_hash = msum.process_inline(fname) 

      if (msum.parsed.short):
        print(f"{the_hash}")
      else:
        print(f"{the_hash}\t{fname}")
    except (OSError, PermissionError) as e:
      print(f"{e}")
      pass;
