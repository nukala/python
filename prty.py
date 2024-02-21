#!/usr/bin/env python3
# coding: utf-8

import json
import sys
import xml.dom.minidom
from xml.parsers.expat import ExpatError



class Prty:
  def pretty_xml(self, fn, of):
    try:
      with open(fn) as xf:
        obj = xml.dom.minidom.parseString(xf.read())  # or xml.dom.minidom.parseString(xml_string)
    
        if obj is not None:
          xml_pretty_str = xml.toprettyxml(indent = '  ')
          ofn = of + ".xml"
          with open(ofn, 'w') as f:
            f.write(xml_pretty_str)
            f.write("\n")
            return True
    except xml.parsers.expat.ExpatError:
      print(f"Bad XML {fn}")
      return False


  def pretty_json(self, fn, of):
    try:
      with open(fn, 'r') as jf:
        obj = json.load(jf)
  
      if obj is not None:
        ofn = of + ".json"
        with open(ofn, 'w') as f:
          f.write(json.dumps(obj, indent=2))
          f.write("\n")
          return True
    except json.decoder.JSONDecodeError:
      print(f"Not a json {fn}")

    return False


if __name__ == "__main__":
  prty = Prty()

  fn = sys.argv[1]
  of = '/tmp/p'

  if prty.pretty_xml(fn, of) == True:
    print(f"Wrote XML into [{of}.xml]")
  if prty.pretty_json(fn, of) == True:
    print(f"JSON in [{of}.json]")


