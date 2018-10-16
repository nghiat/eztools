##----------------------------------------------------------------------------##
## utils.py                                                                   ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import os


def path_from_cwd(path):
    """Join path from cwd to script directory and |path|"""
    cwd_to_script = os.path.dirname(os.path.relpath(__file__))
    return os.path.join(cwd_to_script, path).replace('\\', '/')
