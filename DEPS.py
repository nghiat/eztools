##----------------------------------------------------------------------------##
## DEPS                                                                       ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import _config

deps = []


if _config.is_linux:
    deps.extend([
        {
            "file_name": "gn-linux.tar.xz",
            "folder": ".",
            "url": "https://github.com/nghiat/binaries/raw/master/gn/gn-linux.tar.xz",
            "sha1": "8d7258cec98b816c15b998e2d1136f1a58256e1b"
        },
        {
            "file_name": "ninja-linux-1.8.2.tar.xz",
            "folder": ".",
            "url": "https://github.com/nghiat/binaries/raw/master/ninja-build/ninja-linux-1.8.2.tar.xz",
            "sha1": "498d500a9a749f21a74670933a2cc9847df30526"
        }
    ])
elif _config.is_win:
    deps.extend([
        {
            "file_name": "gn-win.tar.xz",
            "folder": ".",
            "url": "https://github.com/nghiat/binaries/raw/master/gn/gn-win.tar.xz",
            "sha1": "4de49c4497d5ef202acdf79daa16493c3093bfab"
        },
        {
            "file_name": "ninja-win-1.8.2.tar.xz",
            "folder": ".",
            "url": "https://github.com/nghiat/binaries/raw/master/ninja-build/ninja-win-1.8.2.tar.xz",
            "sha1": "493bd091b28c9997223eb6b0a032e295dcdebda1"
        }
    ])
