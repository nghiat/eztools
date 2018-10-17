##----------------------------------------------------------------------------##
## tests/ezdeps/test_create__config.py                                        ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import os
import platform
import pytest

import eztools.ezdeps.create__config as createconfig

from eztools.ezdeps.utils import import_from_path


@pytest.fixture(scope="function")
def _config():
    _config_dir = "."
    _config_path = createconfig.config_filename
    if os.path.isfile(_config_path):
        os.remove(_config_path)
    yield _config_dir, _config_path
    if os.path.isfile(_config_path):
        os.remove(_config_path)


def test__config_file_loadable(_config):
    _config_dir, _config_path = _config
    createconfig.create__config(_config_dir, {}, False)
    assert import_from_path(createconfig.config_module_name, _config_path)


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
    createconfig.create__config(_config_dir, {}, False)
    config_module = import_from_path(createconfig.config_module_name,
                                     _config_path)
    assert config_module.target_arch == target_arch


def test_value_from_commnand_line(_config):
    _config_dir, _config_path = _config
    target_arch_value = "abc"
    createconfig.create__config(_config_dir,
                                {"target_arch": target_arch_value}, False)
    config_module = import_from_path(createconfig.config_module_name,
                                     _config_path)
    assert config_module.target_arch == target_arch_value


def test_value_from_file_and_commnand_line(_config):
    _config_dir, _config_path = _config
    target_arch_value_for_file = "abc"
    target_arch_value_for_command_line = "abc"
    with open(_config_path, "w") as f:
        f.write('{} = "{}"'.format("target_arch", target_arch_value_for_file))
    createconfig.create__config(
        _config_dir, {"target_arch": target_arch_value_for_command_line},
        False)
    config_module = import_from_path(createconfig.config_module_name,
                                     _config_path)
    assert config_module.target_arch == target_arch_value_for_command_line
