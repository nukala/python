#!/usr/bin/env python3
# coding: utf-8

import datetime
import os
import pyclip as pc
import sys
import uuid


############################################################################
# Look up from new-relic using UUIDs with and without dashes.
# Used extensively during one of my jobs as there was a lot of confusion
#  around UUID formatting in logs/NR/Sumo etc
#
# todos in this file
#  send_to_clipboard and get_from_clip helper
#  choose betweem sm and nr
############################################################################

@staticmethod
def copy_to_clipboard(some_string, debug=False, verbose=False):
  """
  " Copies the specified some_string into clipboard in a OS independent fashion
  """
  pc.copy(some_string)

class ToUUID:

  def __init__(self, arg):
    self.uuid = uuid.UUID(arg)
    self.dashed = str(self.uuid)
    self.cleaned = arg.replace("-", "")

  def with_dashes(self):
    return self.dashed

  def no_dashes(self):
    return self.cleaned

if __name__ == "__main__":
  tu = ToUUID(sys.argv[1])
  print(f"_sourceCategory=prod/core/* ( {tu.with_dashes()} OR {tu.no_dashes()} ) ")
  print(f"\n")
  #print(f"SELECT * from Log\nWHERE (dimensions() like '%{tu.no_dashes()}' \nOR dimensions() like '%{tu.with_dashes()} \n -- OR dimensions() like '%xyz%')")

  dd = datetime.date.today()
  mon = f"{dd.month}".zfill(2)
  day = f"{dd.day}".zfill(2)
  s = f"""
SELECT * from Log
WHERE ( 
dimensions() like '%{tu.no_dashes()}%' 
OR dimensions() like '%{tu.with_dashes()}%'
-- OR dimensions() like '%xyz%'
)
-- since \'{dd.year}-{mon}-dd\' until \'{dd.year}-{mon}-{day}\' 
  """

  print(f"{s}")
  tu.copy_to_clipboard(s)

