import os
import sys
import time
from argparse import ArgumentParser
from typing import Tuple
from ghsv import dbgln

def sleep_with_timing(milliseconds: int) -> Tuple[float, float, float]:
    """
    Sleeps for the given number of milliseconds and returns timing details.

    Args:
        milliseconds (int): The duration to sleep in milliseconds.

    Returns:
        Tuple[float, float, float]: A tuple containing:
            - start_time (float): Timestamp before sleeping.
            - end_time (float): Timestamp after sleeping.
            - elapsed (float): Actual elapsed time in milliseconds.
    """
    start_time: float = time.perf_counter()
    time.sleep(milliseconds / 1000.0)
    end_time: float = time.perf_counter()
    elapsed: float = (end_time - start_time) * 1000.0  # convert to ms
    return start_time, end_time, elapsed


class MsNap:
    msnap: int = 0
    verbose: int = 0
    fb_str: str = None
    newline: bool = False

    def __init__(self):
        self.parser = None
        self.unknown_args = None

    def populate_args(self, parsed):
        """
        populate class with values from parsed args
        """
        if parsed.msnap > 0:
            self.msnap = parsed.msnap
        self.verbose = parsed.verbose

        if parsed.fb_str and len(parsed.fb_str) > 0:
            self.fb_str = parsed.fb_str
        self.newline = parsed.newline

        if self.msnap == 0 and len(self.unknown_args) > 1:
            self.dbg1(f"No nap time specified. Looking at unknown_args={self.unknown_args}")
            self.msnap = int(self.unknown_args[1])
            self.dbg1(f"nap from unknown args={self.msnap}")

    def dbg1(self, msg: str):
        dbgln(msg, 1, self.verbose)

    def dbg2(self, msg: str):
        dbgln(msg, 2, self.verbose)

    def parse_args(self, args):
        parser = ArgumentParser(prog="frs",
                                description="To nap a few milliseconds")
        parser.add_argument('-v', action='count', default=0, dest="verbose",
                            help="Enable verbosity (more logging with -vv etc.)")
        parser.add_argument('--verbose', type=int, default=0, dest="verbose",
                            help="Enable verbosity by specifying a number")
        parser.add_argument("-fb", "--feedback", type=str, dest="fb_str",
                            help = "feedback character to echo after napping")
        parser.add_argument("-n", '-nap', '--nap', '--ms_nap', type=int, default=0,
                            dest='msnap', help="Millseconds to nap")
        parser.add_argument("-nl", "--new_line", action="store_true", dest="newline",
                            help = "terminate with a new line")
        self.parser = parser
        parsed, self.unknown_args = parser.parse_known_args(args)
        return parsed

    def do_nap(self):
        self.dbg2(f"napping for [{self.msnap}] millis")

        start, end, elapsed = sleep_with_timing(self.msnap)  # sleep 500 ms
        self.dbg2(f"start={start:.6f}, End={end:.6f}, Elapsed={elapsed:.3f} ms")
        if self.fb_str:
            print(f"{self.fb_str}", end=os.linesep if self.newline else '')

    @staticmethod
    def show_error(msg: str):
        pfx = '' if 'ERR>' in msg else 'ERR> '
        sys.stderr.write(f"{pfx}{msg}")

    def main(self, args) -> int:
        parsed = self.parse_args(args)

        self.populate_args(parsed)
        self.dbg1(f"parsed={str(parsed)}, nap={self.msnap}")

        try:
            if self.msnap > 0:
                self.do_nap()
                return 0
            else:
                MsNap.show_error(f"ERR> Requires a millisecond_nap argument [with -n or direct]\n\n")
                self.parser.print_help()
        # TODO - allow for generic exception not working
        except Exception as e:
            MsNap.show_error(f"exception = {str(e)}")
            self.parser.print_help()

        return 1

if __name__ == "__main__":
    app: MsNap = MsNap()
    sys.exit(app.main(sys.argv))
