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
            "file": "gn-linux.tar.xz",
            "url": "https://github.com/nghiat/binaries/raw/master/gn/gn-linux-0.3.2.tar.xz",
            "sha1": "d4b266fb261bba839aba26b77dbd7c93eaf9097a"
        },
        {
            "file": "ninja-linux.tar.xz",
            "url": "https://github.com/nghiat/binaries/raw/master/ninja-build/ninja-linux-1.8.2.tar.xz",
            "sha1": "498d500a9a749f21a74670933a2cc9847df30526"
        }
    ])
elif _config.is_win:
    deps.extend([
        {
            "file": "gn-win.tar.xz",
            "url": "https://github.com/nghiat/binaries/raw/master/gn/gn-win-0.3.2.tar.xz",
            "sha1": "922f21278f2bd2ea31a89eea75fc3c4aab759d64"
        },
        {
            "file": "ninja-win.tar.xz",
            "url": "https://github.com/nghiat/binaries/raw/master/ninja-build/ninja-win-1.8.2.tar.xz",
            "sha1": "493bd091b28c9997223eb6b0a032e295dcdebda1"
        }
    ])
