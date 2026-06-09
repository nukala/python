from __future__ import annotations

import os
import psutil
import shutil
import sys
from pathlib import Path
from datetime import datetime, date
from basern.rnutils import clear_screen, delete_if_older_than_today

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
# options
#  -opened -o   laptop opened
#  -h   multiline help
#  -keep  do not delete, just append
#  -backup backup old file NOT-WORKING
#  -v and --verbose  same as usual
#  -h and --help
#  -nc --no-clear
#

class HideLock:
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


if __name__ == "__main__":
    hl:HideLock = HideLock()
    pct, plugged = hl.check_battery()
#   #16:so31 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %p %Z")
    now_str = datetime.now().strftime('%b%d %H:%M:%S')
    hl_str = f"{now_str} battery={pct}%"
    if not plugged:
        clear_screen()
        print(f"{hl_str}")

        fobj = hl.append_to_file("hl.txt", hl_str, "hl", delete_if_older = True)
        print(f"========")
        hl.cat_to_sysout(fobj)
