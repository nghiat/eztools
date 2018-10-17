##----------------------------------------------------------------------------##
## eztools/ezdeps/utils.py                                                    ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import importlib
import importlib.util
import os


def import_from_path(module_name, path):
    """Dynamically load module from path. This function also deletes
    the cached file to update changes in the source files so it's expected
    to have performance hit."""
    # Remove cached
    cache_path = importlib.util.cache_from_source(path)
    if os.path.isfile(cache_path):
        os.remove(cache_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
