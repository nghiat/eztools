##----------------------------------------------------------------------------##
## test/ezdeps_create__config_test.py                                         ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import os
import platform
import pytest


from ezdeps_create__config import create__config,\
    config_filename,\
    config_module_name
from test_utils import path_from_script_dir
import utils


@pytest.fixture(scope="function")
def _config():
    _config_dir = path_from_script_dir(".")
    _config_path = path_from_script_dir(config_filename)
    if os.path.isfile(_config_path):
        os.remove(_config_path)
    yield _config_dir, _config_path
    if os.path.isfile(_config_path):
        os.remove(_config_path)


def test__config_file_loadable(_config):
    _config_dir, _config_path = _config
    create__config(_config_dir, {}, False)
    assert utils.import_from_path(config_module_name, _config_path)


def test_existing__config_file(_config):
    _config_dir, _config_path = _config
    machine = platform.machine()
    target_arch = ""
    if machine == "i386":
        target_arch = "x64"
    elif machine == "AMD64":
        target_arch = "x86"
    else:
        target_arch = "x86"
    with open(_config_path, "w") as f:
        f.write('{} = "{}"'.format("target_arch", target_arch))
    create__config(_config_dir, {}, False)
    config_module = utils.import_from_path(config_module_name, _config_path)
    assert config_module.target_arch == target_arch


def test_value_from_commnand_line(_config):
    _config_dir, _config_path = _config
    target_arch_value = "abc"
    create__config(_config_dir, {"target_arch": target_arch_value}, False)
    config_module = utils.import_from_path(config_module_name, _config_path)
    assert config_module.target_arch == target_arch_value


def test_value_from_file_and_commnand_line(_config):
    _config_dir, _config_path = _config
    target_arch_value_for_file = "abc"
    target_arch_value_for_command_line = "abc"
    with open(_config_path, "w") as f:
        f.write('{} = "{}"'.format("target_arch", target_arch_value_for_file))
    create__config(_config_dir,
                   {"target_arch": target_arch_value_for_command_line},
                   False)
    config_module = utils.import_from_path(config_module_name, _config_path)
    assert config_module.target_arch == target_arch_value_for_command_line
