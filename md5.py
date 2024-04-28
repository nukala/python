#!/usr/bin/env python3
# coding: utf-8

###############################################################################
# WIP 
###############################################################################

import sys
import hashlib
import mmap

class md5:

  def __init__(self, fname):
    self.fname = fname
    self.hasher = hashlib.md5()

  def process(self):
    with open(self.fname, "rb") as ff:
      hunk = ff.read(8192)
      while len(hunk) > 0:
        self.hasher.update(hunk)
        hunk = ff.read(8192)
	
      self.theHash = self.hasher.hexdigest()

  # TODO: work in progress, there is a permission error while mapping
  def processMmap(self):
    with open(self.fname, "rb") as ff:
      mm = mmap.mmap(ff.fileno(), 0)
      hunk = mm.read(8192)
      while len(hunk) > 0:
        self.hasher.update(hunk)
        hunk = mm.read(8192)
	
      self.theHash = self.hasher.hexdigest()
      

  def __str__(self):
    return f"{self.theHash}  {self.fname}"


###### end of md5 class

if __name__ == "__main__":
  fname = sys.argv[1]
  m5 = md5(fname)
  m5.process()
  #print(f"{hasher.get_hash(fname)}  {fname}")
  print(f"{m5}")
