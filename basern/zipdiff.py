#!/usr/bin/env python3
# coding: utf-8


from rnutils import *

import os
import zipfile
import datetime
import time



class ZipDiff:

  def __init__(self, zipfn, prefix):
    self.zipfn = zipfn.replace(os.environ['HOME'], '~')
    self.prefix = prefix
    self.basefn = os.path.basename(zipfn)
    zf = zipfile.ZipFile(zipfn)
    self.infos = {}
    for zi in zf.infolist():
      if zi.is_dir(): 
        continue
	
      self.infos[zi.filename] = { 'crc': zi.CRC, 'size': zi.file_size,
				  'filename': zi.filename,
                                  'modified': f"{datetime.datetime(*zi.date_time)}" }

    zf.close()

  def get_info(self, fn):
    try:
      return self.infos[fn]
    except KeyError:
      #return { 'crc': 0, 'size': 0, 'filename' : fn, 'modified' : datetime.datetime.now() }
      return { 'crc': -1, 'size': -1, 'filename' : fn, 'modified' : f'NON EXISTANT({self.basefn})' }


  def __str__(self):
    return f"{self.prefix} {self.zipfn} has {len(self.infos)} items "

  def do_print(self, key):
    zi = self.get_info(key)
    return f" {self.prefix} {zi['size']}   {zi['modified']}  {os.linesep}"

  def all_infos(self):
    return self.infos;

#########
##

prog = get_prog(__file__)
start = time.time()

def show_diffs(lfname, rfname): 
  lzd = ZipDiff(lfname, "<<<< ")
  rzd = ZipDiff(rfname, ">>>> ")
  print(f"{lzd} {rzd}")

  # merge two maps most accurately and idiomatically only in 3.5+
  all_fns = { **lzd.all_infos(), **rzd.all_infos() }
  num_diffs = 0
  for fn in all_fns:
    li = lzd.get_info(fn)
    ri = rzd.get_info(fn)

    #print(f"checking {fn} r-crc={ri['crc']} lcrc={li['crc']}")
    if ri['crc'] != li['crc']:
      print(f"{fn}{os.linesep} {rzd.do_print(fn)} {lzd.do_print(fn)}")
      num_diffs += 1

  return num_diffs


############
# Compare contents of two zip files, look at CRC, date_time stamps and show 
#  diffs in a more readable fashion
#


if __name__ == "__main__":
  if len(sys.argv) != 3:
    print(f"Compares differences inside TWO zip files.")
    print(f"exactly TWO parameters are REQUIRED")
    sys.exit(1)

  log_started_message(None, prog = prog)
  num_diffs = show_diffs(sys.argv[1], sys.argv[2])
  print(f"Found {num_diffs} differences in {elapsed_seconds(start)}")
  #done
