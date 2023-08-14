import pathlib
import os

dir=pathlib.Path(".")
print(f"{dir.absolute().as_posix()}")

for fn in dir.iterdir():
  print(f"{fn.absolute().as_posix()}")