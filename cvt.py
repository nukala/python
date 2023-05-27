#!/usr/bin/env python3.11
# coding: utf-8
import os

#######################################################
# Add support for --rmis and such to substitue the entire text if parsing succeed:
# RoyalMail (InterSoft) will be performing maintenance on their <optional | api type, e.g. international> API from May 02 12:00 PM PDT to May 02 04:01 PM PDT.
#
# During this time RoyalMail (InterSoft) <type of service down or just say all services, e.g. International label generation> will be unavailable.
#######################################################
import pendulum as pdl
import re
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
        'dddd MMMM DD hh:mma z',  # Saturday July 23 11:00pm AEST
        'dddd DD MMM hh:mma z',
        'MMMM DD hh:mma z',  # July 23 11:00pm AEST
        'ddd DD MMMM hh:mma z', # Sun 17 July 5:00am AEST

        'hh:mma z',  # 7:39PM UTC
        'hh:ma z',  # 7:39PM UTC
        'h:mma z',  # 7:39PM UTC
        'h:ma z',  # 7:39PM UTC

        'dddd DD:MM:YYYY ha z', # Wednesday 27.07.2022 5am CEST
        'dddd DD:MM:YYYY hh:mm a z', # Tuesday, 30:08:2022 07:00 am CEST
        'DDMMYYYY ha z', # 09.08.2022  5am CEST
        'DDMMYYYY hh:mma z', # 13.08.2022 11:00pm CEST
        'DD MMMM YYYY HH:mm z', # 30 August 2022 20:00 BST
        'HH:mm dddd DD MMMM z', # 19:00 Saturday 10th September BST
        'YYYY-MM-DD HH:mm:ss z',  # 2022-09-08 22:06:57
        'ddd DD MMM YYYY HH:mm:ss z', # Thu, 15 Sep 2022 13:29:26 GMT
        'DD/MM/YYYY HH:mm z', # 24/09/2022 19:00 BST
        'DD-MM-YYYY HH:mm z',  # 01-06-23   21:00 Europe/Madrid
        'MMMM DD YYYY HH a z', # September 27 2022 5 am Europe/Berlin
        'MMM DD HH:mm z', # Sep 26, 16:53 AEST
        'dddd MMMM DD YYYY HH:mm z',  # Thursday, September 29, 2022, 8:00
        'dddd MMMM DD YYYY HH:mm a z',  # Thursday, September 29, 2022, 10:00 am
        'dddd DD MMMM HH:mm a z', #Sunday 2 October 6:00 pm BST
        'dddd MMMM DD YYYY HH a z', # Sunday October 9, 2022 4 pm
        'ddd DD MMM hh:mma z', # Sat 15 Oct 09:00pm AEST
        'dddd DDMMYYYY HHa z', # 'Sunday, 05.02.2023 between 8am (CET)'
        'dddd DD MMMM hha z', # Saturday 18 February 6pm
        'DD MMMM HH:mm z', # 27th February -  20:00 (GMT)
        'ddd DD MMMM HH:mm a z', #Sat 18th March 11:00 –11:59 PM AEDT
        'HH:mma ddd DD MMM z', # 10:00pm Sat 11th Mar (AEDT)
        'dddd MMMM DD YYYY hha z', #Tuesday, March 28th 2023 6am 8pm (CEST)
     ]

    # dt.strftime("%Y-%m-%dT%H:%M:%S")
    def __init__(self, time_str):
        self.orig_str = time_str.strip()
        self.dt = None
        # to enable PYDBG=1 or on or yes or y
        self.debug = bool(strtobool(os.getenv('PYDBG', 'False')))
        self.verbose = bool(strtobool(os.getenv("PYVRBS", 'False')))

        if self.verbose == True:
            self.debug = True

        self.dbg("env[{PYVRBS}] = [{self.verbose}], using verbose logs")
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

    def vrbs(self, string):
        if self.verbose:
            print(f" >>vrbs: {string}")
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
            .replace("BST", "Europe/London").replace("BDT", "Europe/London") \
            .replace("europe", "Europe").replace("asia", "Asia").replace("america", "America") \
            .strip().replace(' +', ' ')


        dt_str = re.sub('[aA][mM]', 'am', dt_str)
        dt_str = re.sub('[pP][mM]', 'pm', dt_str)
        # SOa/45497158
        dt_str = re\
            .compile(r'(?<=\d)(th|nd|rd|st)')\
            .sub("", dt_str)

        self.dbg(f"[{self.orig_str}] became [{dt_str}]")
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
                self.vrbs(f"str={self.time_str}, dt={self.dt} and format={fmt}")
                if len(fmt) == 0:
                    self.dt = pdl.parse(self.time_str);
                else:
                    self.dt = pdl.from_format(self.time_str, fmt)
                self.dbg(f"matched {self.dt} with format=[{fmt}]")
        except ValueError as ve:
            #self.dbg(f"  [{fmt}] error: {repr(ve)}")
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
    dtstr = "30th August 2022 20:00 BST"
    #dt = pdl.from_format(dtstr, 'hh:mma z')
    fmt = Cvt.fmts[-1]

    args = sys.argv[1:] if len(sys.argv) > 1 else ["blah", dtstr]

    counter = 1
    for dtstr in args:
        counter = counter + 1
        cvt = Cvt(dtstr)
        cvt.doParseDt(fmt)
        cvt.dbg(f"[{dtstr}] becomes {cvt.show()}")
        print(f"{cvt.show()}", end = '')

        if len(args) > 1 and counter % 2 == 0:
            print(f" to ", end = '')
        elif counter > 2:
            print(f"")