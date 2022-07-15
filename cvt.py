#!/usr/bin/env python3
# coding: utf-8

import pendulum as pdl
import sys

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
        'MMMM DD hh:mma z'  # July 23 11:00pm AEST
    ]

    def __init__(self, time_str):
        self.orig_str = time_str.strip()
        self.dt = None
        self._normalize()
        self.debug = False

    def _dbg(self, string):
        if self.debug:
            print(f" >>dbg: {string}")
        else:
            pass

    def _normalize(self) :
        # if 'AEST' in dtstr.capitalize():
        dt_str = self.orig_str.replace('AEST', 'Australia/Sydney').replace('AEDT', 'Australia/Sydney')
        # print(dtstr)
        self.time_str = dt_str

    def _parse(self):
        for fmt in self.fmts:
            #print(f"str={self.time_str}, dt={self.dt} and format={fmt}")
            try:
                if not self.dt:
                    if len(fmt) == 0:
                        self.dt = pdl.parse(self.time_str);
                    else:
                        self.dt = pdl.from_format(self.time_str, fmt)

                else:
                    break
            except ValueError as ve:
                #print(f"  [{fmt}] error: {repr(ve)}")
                pass

    def toPdt(self):
        self._parse()
        if not self.dt:
            return ""
        ca_tz = pdl.timezone('America/Los_Angeles')
        ca_dt = self.dt.in_tz(ca_tz)
        return ca_dt.strftime('%B %d %I:%M %p %Z')



if __name__ == "__main__":
    #dtstr = "2022-07-13T12:33:14.859Z"
    dtstr = "Saturday July 23 11:03pm AEDT "
    # dt = pdl.from_format(dtstr, 'dddd MMMM DD hh:mma z')
    # print(f"dt={dt}")

    if len(sys.argv) > 1:
        dtstr = sys.argv[1]

    cvt = Cvt(dtstr)
    #print(f"[{dtstr}] becomes\n{cvt.toPdt()}")
    print(f"{cvt.toPdt()}")
