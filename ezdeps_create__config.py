##----------------------------------------------------------------------------##
## ezdeps_create__config.py                                                   ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import imp
import os
import platform
import sys


def get_host_os():
    if sys.platform == "win32":
        return "win"
    elif sys.platform == "linux":
        return "linux"


def get_host_arch():
    machine = platform.machine()
    if machine == "i386":
        return "x86"
    elif machine == "AMD64":
        return "x64"


def writestr(f, key, value):
    f.write('{0} = "{1}"\n'.format(key, value))


def writebool(f, key, value):
    if value:
        value = "True"
    else:
        value = "False"
    f.write("{0} = {1}\n".format(key, value))


# List of valid variable names.
variables_name = [
    "host_platform",
    "host_arch",
    "target_platform",
    "target_arch",
    "is_win",
    "is_linux"
]


def create__config(commandline_values, skip_config):
    """Create _config.py file that have these following variables:
    - host_platform = str
    - host_arch = str
    - target_platform = str
    - target_arch = str
    - is_win = bool
    - is_linux = bool
    Variables can can be set from multiple places, so the priorities are:
    default < existing value in file < command line
    You can skip loading value from _config.py (force recreate _config.py)
    by passing True to skip_config
    """
    variables_value = {}
    # First, set variables to their default value
    variables_value["host_platform"] = get_host_os()
    variables_value["host_arch"] = get_host_arch()
    variables_value["target_platform"] = get_host_os()
    variables_value["target_arch"] = get_host_arch()
    variables_value["is_win"] = False
    variables_value["is_linux"] = False
    if variables_value["host_platform"] == "win":
        variables_value["is_win"] = True
    if variables_value["host_platform"] == "linux":
        variables_value["is_linux"] = True
    # Next, load variables from existing _config.py and override the old values
    _config_loaded = False
    if not skip_config and os.path.exists("_config.py"):
        _config_loaded = True
        _config = imp.load_source("_config", "_config.py")
        for key, value in _config.__dict__.items():
            if not key.startswith("__"):
                if key in variables_name:
                    variables_value[key] = value
                else:
                    print("Unrecognized variable in _config.py: " + key)
                    exit(1)
    # Finally, use values from command line (if they are not empty)
    for key, value in commandline_values.items():
        if key not in variables_name:
            print("Unrecognized variable from command line: " + key)
            exit(1)
        if value:
            variables_value[key] = value
    # Export to _config.py
    with open("_config.py", "w") as f:
        for key, value in variables_value.items():
            if isinstance(value, str):
                writestr(f, key, value)
            if isinstance(value, bool):
                writebool(f, key, value)
    if _config_loaded:
        imp.reload(_config)
