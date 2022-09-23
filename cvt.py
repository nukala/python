#!/usr/bin/env python3
# coding: utf-8
import os

import pendulum as pdl
import sys

from distutils.util import  strtobool

# pendulum.parse(str)
# pendulum.from_format('Saturday July 23 11:05pm', 'dddd MMMM DD hh:mma')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma zz')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma z')
# pendulum.from_format('Saturday July 23 11:05pm EST', 'dddd MMMM DD hh:mma z')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma z')

class Cvt:
    # https://github.com/sdispater/pendulum/blob/master/docs/docs/string_formatting.md
    # https://github.com/sdispater/pendulum/blob/master/docs/docs/timezones.md
    fmts = [
        '',
        'dddd MMMM DD hh:mma z',  # Saturday July 23 11:00pm AEST
        'dddd DD MMM hh:mma z',
        'MMMM DD hh:mma z',  # July 23 11:00pm AEST
        'ddd DD MMMM hh:mma z', # Sun 17 July 5:00am AEST
        'dddd DD:MM:YYYY ha z', # Wednesday 27.07.2022 5am CEST
        'dddd DD:MM:YYYY hh:mm a z', # Tuesday, 30:08:2022 07:00 am CEST
        'DDMMYYYY ha z', # 09.08.2022  5am CEST
        'DDMMYYYY hh:mma z', # 13.08.2022 11:00pm CEST
        'DD MMMM YYYY HH:mm z', # 30 August 2022 20:00 BST
        'HH:mm dddd DD MMMM z', # 19:00 Saturday 10th September BST
        'YYYY-MM-DD HH:mm:ss z',  # 2022-09-08 22:06:57
        'ddd DD MMM YYYY HH:mm:ss z', # Thu, 15 Sep 2022 13:29:26 GMT
        'DD/MM/YYYY HH:mm z', # 24/09/2022 19:00 BST
        'MMMM DD YYYY HH a z', # September 27 2022 5 am Europe/Berlin

        'hh:mma z', # 7:39PM UTC
        'hh:ma z',  # 7:39PM UTC
        'h:mma z',  # 7:39PM UTC
        'h:ma z',  # 7:39PM UTC

    ]

    # dt.strftime("%Y-%m-%dT%H:%M:%S")
    def __init__(self, time_str):
        self.orig_str = time_str.strip()
        self.dt = None
        self.debug = bool(strtobool(os.getenv('PYDBG', 'False')))

        self._normalize()
        if len(self.time_str) > 4:
          self._parseDatetime()
        else:
          self.convert()

    def dbg(self, string):
        if self.debug:
            print(f" >>dbg: {string}")
        else:
            pass

    def _normalize(self) :
        # squeeze out spaces
        dt_str = " ".join(self.orig_str.split())
        # if 'AEST' in dtstr.capitalize():
        # trim spaces by strip
        # translate to remove punctuation
        #   translate(str.maketrans('', '', string.punctuation)) REMOVES ':' not acceptable \
        dt_str = dt_str \
            .replace(',', '').replace('.', '').replace('#', '') \
            .replace(' - ', ' ') \
            .replace('(', '').replace(')', '') \
            .replace('AEST', 'Australia/Sydney').replace('AEDT', 'Australia/Sydney')\
            .replace("CEST", 'Europe/Berlin').replace("CET", 'Europe/Berlin') \
            .replace("BST", "Europe/London") \
            .strip().replace(' +', ' ')
        # print(dtstr)
        self.time_str = dt_str
        self.dbg(f"[{self.orig_str}] became [{self.time_str}]")

    @staticmethod
    def is_datetime_string(dtstr):
        if not dtstr and len(dtstr) <= 0:
            return False
        return True

    def doParseDt(self, fmt):
        try:
            if not self.dt:
                self.dbg(f"str={self.time_str}, dt={self.dt} and format={fmt}")
                if len(fmt) == 0:
                    self.dt = pdl.parse(self.time_str);
                else:
                    self.dt = pdl.from_format(self.time_str, fmt)

        except ValueError as ve:
            self.dbg(f"  [{fmt}] error: {repr(ve)}")
            pass

    def _parseDatetime(self):
        if not self.is_datetime_string(self.time_str):
            return
        if self.dt:
            return
        for fmt in self.fmts:
            self.doParseDt(fmt)

            if self.dt:
                break

    def show(self):
        self._parseDatetime()
        if not self.dt:
            return f"NOTHING for [{self.time_str}]"
        ca_tz = pdl.timezone('America/Los_Angeles')
        ca_dt = self.dt.in_tz(ca_tz)
        return ca_dt.strftime('%B %d %I:%M %p %Z')



if __name__ == "__main__":
    #dtstr = "2022-07-13T12:33:14.859Z"
    dtstr = "Saturday July 23 11:03pm AEDT "
    dtstr = "7:39PM UTC"
    dtstr = "30 August 2022 20:00 BST"
    #dt = pdl.from_format(dtstr, 'hh:mma z')
    fmt = 'DD MMMM YYYY HH:mm z'  # 30 August 2022 20:00 BST

    if len(sys.argv) > 1:
        dtstr = sys.argv[1]

    cvt = Cvt(dtstr)
    cvt.doParseDt(fmt)
    cvt.dbg(f"[{dtstr}] becomes\n{cvt.show()}")
    print(f"{cvt.show()}")
