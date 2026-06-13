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
#

#cli = typer.Typer()

class HideLock:
    def typer_entry_point(
        show_pct: Annotated[bool, typer.Option(help="Show battery percentage and cat the file.") ]=True,
        opened: Annotated[bool, typer.Option(help="Laptop opened, indicate so in the log")]=False,
        keep: Annotated[bool, typer.Option("-k", "--keep", "--keep-log", 
            help="Do not delete the log file, just keep appending.")]=False,
        
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
        perform: To show the current battery percentage. Log them into a file and optionally remove the file the next day this program is executed.
        
        Hide all programs except terminal, then run this program and lock the screen.

        [yellow]WIP backup into day-of-week file (say wednesday.hl, etc) and over write as needed[/yellow]
        """
        if vlevel > 0:
            verbosity = vlevel
        if verbosity > 7:
            #just show parameters and return
            print(f"show={show_pct}, opened={opened}, verbosity={verbosity}, vlevel={vlevel}, keep={keep}" + 
                f", backup={backup}, no_clear={no_clear}, cat_only={cat_only}")
            return
        hl:HideLock = HideLock()
        if not show_pct:
            if verbosity > 1:
                print(f"{verbosity} - not showing pct, not doing nothing.")
            return
        pct, plugged = hl.check_battery()
        hl_str = f"{HideLock.get_now_ts()} battery={pct}%"
        if not plugged:
            #clear_screen()
            print(f"{hl_str}")
    
            fobj = hl.append_to_file("hl.txt", hl_str, "hl", delete_if_older = True)
            print(f"========")
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
    def append_to_file(filename: str, content: str, subfolder: str = "default", delete_if_older: bool = False) -> str|Path:
        """
	Appends a line of text to a file within ~/tmp/[subfolder].

	Does not follow SOLID. Peforms append and delete <YUCK>
	"""
        # Resolve the base directory and create subfolders if they don't exist
        base_dir = Path.home() / "tmp" / subfolder
        base_dir.mkdir(parents=True, exist_ok=True)
    
        file_path = base_dir / filename
    
        # delete if there is an older file
        if delete_if_older:
            stat = os.stat(file_path)
            if delete_if_older_than_today(file_path):
                print(f"modified={datetime.fromtimestamp(stat.st_mtime)} older file deleted!")


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
    
    #@cli.callback()
    def foo(verbosity: Annotated[int, 
        typer.Option("--verbosity", "-v", count=True, 
            help="Set verbosity level. Use -v for warning, -vv for info, -vvv for debug."
        ) ] = 0,
        show_pct: Annotated[bool, 
        typer.Option("-show_pct", 
            help="Show battery percentage and cat the file."
        ) ] = True):
        """
        callback: To show the current battery percentage. Log them into a file and optionally remove the file the next day this program is executed.
        
        Hide all programs except terminal, then run this program and lock the screen.

        [yellow]WIP backup into day-of-week file (say wednesday.hl, etc) and over write as needed[/yellow]
        """
        print(f"{get_now_ts()} - callback invoked")
        pass

if __name__ == "__main__":
    typer.run(HideLock.typer_entry_point)
