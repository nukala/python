#!/usr/bin/env python3
# coding: utf-8

###############################################################################
# WIP - due to mmap
#     - yucky way in which files are passed.
#        illegal arguments like -xxx are now considered files and then no help
#     - add option to ls -ltr also 
###############################################################################

from argparse import ArgumentParser

import hashlib
import mmap

class Md5:

    def __init__(self):
        self.BLOCK_SZ = 8192
        self.parsed = None
        self.unknown_args = None

    def process_block(self, fname):
        hasher = hashlib.md5()
        with open(fname, "rb") as ff:
            hunk = ff.read(self.BLOCK_SZ)
            while len(hunk) > 0:
                hasher.update(hunk)
                hunk = ff.read(self.BLOCK_SZ)

        return hasher.hexdigest()

    # TODO: work in progress, there is a permission error while mapping
    def process_mmap(self, fname):
        hasher = hashlib.md5()
        with open(fname, "rb") as ff:
            mm = mmap.mmap(ff.fileno(), 0)
            hunk = mm.read(self.BLOCK_SZ)
            while len(hunk) > 0:
                hasher.update(hunk)
                hunk = mm.read(self.BLOCK_SZ)

        return hasher.hexdigest()

    def process_inline(self, file_name: str, verbose: int = 0):
        if verbose > 0:
            print(f"inline: Input filename=[{file_name}]")

        from basern.rnutils import open_resolved
        with open_resolved(file_name, verbose = verbose) as ff:
            digest = hashlib.file_digest(ff, "md5")

        return digest.hexdigest()

    def parse_args(self, args=None):
        parser = ArgumentParser(prog='md5',
                                description="To generate md5 sum of specified files in a platform agnostic way.")
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

        self.parsed, self.unknown_args = parser.parse_known_args(args)

        if self.parsed.short and len(self.unknown_args) > 1:
            raise Exception(f"Short={self.parsed.short} and unknown_args{self.unknown_args}"
                            f".len={len(self.unknown_args)} are not compatible"
                            f"\nONLY one file_name is allowed!")

        if self.parsed.lsltr:
            self.parsed.short = True

    @staticmethod
    def parse_lsl(lsl_str: str, verbose: int = 0):
        """
        Parses ls -ltr output, removes permissions and owner-group details.
        Shows only size and modification dates. Filename too

        So:
          -rwxr-xr-x 1 ravi None 1690 Nov 10 14:13 FILE_NAME
        becomes
          1690 Nov 10 14:13 FILE_NAME
        """
        if verbose > 1:
            print(f"Input lsl=[{lsl_str}]")
        parts = lsl_str.split(" ")
        num: int = len(parts)

        if num <= 0:
            return ""

        parsed = " ".join(parts[4:])

#        from basern.getmtag import is_windows
#        if is_windows():
#            parsed = " ".join(parts[4:])

        if verbose >= 1:
            print(f" num={num}, parsed={parsed}")
        return parsed


###### end of md5 class

if __name__ == "__main__":
    # fname = sys.argv[1]
    msum = Md5()

    msum.parse_args()

    # preparation to help measure time spent
    for fname in msum.unknown_args:
        the_hash = 'unknown'
        try:
            if msum.parsed.use_block:
                the_hash = msum.process_block(fname)
            elif msum.parsed.use_mmap:
                the_hash = msum.process_mmap(fname)
            else:
                the_hash = msum.process_inline(fname, msum.parsed.verbose)

            end = ""
            if msum.parsed.newline:
                end = "\n"
            if msum.parsed.short:
                print(f"{the_hash}", end=f"{end}")
                if msum.parsed.lsltr:
                    from basern.rnutils import getoutput_from_run
                    lsl = getoutput_from_run(['ls', '-ltr', fname], None,
                                             show_result=False, show_output=False, show_error=False)['stdout']
                    print(f"  {msum.parse_lsl(lsl, msum.parsed.verbose)}")
                if msum.parsed.after_sep:
                    print(f"{msum.parsed.after_sep}", end="")
            else:
                fname = (fname.replace("/cygdrive/c/Users/ravi", "~")
                         .replace("C:/Users/ravi", "~"))
                print(f"{the_hash}\t{fname}")
        except (OSError, PermissionError) as e:
            print(f"{e}\n")
            if msum.parsed.verbose > 1:
                import traceback

                traceback.print_exc()
            print("\n")
            pass
