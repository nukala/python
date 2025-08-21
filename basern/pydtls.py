#!/usr/bin/env python3
# coding: utf-8

import os
import platform
import sys
import sysconfig

print("os_name: " + os.name)
print("sys_platform: " + sys.platform)
print("platform_machine: " + platform.machine())
print("platform_python_implementation: " + platform.python_implementation())
print("platform_release: " + platform.release())
print("platform_system: " + platform.system())
print("platform_version: " + platform.version())
print("python_version: " + ".".join(platform.python_version_tuple()[:2]))
print("python_full_version: " + platform.python_version())

print(" ==== sys ==== ")
print("exec_prefix: " + sys.exec_prefix)
print("base_exec_prefix: " + sys.base_exec_prefix)
print("api_version: " + str(sys.api_version))
print("version_info: " + str(sys.version_info))
print(f"path: {str(sys.path)}\n")
if os.environ.get("HOME") is not None: 
  print(f"home: {os.environ["HOME"]}")
elif os.environ.get("USERPROFILE") is not None: 
  print(f"userprofile: {os.environ["USERPROFILE"]}")

print(f"system: {platform.system()}")
if platform.system() == 'Windows':
  print("winver: " + sys.winver)
  print(f"windows version: {sys.getwindowsversion()}")

def format_full_version(info):
    version = "{0.major}.{0.minor}.{0.micro}".format(info)
    kind = info.releaselevel
    if kind != "final":
        version += kind[0] + str(info.serial)
    return version


if hasattr(sys, "implementation"):
    implementation_version = format_full_version(sys.implementation.version)
    implementation_name = sys.implementation.name
else:
    implementation_version = "0"
    implementation_name = ''

print("implementation_name: " + implementation_name)
print("implementation_version: " + implementation_version)

print("")
print(f"platlibdir: {sys.platlibdir}")
print(f"plat.uname: {platform.uname()}")

print("")
print(f"LIBDIR: {sysconfig.get_config_vars('LIBDIR')}")
print(f"default scheme: {sysconfig.get_default_scheme()}")
print(f"path_names: {sysconfig.get_path_names()}")
print(f"platlib: {sysconfig.get_path('platlib')}")
