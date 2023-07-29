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
from argparse import ArgumentParser

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
        'DD/MM/YY HH:mm z', # 24/09/22 19:00 BST
        'DD-MM-YY HH:mm z',  # 01-06-23   21:00 Europe/Madrid
        'DD/MM/YYYY HH:mm z', # 24/09/2022 19:00 BST
        'DD/MM/YYYY HH:mm a z', # 25/06/2023 09:00 AM
        'DD-MM-YYYY HH:mm z',  # 01-06-2023   21:00 Europe/Madrid
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
        'MMMM DD YYYY h a z',  # June 27, 2023 5 am
        'MMMM DD YYYY h:m a z', # June 27, 2023 5:00 am
        'dddd MMMM DD h a z', #Sunday, June 25th 10 am
     ]

    def parse_args(self, args=None):
        parser = ArgumentParser(prog = 'cvt'
                                , description='To convert strings into Pacific timezone equivalents'
                                , epilog="START_STR is required")
        parser.add_argument('-f', '--from', dest='start_str', nargs="?", default=None, required=True
                            , help='when the maintenance starts')
        parser.add_argument('-t', '--to', dest='end_str', nargs="?", default=None, required=False
                            , help='when the maintenance completes')

        parser.add_argument('-d', '--debug', action='store_true', default=False, dest = "debug"
                            , help='Enable debug logs')
        parser.add_argument('-v', '--verbose', action='store_true', default=False, dest="verbose"
                            , help='Enable verbose logs')
        parser.add_argument('-es', '--es', '--madrid', dest="madrid"
                            , action='store_true', required=False, default=False
                            , help='Append Europe/Madrid as the timezone')
        parser.add_argument('-uk', '--uk', '--london', dest="london"
                            , action='store_true', required=False, default=False
                            , help='Append Europe/London as the timezone')
        parser.add_argument('-fr', '--fr', '--paris', dest="paris"
                            , action='store_true', required=False, default=False
                            , help='Append Europe/Paris as the timezone')
        parser.add_argument('-de', '--de', '--berlin', dest="berlin"
                            , action='store_true', required=False, default=False
                            , help='Append Europe/Berlin as the timezone')
        parser.add_argument('-au', '--au', '--sydney', dest="sydney"
                            , action='store_true', required=False, default=False
                            , help='Append Australia/Sydney as the timezone')
        parsed = parser.parse_args(args)
        #print(f"PARSED> {parsed}, from=[{parsed.start_str}], to=[{parsed.end_str}], "
        #      f"madrid={parsed.madrid}, debug={parsed.debug}, verbose={parsed.verbose}")
        return parsed

    # match and case are new in 3.10, so lets use elif for now
    def tz_name(self):
        ret = None
        if self.parsed.madrid:
            ret = "Europe/Madrid"
        elif self.parsed.london:
            ret = "Europe/Lodon"
        elif self.parsed.paris:
            ret = "Europe/Paris"
        elif self.parsed.berlin:
            ret = "Europe/Berlin"
        elif self.parsed.sydney:
            ret = "Australia/Sydney"
        if not ret:
            self.dbg(f"parsed=[{self.parsed}] no timezone {ret}")
        return ret

    def __init__(self, arguments=None):
        self.parsed = self.parse_args(arguments)
        self.debug = self.parsed.debug
        self.verbose = self.parsed.verbose

        if self.parsed.verbose == True:
            self.debug = True

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

    def _normalize(self, some_str) :
        # squeeze out spaces
        dt_str = " ".join(some_str.split())
        # if 'AEST' in dtstr.capitalize():
        # trim spaces by strip
        # translate to remove punctuation
        #   translate(str.maketrans('', '', string.punctuation)) REMOVES ':' not acceptable \
        dt_str = dt_str \
            .replace(',', '').replace('.', '').replace('#', '') \
            .replace(' - ', ' ') \
            .replace('(', '').replace(')', '') \
            .replace('horas', '') \
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

        self.dbg(f"[{some_str}] became [{dt_str}]")
        return dt_str

    @staticmethod
    def is_datetime_string(dt_str):
        if not dt_str and len(dt_str) <= 0:
            return False
        return True

    def get_from(self):
        return self.parsed.start_str

    def get_to(self):
        return self.parsed.end_str

    def do_parse_dt(self, fmt, dt_str):
        ret = None
        try:
            self.vrbs(f"Trying: str={dt_str}, and format={fmt}")
            if len(fmt) == 0:
                ret = pdl.parse(dt_str);
            else:
                ret = pdl.from_format(dt_str, fmt)
            if ret:
                self.dbg(f"MATCHED {dt_str} with format=[{fmt}], is=[{ret}]")
        except ValueError as ve:
            pass

        return ret

    def parse_datetime(self, some_str):
        if not self.is_datetime_string(some_str):
            return

        dt_str = self._normalize(some_str)
        for fmt in self.fmts:
            the_dt = self.do_parse_dt(fmt, dt_str)

            if the_dt:
                break
        return the_dt

    def show(self, dt_str):
        dt = self.parse_datetime(dt_str)
        if not dt:
            tz = self.tz_name()
            if tz:
                dt_str = f"{dt_str} {self.tz_name()}"
                dt = self.parse_datetime(dt_str)
            if not dt:
                return f"NOTHING for [{dt_str}], tz=[{tz}]"

        ca_tz = pdl.timezone('America/Los_Angeles')
        ca_dt = dt.in_tz(ca_tz)
        return ca_dt.strftime('%B %d %I:%M %p %Z')



if __name__ == "__main__":
    args = None#["-es", "-f", "15/06/2023   23:30", "-t", "16/06/23   01:30 horas"]
    cvt = Cvt(args)
    bgn = cvt.show(cvt.get_from())
    edn = None
    if cvt.get_to():
        edn = cvt.show(cvt.get_to())

    print(f"{bgn}", end = '')
    if edn:
        print(f" to {edn}", end = '')

    print("")
