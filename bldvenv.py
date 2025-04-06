#!/usr/bin/env python3
# coding: utf-8

from basern import rnutils
from datetime import datetime
import os
import subprocess
import sys


class BuildVenv:
    verbose = False

    def __init__(self, verbose = False):
        self.verbose = verbose

    def activate_venv(self):
        # try venv, env, myenv
        envdir = rnutils.find_recursively("venv", start_path=__file__, check_folder=True)
        reqtxt = rnutils.find_recursively("requirements.txt", __file__, verbose=self.verbose)
        if reqtxt is None:
            print(f"Missing requirements.txt file")
            return
        print(f"venv={envdir}, exists={os.path.isdir(envdir)}\nreq={reqtxt}")
        if self.verbose:
            print("")
        start = rnutils.log_ts(verbose=self.verbose)
        if self.verbose:
            print(f"Started at {start}")
        try:
            vdir = envdir if envdir else "venv"
            subprocess.run([sys.executable, "-m", "venv", vdir], capture_output=True)
            folder = "Scripts" if sys.platform == "win32" else "bin"
            subprocess.run([os.path.join(envdir, folder, "pip"), "install"
                               , "--verbose", "--upgrade-strategy", "only-if-needed"
                               , "--no-python-version-warning", "--disable-pip-version-check"
                               , "-r", reqtxt])
        except KeyboardInterrupt:
            print(f"Interrupted")
        end = rnutils.log_ts(verbose=self.verbose)
        if self.verbose:
            print(f"\n")
        print(f"  end={end}\nstart={start}")


if __name__ == "__main__":
    bv = BuildVenv(True)
    bv.activate_venv()
