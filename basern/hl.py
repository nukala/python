import datetime
import os
import psutil
import shutil
import sys
from pathlib import Path

#
# WIP Idea is to replace hl=xx with an automatic script, that:
#  appends battery pct to a file (~/tmp/hl/monday.hl, etc)
#  copies "bat file_name" into clipboard
#  shows battery pct on command line
#  replace the file if dates are not the same
#
#  shows nothing if plugged in
#
def check_battery() -> tuple[int, bool]:
    """
    returns battery percentage and plugged in status if possible
            if no battery returns 100(plugged in?), True
    """
    battery = psutil.sensors_battery()
    
    if battery is None:
        print("No battery detected on this device.")
        return 100, True
        
    percent = battery.percent
    plugged = battery.power_plugged
    
#    if not plugged:
#        #16:so31 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %p %Z")
#        #print(f"{now_str} battery={percent}%")
#	return percent, False
#    else: 
#        #print(f"{now_str}  Power Source: {'AC Adapter (Plugged In)' if plugged else 'Battery'}")
#	return "", True
    return percent, plugged

def append_to_file(filename: str, content: str, subfolder: str = "default", file_marker: bool = False) -> str|Path:
    """Appends a line of text to a file within ~/tmp/[subfolder]."""
    # Resolve the base directory and create subfolders if they don't exist
    base_dir = Path.home() / "tmp" / subfolder
    base_dir.mkdir(parents=True, exist_ok=True)

    file_path = base_dir / filename

    ### if file separator is needed check and add when necessary
    if file_marker:
        from basern.rnutils import is_exists
        if not is_exists(file_path):
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"========\n")
                print(f"{file_path} created!")

    # Use 'a' (append) mode to add content without overwriting
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{content.rstrip()}\n")
    return file_path


def cat_to_sysout(file_obj: str|Path) -> None:
    import shutil
    import sys
    with open(file_obj, "r") as ff:
        shutil.copyfileobj(ff, sys.stdout)

if __name__ == "__main__":
    pct, plugged = check_battery()
    now_str = datetime.datetime.now().strftime('%b%d %H:%M:%S')
    hl_str = f"{now_str} battery={pct}%"
    if not plugged:
        print(f"{hl_str}")
    fobj = append_to_file("hl.txt", hl_str, "hl", True)
    cat_to_sysout(fobj)

