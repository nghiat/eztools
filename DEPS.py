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
            "file_name": "gn-linux-0.3.2.tar.xz",
            "folder": ".",
            "url": "https://github.com/nghiat/binaries/raw/master/gn/gn-linux-0.3.2.tar.xz",
            "sha1": "8c1e12d706f1868ebaa523ebea49c88115e4b53a"
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
            "file_name": "gn-win-0.3.2.tar.xz",
            "folder": ".",
            "url": "https://github.com/nghiat/binaries/raw/master/gn/gn-win-0.3.2.tar.xz",
            "sha1": "09305c73377795024ef3d5d02f0019c891b79b6c"
        },
        {
            "file_name": "ninja-win-1.8.2.tar.xz",
            "folder": ".",
            "url": "https://github.com/nghiat/binaries/raw/master/ninja-build/ninja-win-1.8.2.tar.xz",
            "sha1": "493bd091b28c9997223eb6b0a032e295dcdebda1"
        }
    ])
