#!/usr/bin/env python3
# coding: utf-8
###############################################################################
# WIP - due to mmap
#     - yucky way in which files are passed.
#        illegal arguments like -xxx are now considered files and then no help
#     Missing CLI options:
#       missing/broken options with typer ---after for lsep
#       add tests for lister and this code!
#       support multiple -d options instead of CSV!
#       Option for ignoring all excludes dirs&files. Individual is overkill
#       cleanup usage after hooking up TeeFile with out and err!
#       support for groovy options=" -b -f -noout"; backup, write to file, nooutput
#       add for short path vs absolute
#     -
#     -
#     - grep -v Cache aaa | grep -v github | grep -v 26[a-z][a-z][a-z][0-9]| sort 1>as
###############################################################################
from __future__ import annotations

import hashlib
import mmap
import psutil
import sys
import typer

from basern.file_info import format_ls_name
from basern.lister import Lister
from basern.proc_utils import ProcUtils
from basern.rnutils import ( adjust_winpath, format_bytes, open_resolved )
from basern.stopwatch import Stopwatch
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import IO, List, Annotated, Final

# remove the completion related help text
# , "ignore_unknown_options": True
app = typer.Typer(add_completion=False,
                  context_settings={"help_option_names": ["-h", "--help", "-?"],
                                    "allow_extra_args": True, 
                                    "ignore_unknown_options": True, })


class Md5:

    @dataclass
    class MdConfig:
        directories: List[str]=None
        backup: bool=True
        force: bool=False
        verbosity: int=0
        full_path: bool=False
        lsltr: bool=False
        sum_only: bool=False
        format_size: bool=False
        short_sep: str=""

        def dump_config(self, message:str="", dirs_also:bool=False) -> str:
            dirs_str = f"\ndirs={self.directories}" if dirs_also else ""
            return (f"{message}DUMP: backup={self.backup}, force={self.force}, verbosity={self.verbosity}," +
                    f"full_path={self.full_path}, lsltr={self.lsltr}, short={self.sum_only}, " +
                    f"format_size={self.format_size}, short_sep={self.short_sep}" +
                    f"{dirs_str}")

    def __init__(self):
        self.BLOCK_SZ = 2*8_192
        self.parsed = None
        self.unknown_args = None
        self.lsl_timer = Stopwatch(precision=1)
        self.lst_timer = Stopwatch(precision=0)
        self.sum_timer = Stopwatch()

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

    @app.command(help="Generate MD5 sums of files and folders "
                      "\n  as specified via CLI switches !")
    def entry_point(
            ctx: typer.Context,
            dirs: Annotated[List[str], typer.Option("-d", "--dir", help="List of directories")]=None,
            force: Annotated[bool, typer.Option("-f", "--force", help="Force rewrite even if the output file exists already")]=False,
            posix: Annotated[bool, typer.Option("-p", "-fp", "--full_path", help="Use absolute posix paths")]=False,
            lsltr: Annotated[bool, typer.Option("-l", "-lsltr", "--lsltr",
                                                help="Show file size and modification dates")]=False,
            sum_only: Annotated[bool, typer.Option("-s", "-short", "--short", help="Short, only sum is printed")]=False,
            format_size: Annotated[bool, typer.Option("-fs", "--format_size", help="Format size into kB, etc.",)]=False,
            after_sep: Annotated[str, typer.Option("-a", "--after", help="ONLY when short is enabled, use this separator."
                                                                         "In order to minimize addtional 'echo -n ' in scripts")]="",

            verbosity: Annotated[int, typer.Option("-v", count=True,
                                                       help="Set verbosity level. Use -v for warning, -vv for info, -vvv for debug.")] = 0,
            vlevel: Annotated[int, typer.Option("--verbosity", "-vrb",
                                                    help="Specify a verbosity level, 1=warning, 2=info,3=debug etc.")] = 0,
    ):
        if vlevel>0:
            verbosity=vlevel

        # prepare config
        cfg: Md5.MdConfig = Md5.MdConfig(force=force, verbosity=verbosity)
        if dirs:
            cfg.directories=dirs
        cfg.full_path = posix
        cfg.lsltr = lsltr
        cfg.sum_only = sum_only
        cfg.format_size = format_size
        cfg.short_sep=after_sep

        # supply config into context, if there are other commands!
        ctx.obj = cfg

        if cfg.verbosity>2:
            print(f"{cfg.verbosity} - cfg={cfg}-{cfg.dump_config()}")

        # instantiate worker object
        msum: Md5 = Md5()
        # invoke business logic of this script
        msum.biz_logic(cfg, ctx.args)


    def biz_logic(self, cfg: Md5.MdConfig, args:list[str]):
        self.begin_work(cfg.directories, cfg.verbosity)
        files: list[str]
        if cfg.directories:
            files = self.build_files_list(cfg.directories, verbosity=cfg.verbosity)
        else:
            files = args

        if cfg.verbosity>5:
            print(f"v={cfg.verbosity} files[{files}].{len(files)}")
        for fname in files:
            adj_path = adjust_winpath(fname, verbose=cfg.verbosity > 0)
            adjusted = str(adj_path or "")

            try:
                the_hash = self.calculate_hash(fname, verbosity=cfg.verbosity)
                if not the_hash:
                    continue
                print(f"{self.build_output(cfg, adj_path, the_hash)}", end=f"{self.build_end(cfg)}")
            except (OSError, PermissionError, FileNotFoundError, WindowsError, UnicodeEncodeError) as e:
                print(f"{adjusted}\n\n")

        self.end_work(cfg.directories, files, cfg.verbosity)

    def build_end(self, cfg: Md5.MdConfig) -> str:
        # for now 
        return '' if cfg.sum_only else '\n'
    
    def build_output(self, cfg: Md5.MdConfig, adj_path: Path, hash: str) -> str:
        answer: str = f"{hash}"

        if cfg.verbosity>1:
            print(f" {cfg.verbosity} - {cfg.dump_config()}")

        if cfg.sum_only:
            return f"{answer}{cfg.short_sep}"
        if cfg.lsltr:
            answer=f"{answer}  {format_ls_name(adj_path, use_absolute=not cfg.format_size)}"
            return answer

        if cfg.full_path:
            answer=f"{answer} {adj_path.absolute().as_posix()}"
        else:
            answer=f"{answer} {adj_path.name}"

        return answer
    
    @staticmethod
    def get_file_name(file_name: str, full_path: bool=False) -> str:
        return Path(file_name).absolute().as_posix() if full_path else file_name

    def build_files_list(self, dirs: list[str], verbosity=0) -> list[str]:
        if not dirs:
            return []

        self.lst_timer.start()
        exc_dirs: list[str] = [*Lister.EXCLUDED_DIRS, "shp", "vimtmp",
                               "cygwin", "cygwin64", "Raj Debbad", "Ravi and Megan Weddings",]
        if verbosity > 2:
            print(f"excluded dirs = [{" ".join(exc_dirs)}]")

        exc_fils: list[str] = [*Lister.EXCLUDED_EXTS, ".foo",]
        if verbosity > 2:
            print(f"excluded files = [{" ".join(exc_fils)}]")

        if len(dirs) > 1:
            ProcUtils.lower_priority(verbose=verbosity)

        files: list[str] = []
        for dd in dirs:
            files.extend(Lister.deep_search_strs(dd, exclude_dirs=exc_dirs, exclude_exts=exc_fils
                                                 , verbose=verbosity, posix_path=True))
        self.lst_timer.stop()
        return files

    def calculate_hash(self, adjusted: str, verbosity: int = 0):
        the_hash: str|None
        self.sum_timer.start()
        # if self.parsed.use_block:
        #     the_hash = self.process_block(adjusted)
        # elif self.parsed.use_mmap:
        #     the_hash = self.process_mmap(adjusted)
        # else:
        the_hash = self.process_inline(adjusted, verbosity)
        self.sum_timer.stop()

        return the_hash

    @staticmethod
    def begin_work(dirs: list[str], verbosity: int = 0):
        if len(dirs or []) > 1 or verbosity > 0:
            print(f"# [ {" ".join(sys.argv[1:])} ]  ({datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')})"
                  f", begin nice={psutil.Process().nice()}")

    def end_work(self, dirs: list[str], files: list[str], verbosity: int = 0):
        if len(dirs or []) > 1 or verbosity > 0:
            lsl_str = f"lsl={self.lsl_timer}, " if self.lsl_timer.elapsed_seconds else ""
            lst_str = f"list_files={self.lst_timer}, " if self.lst_timer.elapsed_seconds else ""

            print(f"# Total number={len(files or [])}, gen_sums={self.sum_timer}, "
                  f"{lst_str}{lsl_str}nice={psutil.Process().nice()}")

###### end of md5 class

if __name__ == "__main__":
    # for files with unprintable names
    # Forces your console output to safely use UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    # fname = sys.argv[1]
    # msum = Md5()
    # msum.legacy_work()
    app()

