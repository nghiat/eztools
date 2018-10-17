##----------------------------------------------------------------------------##
## eztools/ezdeps/ezdeps.py                                                   ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import argparse

from eztools.ezdeps.action import run_action
from eztools.ezdeps.create__config import create__config


def ezdeps(args):
    parser = argparse.ArgumentParser(description="Binaries management tool.")
    parser.add_argument(
        "-d",
        "--dir",
        default=".",
        help="Directory contains top level DEPS file"
        " (default to current directory)",
        type=str)
    parser.add_argument(
        "--host-platform",
        choices=["win", "linux"],
        default="",
        help="Host platform (default to current platform)",
        type=str)
    parser.add_argument(
        "--host-arch",
        choices=["x86", "x64"],
        default="",
        help="Host architecture (default to current architecture)",
        type=str)
    parser.add_argument(
        "--target-platform",
        choices=["win", "linux"],
        default="",
        help="Target platform (default to current platform)",
        type=str)
    parser.add_argument(
        "--target-arch",
        choices=["x86", "x64"],
        default="",
        help="Target architecture (default to current architecture)",
        type=str)
    parser.add_argument(
        "--skip-config",
        action="store_true",
        default=False,
        help="Target architecture (default to current architecture)")
    parser.add_argument(
        "action", choices=["sync", "clean"], default="sync", nargs='?')
    parsed_args = parser.parse_args(args)
    create__config(
        ".", {
            "host_platform": parsed_args.host_platform,
            "host_arch": parsed_args.host_arch,
            "target_platform": parsed_args.target_platform,
            "target_arch": parsed_args.target_arch
        }, parsed_args.skip_config)
    run_action(parsed_args.action, parsed_args.dir)
