from __future__ import annotations

import os
import psutil
import shutil
import sys
import typer

from basern.rnutils import clear_screen, delete_if_older_than_today
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Annotated, Final

# WIP:
#  opened is a sub-command instead of option, duplicate? clear and keep
#   remove show_pct is this implied, any other behavior possible?
#
#==========
# Idea is to generate battery percentages, log them into a file and show them in the end. Also clean up logs from
#  executions of prior days
#  appends battery pct to the same log file
#  shows battery pct on command line
#  replace the file if dates are not the same
#
#  shows nothing if plugged in
#  hl = hide+lock -> close the lid
#

cli = typer.Typer()


class HideLock:
    @dataclass
    class HlConfig:
        SUB_FOLDER: Final[str] = "hl"
        HL_FILE_NAME: Final[str] = "hl.txt"

        clear: bool=True
        keep: bool=False
        opened: bool=False
        verbosity: int=0

        def dump_config(self, message=""):
            print(f"{message}DUMP: keep={self.keep}, clear={self.clear}, opened={self.opened}" + 
                f"\n\tverbosity={self.verbosity}")

 #   @l
    @cli.command()
    def show(ctx: typer.Context,
        show_pct: Annotated[bool, typer.Option(help="Show battery percentage and cat the file.") ]=True,
        opened: Annotated[bool, typer.Option("-o", "--opened",
            help="Laptop opened, indicate so in the log. default=off.")]=False,
        keep: Annotated[bool, typer.Option(help="Do not delete the log file on next day, just keep appending.")]=False,
        
        help: Annotated[bool, typer.Option("-h", help="show this help text")]=False,
            ) -> None:
        """
        Shows the current available battery percentage, appends to a log file, clears the screen and con-catenates log-file contents onto the screen. Also, deletes the log-file if day changes from 14th to 15th say

	[b]
        optional controls:
            opened:  to show that laptop was opened when the percentages were generated
            keep:  do not delete the log file of prior day
        [/b]
        """
        cfg: HideLock.HlConfig=ctx.obj
        if cfg.verbosity >= 3:
            print(f"in show ctx={ctx}")
        if not show_pct:
            if cfg.verbosity > 1:
                print(f"{cfg.verbosity} - not showing pct, not doing nothing.")
            return
        cfg.keep = keep
        cfg.opened = opened

        hl:HideLock = HideLock()
        # gather percentage and write to file
        hl.gatherpct_writelog(ctx)

    @cli.command(help="concatenate log ONLY, optionally for clear screen")
    def cat(ctx: typer.Context,
            clear: Annotated[bool, typer.Option(help="Clear screen before concatenating log file")]=True,
    
            help: Annotated[bool, typer.Option("-h", help="show this help text")]=False,
            ) -> None:
        hl: HideLock=HideLock()
        cfg: HideLock.HlConfig=ctx.obj

        cfg.clear=clear
        if cfg.clear:
            clear_screen()
        fobj=hl.get_file_path(subfolder=HideLock.HlConfig.SUB_FOLDER, filename=HideLock.HlConfig.HL_FILE_NAME)
        hl.cat_to_sysout(fobj)

    def gatherpct_writelog(self, ctx: typer.Context) -> None:
        pct, plugged = self.check_battery()

        cfg:HideLock.HlConfig = ctx.obj
        if plugged:
            if cfg.verbosity >= 2:
                print(f" >>> plugged in, nothing to do")
                return

        hl_str = f"{HideLock.get_now_ts()} battery={pct}% {"OPENED" if cfg.opened else ""}"

        if cfg.clear:
            clear_screen()
        print(f"{hl_str}")

        fobj = self.append_to_file(ctx, HideLock.HlConfig.HL_FILE_NAME, hl_str, HideLock.HlConfig.SUB_FOLDER, 
            verbosity=cfg.verbosity, delete_if_older=True)
        print(f"========")
        self.cat_to_sysout(fobj)


    def check_battery(self) -> tuple[int, bool]:
        """
        returns battery percentage and plugged in status if possible
        if no battery returns 100(plugged in?), True
        """
        battery = psutil.sensors_battery()
        
        if battery is None:
            print(" >>> No battery detected on this device.")
            return 100, True
        
        percent = battery.percent
        plugged = battery.power_plugged
    
        return percent, plugged

    @staticmethod
    def get_file_path(filename: str, subfolder:str, verbosity: int=0) -> Path:
        # Resolve the base directory and create subfolders if they don't exist
        base_dir = Path.home() / "tmp" / subfolder
        base_dir.mkdir(parents=True, exist_ok=True)
    
        file_path = base_dir / filename
        if verbosity>1:
            print(f"{verbosity} - returning [{file_path}]")
        return file_path

    @staticmethod
    def append_to_file(ctx: typer.Context, filename: str, content: str, subfolder: str = "default", 
            delete_if_older: bool = False, verbosity: int = 0) -> str|Path:
        """
	Appends a line of text to a file within ~/tmp/[subfolder].

	Does not follow SOLID. Peforms append and delete <YUCK>
        """
        cfg: HideLock.HlConfig=ctx.obj
        file_path = HideLock.get_file_path(filename, subfolder=subfolder, verbosity=verbosity)

        # delete if there is an older file
        if not cfg.keep and delete_if_older:
            if cfg.verbosity >= 3:
                print(f" checking to delete keep={cfg.keep}, delete_if_older={delete_if_older}")
            stat = os.stat(file_path)
            if delete_if_older_than_today(file_path, verbosity=verbosity):
                print(f"modified={datetime.fromtimestamp(stat.st_mtime)} older file deleted!")
        else:
            print(f"  >> not deleting keep={cfg.keep}, delete_if_older={delete_if_older}")


        # Use 'a' (append) mode to add content without overwriting
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{content.rstrip()}\n")
        return file_path


    @staticmethod
    def cat_to_sysout(file_obj: str|Path) -> None:
        import shutil
        import sys
        with open(file_obj, "r") as ff:
            shutil.copyfileobj(ff, sys.stdout)

    @staticmethod
    def get_now_ts() -> str:
        #16:so31 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %p %Z")
        now_str = datetime.now().strftime('%b%d %H:%M:%S')
        return now_str

    @cli.callback(invoke_without_command=True)
    def typer_entry_point(ctx: typer.Context,        
        clear: Annotated[bool, typer.Option(help="Clear screen before concatenating log file")]=True,

        # explicitly adding this seems to enable `-h`
        help: Annotated[bool, typer.Option("-h", help="show this help text")]=False,
        verbosity: Annotated[int, typer.Option("-v", count=True, 
            help="Set verbosity level. Use -v for warning, -vv for info, -vvv for debug.") ]=0,
        vlevel: Annotated[int, typer.Option("--verbosity", "-vrb",
            help="Specify a verbosity level, 1=warning, 2=info,3=debug etc.")]=0,
    ) -> None:
        """
        To show the current battery percentage. Log them into a file and optionally remove the file the next day this program is executed.
        
        Hide all programs except terminal, then run this program and lock the screen.

        [yellow]IGNORING backup into day-of-week file (say wednesday.hl, etc) and over write as needed[/yellow]
        """
        # prepare config
        if vlevel > 0:
            verbosity = vlevel
        
        # now setup config
        cfg: HideLock.HlConfig=HideLock.HlConfig(clear=clear, verbosity=verbosity)
        if cfg.verbosity >= 3:
            cfg.dump_config("entry_point ")

        ctx.obj = cfg
        if cfg.verbosity > 7:
            #just show parameters and return
            cfg.dump_config()
            return
        if ctx.invoked_subcommand is None:
            msg="No command provided, defaualt action=show " if cfg.verbosity > 2 else ""
            if cfg.verbosity >= 3:
                cfg.dump_config(f"{msg}")
                print(f"before default show ctx=[{ctx}]")
            HideLock.show(ctx)


if __name__ == "__main__":
    cli()
