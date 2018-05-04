##----------------------------------------------------------------------------##
## ezdeps.py                                                                  ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import ezdeps_action
import ezdeps_create__config

import argparse


if __name__ == "__main__":
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
        "action",
        choices=["sync", "force-extract", "update", "clean"],
        default="sync",
        nargs='?')
    args = parser.parse_args()
    ezdeps_create__config.create__config({
        "host_platform": args.host_platform,
        "host_arch": args.host_arch,
        "target_platform": args.target_platform,
        "target_arch": args.target_arch
    }, args.skip_config)
    ezdeps_action.run_action(args.action, args.dir)
