from rnutils import is_exists

import sys
import os
import platform
import datetime
import subprocess

def creation_date(path):
  """
  Return timestamp in a readable fashion
  """
  return datetime.datetime.fromtimestamp(creation_timestamp(path))

def creation_timestamp(path):
    """
    Get the timestamp that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    ct = None
    if platform.system() == 'Windows':
        ct = os.path.getctime(path)
    else:
        stat = os.stat(path)
	#print(str(stat))
        try:
            ct = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            ct = stat.st_mtime
    return ct
   

def modification_date(path):
  """
  Return modifcation date in a readable fashion
  """
  return datetime.datetime.fromtimestamp(modification_timestamp(path))


def modification_timestamp(path):
  mt = None
  if platform.system() == 'Windows':
    mt = os.path.getmtime(path)
  else:
    stat = os.stat(path)
    #print(str(stat))
    mt = stat.st_mtime
  return mt

def get_mod_fstamp(path):
    """
    Get the modify timestamp in yymondd format (20jan01) in lowercase
    use current time if path does not exist
    """
    mt = datetime.datetime.today()
    if is_exists(path):
        mt = modification_date(path)

    return mt.strftime('%y%b%d').lower()


##################
# modify time of parameter

if __name__ == "__main__" :
    print(f"args={sys.argv}.{len(sys.argv)}")
    fn = sys.argv[1]
    print("=== ")
    if platform.system() == 'Darwin':
        stat = subprocess.run(["stat", "-x", fn], stderr=subprocess.DEVNULL)
    else:
        stat = subprocess.run(["stat", fn], stderr=subprocess.DEVNULL)
    print(f"stat={stat.returncode}{os.linesep}==={os.linesep}")
    if not stat.returncode == 0:
        print(f"file \"{fn}\" does not exist")
        sys.exit(1)
    print(f"\"{fn}\" was created at={creation_date(fn)}")
    print(f"\"{fn}\" was modified at={modification_date(fn)}")
    print(f"\"{fn}\" earliest = {min(modification_date(fn), creation_date(fn))}")
