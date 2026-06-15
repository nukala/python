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
from typing import Annotated

#
# WIP Idea is to replace hl=xx with an automatic script, that:
#  appends battery pct to a file (~/tmp/hl/monday.hl, etc)
#  copies "bat file_name" into clipboard
#  shows battery pct on command line
#  replace the file if dates are not the same
#
#  shows nothing if plugged in
#  hl = hide+lock -> close the lid
#
# Use sub-commands:
#

cli = typer.Typer()


class HideLock:
    @dataclass
    class AppConfig:
        keep: bool=False
        no_clear: bool=False
        cat_only: bool=False
        backup: bool=False
        verbosity: int=0

        def dump_config(self):
            # print(f"DUMP: show_pct={self.show_pct}, opened={self.opened}, keep={self.keep}, backup={self.backup}" + 
            #     f", no_clear={self.no_clear}, cat_only={self.cat_only}" + 
            #     f"\n\tverbosity={self.verbosity}")
            print(f"DUMP: keep={self.keep} backup={self.backup}, no_clear={self.no_clear}, cat_only={self.cat_only}" + 
                f"\n\tverbosity={self.verbosity}")

    @cli.command()
    def show(ctx: typer.Context,
        show_pct: Annotated[bool, typer.Option(help="Show battery percentage and cat the file.") ]=True,
        opened: Annotated[bool, typer.Option(help="Laptop opened, indicate so in the log")]=False,
        keep: Annotated[bool, typer.Option("-k", "--keep", "--keep-log", 
            help="Do not delete the log file, just keep appending.")]=False,
        
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
        hl:HideLock = HideLock()
        cfg: AppConfig=ctx.obj
        #print(f"in show ctx={ctx}")
        if not show_pct:
            if cfg.verbosity > 1:
                print(f"{cfg.verbosity} - not showing pct, not doing nothing.")
            return
        cfg.keep = keep
        pct, plugged = hl.check_battery()
        hl_str = f"{HideLock.get_now_ts()} battery={pct}%"
        if not plugged:
            if not cfg.no_clear:
                clear_screen()
            print(f"{hl_str}")
    
            fobj = hl.append_to_file(ctx, "hl.txt", hl_str, "hl", verbosity=cfg.verbosity, delete_if_older = True)
            print(f"========")
            hl.cat_to_sysout(fobj)

    @cli.command(help="concatenate log ONLY, optionally no-clear-screen")
    def cat(ctx: typer.Context,
    
            help: Annotated[bool, typer.Option("-h", help="show this help text")]=False,
            ) -> None:
        hl: HideLock=HideLock()
        if not ctx.obj.no_clear:
            clear_screen()
        fobj=hl.get_file_path(subfolder="hl", filename="hl.txt")
        hl.cat_to_sysout(fobj)

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
        file_path = HideLock.get_file_path(filename, subfolder=subfolder, verbosity=verbosity)
        cfg: AppConfig=ctx.obj

        # delete if there is an older file
        if not cfg.keep and delete_if_older:
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
        no_clear: Annotated[bool, typer.Option(help="Do not clear screen before concatenating log file")]=False,
        cat_only: Annotated[bool, typer.Option(
            help="Only concatenate the log file. Donot show, donot append log file")]=False,

        backup: Annotated[bool, typer.Option("-b", 
            help="WIP: As day-of-week and replace as needed. As monday.hl for example")]=False,

        # explicitly adding this seems to enable `-h`
        help: Annotated[bool, typer.Option("-h", help="show this help text")]=False,
        verbosity: Annotated[int, typer.Option("-v", count=True, 
            help="Set verbosity level. Use -v for warning, -vv for info, -vvv for debug.") ]=0,
        vlevel: Annotated[int, typer.Option("--verbosity", "-vrb",
            help="Specify a verbosity level, 1=warning, 2=info,3=debug etc.")]=0,
    ) -> None:
        """
        typer_entry_point: To show the current battery percentage. Log them into a file and optionally remove the file the next day this program is executed.
        
        Hide all programs except terminal, then run this program and lock the screen.

        [yellow]WIP backup into day-of-week file (say wednesday.hl, etc) and over write as needed[/yellow]
        """
        # prepare config
        if vlevel > 0:
            verbosity = vlevel
        
        # now setup config
        cfg: HideLock.AppConfig=HideLock.AppConfig(backup=backup, no_clear=no_clear, cat_only=cat_only, 
            verbosity=verbosity)
        print(f"entry_point ", end='')
        cfg.dump_config()
        # hl.config.show_pct=show_pct

        ctx.obj = cfg
        if verbosity > 7:
            #just show parameters and return
            cfg.dump_config()
            return
        if ctx.invoked_subcommand is None:
            print("No command provided. Running default action...", end='')
            ctx.obj.dump_config()
            print(f"before default show ctx=[{ctx}]")
            ctx.invoke(show)


if __name__ == "__main__":
    #typer.run(HideLock.typer_entry_point)
    cli()
