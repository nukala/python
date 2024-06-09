#!/usr/bin/env python3
# coding: utf-8

###############################################################################
# WIP - due to mmap 
###############################################################################

from argparse import ArgumentParser
from glob import glob  

import sys
import hashlib
import mmap

class md5:

  def __init__(self):
    self.BLOCK_SZ = 8192

  def process(self, fname):
    hasher = hashlib.md5()
    with open(fname, "rb") as ff:
      hunk = ff.read(self.BLOCK_SZ)
      while len(hunk) > 0:
        hasher.update(hunk)
        hunk = ff.read(self.BLOCK_SZ)
	
      self.theHash = hasher.hexdigest()
      self.fname = fname

  # TODO: work in progress, there is a permission error while mapping
  def processMmap(self, fname):
    hasher = hashlib.md5()
    with open(fname, "rb") as ff:
      mm = mmap.mmap(ff.fileno(), 0)
      hunk = mm.read(self.BLOCK_SZ)
      while len(hunk) > 0:
        hasher.update(hunk)
        hunk = mm.read(self.BLOCK_SZ)
	
      self.theHash = hasher.hexdigest()
      self.fname = fname

  def processInline(self, fname):
    with open(fname, "rb") as ff:
      digest = hashlib.file_digest(ff, "md5")
    
    self.theHash = digest.hexdigest()
    self.fname = fname

  def parse_args(self, args=None):
    parser = ArgumentParser(prog = 'md5',
                            description="To generate md5 sum of specified files.")
    parser.add_argument('-v', '--verbose', action='store_true', default = False, dest = "verbose", 
                        help="Enable verbosity")
    parser.add_argument('-s', '--short', action='store_true', default = False, dest = "short",
            help="Short output, no filename")
    parser.add_argument('--memmap', "--memory_map", action='store_true', default = False, 
                        dest = "use_mmap", help="Use memory mapped files. DOES NOT WORK")
    parser.add_argument('--hashlib', "--use_hashlib", action='store_true', default = False, 
                        dest = "use_hashlib", help="Use slower hashlib based operations")
    parser.add_argument("-f", "--files", nargs='*', dest="files", help="names of files to md5 summed")

    self.parsed = parser.parse_args(args)

    file_names=[]
    for f in self.parsed.files:
      file_names += glob(f)
    self.file_names = file_names


  def __str__(self):
    return f"{self.theHash}  {self.fname}"


###### end of md5 class

if __name__ == "__main__":
  msum = md5()
  # msum.parse_args()

  # preparation to help measure time spent
  # if msum.parsed.use_hashlib:
  #   msum.process()
  # elif msum.parsed.use_mmap:
  #   msum.processMmap()
  # else: 
  #   msum.processInline()

  for i in range(1):
    msum.processInline(sys.argv[1])
    print(f"{msum}")
