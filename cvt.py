#!/usr/bin/env python3
# coding: utf-8


import pendulum as pdl
import sys
import re


# pendulum.parse(str)
# pendulum.from_format('Saturday July 23 11:05pm', 'dddd MMMM DD hh:mma')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma zz')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma z')
# pendulum.from_format('Saturday July 23 11:05pm EST', 'dddd MMMM DD hh:mma z')
# pendulum.from_format('Saturday July 23 11:05pm AEST', 'dddd MMMM DD hh:mma z')
# import readline
# for i in range(readline.get_current_history_length()):
#   print(readline.get_history_item(i+1))
# readline.clear_history()

class Cvt:
    # https://github.com/sdispater/pendulum/blob/master/docs/docs/string_formatting.md
    # https://github.com/sdispater/pendulum/blob/master/docs/docs/timezones.md
    fmts = [
        '',
        'dddd MMMM DD hh:mma z',  # Saturday July 23 11:00pm AEST
        'MMMM DD hh:mma z',  # July 23 11:00pm AEST
        'ddd DD MMMM hh:mma z', # Sun 17 July 5:00am AEST
        'dddd, DD.MM.YYYY ha z', # Wednesday, 27.07.2022 5am CEST
        'DDMMYYYY ha z', # 09.08.2022  5am CEST
        'hh:mma z', # 7:39PM UTC
        'hh:ma z',  # 7:39PM UTC
        'h:mma z',  # 7:39PM UTC
        'h:ma z',  # 7:39PM UTC
    ]

    # dt.strftime("%Y-%m-%dT%H:%M:%S")
    def __init__(self, time_str):
        self.orig_str = time_str.strip()
        self.dt = None
        self._normalize()
        self.debug = False
        self._parse()

    def dbg(self, string):
        if self.debug:
            print(f" >>dbg: {string}")
        else:
            pass

    def _normalize(self) :
        # squeeze out spaces
        dt_str = re.sub(' +', ' ', self.orig_str)
        # if 'AEST' in dtstr.capitalize():
        # trim spaces by strip
        # translate to remove punctuation
        #   translate(str.maketrans('', '', string.punctuation)) REMOVES ':' not acceptable \
        dt_str = dt_str \
            .replace(',', '').replace('.', '').replace('#', '') \
            .strip()\
            .replace('AEST', 'Australia/Sydney').replace('AEDT', 'Australia/Sydney')\
            .replace("CEST", 'Europe/Berlin').replace("CET", 'Europe/Berlin')
        # print(dtstr)
        self.time_str = dt_str

    @staticmethod
    def is_datetime_string(dtstr):
        if not dtstr and len(dtstr) <= 0:
            return False
        return True

    def _parse(self):
        if not self.is_datetime_string(self.time_str):
            return
        if self.dt:
            return
        for fmt in self.fmts:
            self.dbg(f"str={self.time_str}, dt={self.dt} and format={fmt}")
            try:
                if not self.dt:
                    if len(fmt) == 0:
                        self.dt = pdl.parse(self.time_str);
                    else:
                        self.dt = pdl.from_format(self.time_str, fmt)

                else:
                    break
            except ValueError as ve:
                self.dbg(f"  [{fmt}] error: {repr(ve)}")
                pass

    def toPdt(self):
        self._parse()
        if not self.dt:
            return f"NOTHING for [{self.time_str}]"
        ca_tz = pdl.timezone('America/Los_Angeles')
        ca_dt = self.dt.in_tz(ca_tz)
        return ca_dt.strftime('%B %d %I:%M %p %Z')



if __name__ == "__main__":
    #dtstr = "2022-07-13T12:33:14.859Z"
    dtstr = "Saturday July 23 11:03pm AEDT "
    dtstr = "7:39PM UTC"
    #dt = pdl.from_format(dtstr, 'hh:mma z')

    if len(sys.argv) > 1:
        dtstr = sys.argv[1]

    cvt = Cvt(dtstr)
    cvt.dbg(f"[{dtstr}] becomes\n{cvt.toPdt()}")
    print(f"{cvt.toPdt()}")
