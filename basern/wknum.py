#!/usr/bin/env python3
# coding: utf-8

import datetime

class DtUtils:
  def __init__(self):
    pass

  def today(self):
    return datetime.date.today()

  def wknum(self):
    return self.today().isocalendar()[1]

  def __str__ (self):
    return f"{self.today()} is weekNumber: {self.wknum()}"


if __name__ == '__main__':
  du = DtUtils()
  print(f"{du}")
  #min=datetime.datetime.today().minute + 5
  #if min > 60:
  #  min = min - 60;
  #print(f"min={min}")
