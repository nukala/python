#!/usr/bin/env python3
# coding: utf-8

from rnutils import *
from yesno import *
from gtpull import *


class gtcln:
  def __init__(self):
    self.root = get_gitroot()   

# end of gtcln

def main():
  gc = gtcln()

if __name__ == "__main__":
  sys.exit(main())
