#!/usr/bin/env python3 
# coding: utf-8 

from rnutils import *
from os import *


"""
To return a shorter version of pwd. 
 if > 3 return 3 dirnames
 if 2 return those two
 else return entire

Works in C\: drive and many other folders.
"""

if __name__ == "__main__" :
  print(f"{short_pwd()}", end='')
