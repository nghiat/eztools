##----------------------------------------------------------------------------##
## test/ezdeps_action_test.py                                                 ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import hashlib
import http.server
import importlib
import json
import lzma
import os
import pytest
import shutil
import socketserver
import tarfile
import threading

import ezdeps_action


here = os.path.dirname(os.path.relpath(__file__))
port = 8000
server_address = "http://127.0.0.1:{}/".format(port)


def here_path(path):
    return os.path.join(here, path).replace('\\', '/')


def simple_sha1(path):
    hash = hashlib.sha1()
    with open(path, "rb") as f:
        hash.update(f.read())
    return hash.hexdigest().lower()


@pytest.fixture(scope="function")
def file_and_hash():
    file_name = "file"
    file_path = here_path(file_name)
    with open(file_path, "wb") as f:
        f.write("a".encode("utf-8"))
    yield file_name, file_path, simple_sha1(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture(scope="function")
def xz_file_and_hash(file_and_hash):
    file_name, file_path, hash = file_and_hash
    xz_name = file_name + ".tar.xz"
    tar_path = here_path(file_name + ".tar")
    xz_path = tar_path + ".xz"
    with tarfile.open(tar_path, "w") as tar:
        tar.add(file_path, arcname=file_name)
    with open(tar_path, "rb") as tar:
        with lzma.open(xz_path, "w") as xz:
            xz.write(tar.read())
    os.remove(tar_path)
    yield xz_name, xz_path, simple_sha1(xz_path)
    if os.path.exists(xz_path):
        os.remove(xz_path)


@pytest.fixture(scope="module")
def local_server():
    httpd = socketserver.TCPServer(("", port),
                                   http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=httpd.serve_forever).start()
    yield
    shutdown_thread = threading.Thread(target=httpd.shutdown)
    shutdown_thread.start()
    shutdown_thread.join()


@pytest.fixture(scope="module")
def non_existent_path():
    return here_path("asdfghjkl")


@pytest.fixture(scope="function")
def empty_folder():
    folder = here_path("test_folder")
    os.makedirs(folder, exist_ok=True)
    yield folder
    shutil.rmtree(folder)


@pytest.fixture(scope="function")
def download_folder():
    folder = here_path("download_folder")
    os.makedirs(folder)
    yield folder
    shutil.rmtree(folder)


@pytest.fixture(scope="function")
def deps_files(file_and_hash, local_server, xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    top_level_deps_path = here_path("DEPS.py")
    file_download_name = "tmp_" + file_name
    file_download_path = here_path(file_download_name)
    link_folder_name = "link"
    with open(top_level_deps_path, "w") as f:
        f.write(
            """
deps = [
    {{
        "file": "{0}",
        "url": "{1}",
        "sha1": "{2}"
    }}
]
links = [ "{3}" ]""".format(file_download_name,
                            server_address + file_path,
                            file_hash,
                            link_folder_name))
    link_folder_path = here_path(link_folder_name)
    os.makedirs(link_folder_path, exist_ok=True)
    link_deps_file_path = os.path.join(link_folder_path, "DEPS.py")
    xz_download_name = "tmp_" + xz_name
    xz_download_path = os.path.join(link_folder_path, xz_download_name)
    with open(link_deps_file_path, "w") as f:
        f.write(
            """
deps = [
    {{
        "file": "{0}",
        "url": "{1}",
        "sha1": "{2}"
    }}
]""".format(xz_download_name, server_address + xz_path, xz_hash))
    yield os.path.dirname(top_level_deps_path), \
        [
            {
                "file": file_download_path,
                "url": server_address + file_path,
                "sha1": file_hash
            },
            {
                "file": xz_download_path,
                "url": server_address + xz_path,
                "sha1": xz_hash
            },
        ]
    if os.path.exists(file_download_path):
        os.remove(file_download_path)
    if os.path.exists(xz_download_path):
        os.remove(xz_download_path)
    os.remove(top_level_deps_path)
    downloaded_deps_file_path = here_path(ezdeps_action.downloaded_deps_file_name)
    if os.path.exists(downloaded_deps_file_path):
        os.remove(downloaded_deps_file_path)
    shutil.rmtree(link_folder_path)


@pytest.fixture(scope="function")
def _ez_downloaded_deps_json(deps_files, file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    top_deps_dir, downloaded_files = deps_files
    will_be_deleted_file_name = file_name + "_will_be_deleted"
    will_be_deleted_file_path = here_path(will_be_deleted_file_name)
    will_be_deleted_file = {
        "file": will_be_deleted_file_path,
        "url": server_address + file_path
    }
    exported_files = downloaded_files[:]
    exported_files.append(will_be_deleted_file)
    json_path = os.path.join(top_deps_dir,
                             ezdeps_action.downloaded_deps_file_name)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"deps": exported_files}, f, ensure_ascii=False, indent=4)
    yield will_be_deleted_file
    if os.path.exists(will_be_deleted_file_path):
        os.remove(will_be_deleted_file_path)
    os.remove(json_path)


def test_calculate_hash_from_path(empty_folder,
                                  file_and_hash,
                                  non_existent_path):
    file_name, file_path, file_hash = file_and_hash
    assert ezdeps_action.calculate_sha1(file_path) == file_hash
    assert ezdeps_action.calculate_sha1(non_existent_path) == ""
    assert ezdeps_action.calculate_sha1(empty_folder) == ""


def test_verify_sha1(empty_folder, file_and_hash, non_existent_path):
    file_name, file_path, file_hash = file_and_hash
    assert ezdeps_action.verify_sha1(file_path, file_hash)
    assert ezdeps_action.verify_sha1(non_existent_path, "")
    assert ezdeps_action.verify_sha1(empty_folder, "")


def test_download_file(download_folder,
                       local_server,
                       non_existent_path,
                       xz_file_and_hash):
    save_path = os.path.join(download_folder, "downloaded_file")
    xz_name, xz_path, xz_hash = xz_file_and_hash
    assert ezdeps_action.download_file(server_address + xz_path, save_path)
    assert ezdeps_action.verify_sha1(save_path, xz_hash)
    os.remove(save_path)
    assert not ezdeps_action.download_file(server_address + non_existent_path,
                                           save_path)
    # invalid address
    assert not ezdeps_action.download_file("http:/abc", save_path)


def test_extract_tar_xz(empty_folder,
                        file_and_hash,
                        non_existent_path,
                        xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    assert ezdeps_action.extract_tar_xz(xz_path, empty_folder)
    assert ezdeps_action.verify_sha1(os.path.join(empty_folder, file_name),
                                     file_hash)
    assert not ezdeps_action.extract_tar_xz(file_path, empty_folder)
    assert not ezdeps_action.extract_tar_xz(non_existent_path, empty_folder)


def test_delete_extracted_files(empty_folder, file_and_hash, xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    # TODO move this out of here
    extracted_file = os.path.join(empty_folder, file_name)
    assert ezdeps_action.extract_tar_xz(xz_path, empty_folder)
    assert os.path.isfile(extracted_file)
    ezdeps_action.delete_extracted_files(xz_path, empty_folder)
    assert not os.path.exists(extracted_file)


def test_has_archive_name():
    assert ezdeps_action.has_archive_name("abc.xz")
    assert ezdeps_action.has_archive_name("abc.tar.xz")
    assert not ezdeps_action.has_archive_name("file.xzy")


def test_get_dep(empty_folder, file_and_hash, local_server, xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    download_file_address = server_address + xz_path
    save_path = os.path.join(empty_folder, xz_name)
    extracted_file = os.path.join(empty_folder, file_name)
    # invalid address
    assert not ezdeps_action.get_dep({"file": save_path,
                                      "url": "http://abc",
                                      "sha1": xz_hash})
    # wrong hash
    assert not ezdeps_action.get_dep({"file": save_path,
                                      "url": download_file_address,
                                      "sha1": ""})
    assert os.path.isfile(save_path)
    os.remove(save_path)
    # correct hash
    assert ezdeps_action.get_dep({"file": save_path,
                                  "url": download_file_address,
                                  "sha1": xz_hash})
    assert os.path.isfile(extracted_file)
    # Change extracted file content
    with open(extracted_file, "w") as f:
        f.write("")
    new_hash = ezdeps_action.calculate_sha1(extracted_file)
    assert ezdeps_action.get_dep({"file": save_path,
                                  "url": download_file_address,
                                  "sha1": xz_hash})
    # Check the file is not overwritten.
    assert ezdeps_action.verify_sha1(extracted_file, new_hash)
    # Force extract
    assert ezdeps_action.get_dep({"file": save_path,
                                  "url": download_file_address,
                                  "sha1": xz_hash},
                                 True)
    # Check the file is overwritten.
    assert ezdeps_action.verify_sha1(extracted_file, file_hash)


def test_clean(empty_folder, file_and_hash, local_server, xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    download_file_address = server_address + xz_path
    save_path = os.path.join(empty_folder, xz_name)
    extracted_file = os.path.join(empty_folder, file_name)
    ezdeps_action.get_dep({"file": save_path,
                           "url": download_file_address,
                           "sha1": xz_hash})
    assert os.path.isfile(save_path)
    assert os.path.isfile(extracted_file)
    ezdeps_action.clean({"file": save_path})
    assert not os.path.isfile(save_path)
    assert not os.path.isfile(extracted_file)


def test_sync_action(deps_files):
    top_deps_dir, downloaded_files = deps_files
    # sync
    ezdeps_action.run_action("sync", top_deps_dir)
    for file in downloaded_files:
        assert ezdeps_action.verify_sha1(file["file"], file["sha1"])


def test_clean_unused_files(_ez_downloaded_deps_json, deps_files):
    top_deps_dir, downloaded_files = deps_files
    will_be_deleted_file = _ez_downloaded_deps_json
    for file in downloaded_files:
        ezdeps_action.download_file(file["url"], file["file"])
    ezdeps_action.download_file(will_be_deleted_file["url"],
                                will_be_deleted_file["file"])
    ezdeps_action.run_action("sync", top_deps_dir)
    assert not os.path.exists(will_be_deleted_file["file"])


def test_force_extract(deps_files):
    top_deps_dir, downloaded_files = deps_files
    ezdeps_action.run_action("sync", top_deps_dir)
    for file in downloaded_files:
        if ezdeps_action.has_archive_name(file["file"]):
            ezdeps_action.delete_extracted_files(file["file"],
                                                 os.path.dirname(file["file"]))
    ezdeps_action.run_action("force-extract", top_deps_dir)
    for file in downloaded_files:
        if ezdeps_action.has_archive_name(file["file"]):
            archive_dir = os.path.dirname(file["file"])
            with lzma.open(file["file"]) as f:
                with tarfile.open(fileobj=f) as tar:
                    for file_in_archive in tar.getnames():
                        assert os.path.exists(os.path.join(archive_dir,
                                                           file_in_archive))
