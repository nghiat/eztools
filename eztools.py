##----------------------------------------------------------------------------##
## eztools.py                                                                 ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import argparse
import sys

from eztools.ezdeps.ezdeps import ezdeps


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", choices=["ezdeps"])
    namespace, tool_args = parser.parse_known_args()
    if namespace.tool == "ezdeps":
        ezdeps(tool_args)
    sys.exit(0)
