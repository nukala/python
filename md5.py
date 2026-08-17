#!/usr/bin/env python3
# coding: utf-8
###############################################################################
# WIP - due to mmap
#     - yucky way in which files are passed.
#        illegal arguments like -xxx are now considered files and then no help
#     - lister with folders via CSV
#     - use typer
#     - add tests for lister and this code!
#     - for ignoring exc_dirs and another for ignoring exc_fils
#     - lower priority
#     - cleanup usage after hooking up TeeFile with out and err!
#     -
#     -
#     - handling exceptions as in m5 $DBXDIR 1>dbx.md5
###############################################################################

import hashlib
import mmap
import os
import sys

from argparse import ArgumentParser

import psutil

from basern.lister import Lister
from basern.rnutils import ( adjust_winpath, format_bytes, open_resolved )
from basern.stopwatch import Stopwatch
from datetime import datetime
from typing import IO

class Md5:

    def __init__(self):
        self.BLOCK_SZ = 8192
        self.parsed = None
        self.unknown_args = None
        self.parse_timer = Stopwatch(precision=2)
        self.lst_timer = Stopwatch(precision=2)
        self.sum_timer = Stopwatch(precision=3)

    def process_block(self, fname: str):
        hasher = hashlib.md5()
        with open(fname, "rb") as ff:
            hunk = ff.read(self.BLOCK_SZ)
            while len(hunk) > 0:
                hasher.update(hunk)
                hunk = ff.read(self.BLOCK_SZ)

        return hasher.hexdigest()

    # TODO: work in progress, there is a permission error while mapping
    def process_mmap(self, fname: str):
        hasher = hashlib.md5()
        with open(fname, "rb") as ff:
            mm = mmap.mmap(ff.fileno(), 0)
            hunk = mm.read(self.BLOCK_SZ)
            while len(hunk) > 0:
                hasher.update(hunk)
                hunk = mm.read(self.BLOCK_SZ)

        return hasher.hexdigest()

    @staticmethod
    def process_inline(file_name: str, verbose: int = 0)-> str | None:
        if verbose > 0:
            print(f"process_inline: Input filename=[{file_name}]")

        ff: IO|None=None
        try:
            ff = open_resolved(file_name, verbose=verbose)
            if ff:
                return hashlib.file_digest(ff, "md5").hexdigest()
            elif verbose > 0:
                print(f"{verbose} file_name={file_name} could not be opened")
        finally:
            if ff is not None:
                ff.close()

    def parse_args(self, args=None):
        self.parse_timer.start()
        parser = ArgumentParser(prog='md5',
                                description="To generate md5 sum of specified files in a platform agnostic way."
                                            "Usage: time m5 -d $BOXDIR 1>aaa; shwm5 aaa")
        parser.add_argument('-v', '--verbose', action='count', default=0, dest="verbose",
                            help="Enable verbosity")
        parser.add_argument('-s', '--short', action='store_true', default=False, dest="short",
                            help="Short output, no filename, no CRLF or LF")
        parser.add_argument("-nl", "--new_line", action="store_true", dest="newline",
                            help="terminate with a new line")
        parser.add_argument('--mmap', "--memory_map", action='store_true', default=False,
                            dest="use_mmap", help="Use memory mapped files. DOES NOT WORK")
        parser.add_argument('--block', "--use_block", action='store_true', default=False,
                            dest="use_block", help="Use slower hashlib based operations")
        parser.add_argument("-l", "--lsltr", "--ls-ltr", action='store_true', default=False,
                            dest="lsltr", help="Execute ls -ltr on the file")
        parser.add_argument('-a', '--after', action='store', dest="after_sep",
                            help="When short is enabled, this parameter is printed after the sum. "
                                 + "In order to minimize addtional \'echo -n " "\' in scripts")
        parser.add_argument("-d", "--dirs", action="store", dest="dirs",
                            help="Find all the files in the folder specified via parameter and its sub-folders")

        self.parsed, self.unknown_args = parser.parse_known_args(args)

        if self.parsed.short and len(self.unknown_args) > 1:
            raise Exception(f"Short={self.parsed.short} and unknown_args{self.unknown_args}"
                            f".len={len(self.unknown_args)} are not compatible"
                            f"\nONLY one file_name is allowed!")

        if self.parsed.lsltr:
            self.parsed.short = True
        self.parse_timer.stop()

    @staticmethod
    def parse_lsl(lsl_str: str, raw_byte_count = True, verbose: int = 0):
        """
        Parses ls -ltr output, removes permissions and owner-group details.
        Shows only size and modification dates. Filename too

        So:
          -rwxr-xr-x 1 ravi None 1690 Nov 10 14:13 FILE_NAME
        becomes
          1690 Nov 10 14:13 FILE_NAME

        Args:
            lsl_str: String output from `ls -ltr FN`
            raw_byte_count: show count as bytes (default True)
                            False - formats the size in KB and MB
            verbose: show verbose output
        """
        if verbose > 1:
            print(f"Input lsl=[{lsl_str}]")
        parts = lsl_str.split(" ")
        num: int = len(parts)

        if num <= 0:
            return ""

        if raw_byte_count:
            parsed = " ".join(parts[4:])
        else:
            sz = format_bytes(parts[4]) + " "
            parsed = sz + " ".join(parts[5:])

        if verbose >= 1:
            print(f" num={num}, parsed={parsed}")
        return parsed

    def lower_priority(self, verbose:int=0):
        import psutil
        p = psutil.Process()
        old=p.nice()
        if psutil.WINDOWS:
            p.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            # On Unix/Linux/macOS, higher nice values mean lower priority (19 is max low)
            p.nice(19)
        if verbose>0:
            print(f"old niceness=[{old}], current=[{p.nice()}]")

    def build_files_list(self) -> list[str]:
        if not self.parsed.dirs:
            return []

        self.lst_timer.start()
        exc_dirs: list[str] = [*Lister.EXCLUDED_DIRS, "Ravi and Megan Weddings", "shp", "vimtmp", "cygwin",
                               "cygwin64", "Raj Debbad", f"ffox{os.sep}Cache"]
        if self.parsed.verbose > 2:
            print(f"excluded dirs = [{exc_dirs}]")

        exc_fils: list[str] = [*Lister.EXCLUDED_EXTS, ".foo" ]
        if self.parsed.verbose > 2:
            print(f"excluded files = [{exc_fils}]")

        dirs:list[str]
        if "," in self.parsed.dirs:
            dirs=self.parsed.dirs.split(",")
            self.lower_priority(verbose=self.parsed.verbose)
        else:
            dirs=[self.parsed.dirs]

        files: list[str] = []
        for dd in dirs:
            files.extend(Lister.deep_search_strs(dd, exclude_dirs=exc_dirs, exclude_exts=exc_fils
                                            , verbose=self.parsed.verbose, posix_path=True))
        self.lst_timer.stop()
        return files

###### end of md5 class

if __name__ == "__main__":
    # fname = sys.argv[1]
    msum = Md5()

    msum.parse_args()

    #for files with unprintable names
    # Forces your console output to safely use UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    if msum.parsed.dirs:
        print(f"# {sys.argv} parsed={msum.parse_timer} ({datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')})"
              f", nice={psutil.Process().nice()}")
    # preparation to help measure time spent
    files: list[str] = msum.unknown_args if not msum.parsed.dirs else msum.build_files_list()

    msum.sum_timer.start()
    for fname in files:
        the_hash = 'unknown'
        adj_path = adjust_winpath(fname, verbose=msum.parsed.verbose)
        if adj_path is None:
            if msum.parsed.verbose > 0:
                sys.stderr.write(f"fname={fname} does not exist. Cannot be adjusted\n")
            continue

        adjusted = str(adj_path)
        try:
            if msum.parsed.use_block:
                the_hash = msum.process_block(adjusted)
            elif msum.parsed.use_mmap:
                the_hash = msum.process_mmap(adjusted)
            else:
                the_hash = msum.process_inline(adjusted, msum.parsed.verbose)

            if the_hash is None:
                continue
            end = ""
            if msum.parsed.newline:
                end = "\n"
            if msum.parsed.short:
                print(f"{the_hash}", end=f"{end}")
                if msum.parsed.lsltr:
                    # lsl = getoutput_from_run(['ls', '-ltr', adjusted], None,
                    #                          show_result=False, show_output=False, show_error=False)['stdout']
                    # print(f"  {msum.parse_lsl(lsl, raw_byte_count=True, verbose=msum.parsed.verbose)}")
                    from basern.file_info import format_ls_name
                    print(f"  {format_ls_name(adjusted, use_absolute=True)}")
                if msum.parsed.after_sep:
                    print(f"{msum.parsed.after_sep}", end="")
            else:
                print(f"{the_hash}\t{adj_path.absolute().as_posix()}")
        except (OSError, PermissionError, FileNotFoundError, WindowsError, UnicodeEncodeError) as e:
            # if msum.parsed.verbose > 1:
            #     print(f"{e}\n")
            # print(f"=== {adj_path.absolute().as_posix()} ===")
            # import traceback
            #
            # traceback.print_exc(e)
            print(f"{adjusted}\n\n")

    # finished looping
    msum.sum_timer.stop()
    if msum.parsed.dirs:
        print(f"# Total number={len(files)}, gen_sums={msum.sum_timer}, list={msum.lst_timer}"
              f", nice={psutil.Process().nice()}")
