##----------------------------------------------------------------------------##
## utils.py                                                                   ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import os


def path_from_script_dir(path):
    """Join |path| to current working directory path"""
    here = os.path.dirname(os.path.relpath(__file__))
    return os.path.join(here, path).replace('\\', '/')
