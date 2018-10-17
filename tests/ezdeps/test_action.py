##----------------------------------------------------------------------------##
## tests/ezdeps/test_action.py                                                ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import hashlib
import http.server
import importlib
import lzma
import os
import pytest
import shutil
import socketserver
import tarfile
import threading

import eztools.ezdeps.action as action

port = 8000
server_address = "http://127.0.0.1:{}/".format(port)


def simple_sha1(path):
    hash = hashlib.sha1()
    with open(path, "rb") as f:
        hash.update(f.read())
    return hash.hexdigest().lower()


@pytest.fixture(scope="function")
def file_and_hash():
    file_name = "file"
    file_path = file_name
    with open(file_path, "wb") as f:
        f.write("a".encode("utf-8"))
    yield file_name, file_path, simple_sha1(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture(scope="function")
def xz_file_and_hash(file_and_hash):
    file_name, file_path, hash = file_and_hash
    xz_name = file_name + ".tar.xz"
    tar_path = file_name + ".tar"
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
    return "asdfghjkl"


@pytest.fixture(scope="function")
def empty_folder():
    folder = "test_folder"
    os.makedirs(folder, exist_ok=True)
    yield folder
    shutil.rmtree(folder)


@pytest.fixture(scope="function")
def download_folder():
    folder = "download_folder"
    os.makedirs(folder)
    yield folder
    shutil.rmtree(folder)


@pytest.fixture(scope="function")
def deps_files(file_and_hash, local_server, xz_file_and_hash):
    importlib.invalidate_caches()
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    top_level_deps_dir = ""
    top_level_deps_path = "DEPS.py"
    file_download_name = "tmp_" + file_name
    file_folder_in_deps = "."
    file_download_folder = file_folder_in_deps
    file_download_path = action.get_download_path(file_download_folder,
                                                  file_download_name)
    link_folder_name = "link"
    with open(top_level_deps_path, "w") as f:
        f.write("""
deps = [
    {{
        "file_name": "{0}",
        "folder": "{1}",
        "url": "{2}",
        "sha1": "{3}"
    }}
]
links = [ "{4}" ]""".format(file_download_name, file_folder_in_deps,
                            server_address + file_path, file_hash,
                            link_folder_name))
    link_folder_path = link_folder_name
    os.makedirs(link_folder_path, exist_ok=True)
    link_deps_file_path = os.path.join(link_folder_path, "DEPS.py")
    xz_download_name = "tmp_" + xz_name
    xz_download_folder_in_deps = "."
    xz_download_folder = link_folder_path
    xz_download_path = action.get_download_path(xz_download_folder,
                                                xz_download_name)
    with open(link_deps_file_path, "w") as f:
        f.write("""
deps = [
    {{
        "file_name": "{0}",
        "folder": "{1}",
        "url": "{2}",
        "sha1": "{3}"
    }}
]""".format(xz_download_name, xz_download_folder_in_deps,
            server_address + xz_path, xz_hash))
    # yeilds the actual folder instead of folder relative to DEPS.py file
    yield top_level_deps_dir, \
        [
            {
                "file_name": file_download_name,
                "folder": file_download_folder,
                "url": server_address + file_path,
                "sha1": file_hash
            },
            {
                "file_name": xz_download_name,
                "folder": xz_download_folder,
                "url": server_address + xz_path,
                "sha1": xz_hash
            },
        ]
    if os.path.exists(file_download_path):
        os.remove(file_download_path)
    if os.path.exists(xz_download_path):
        os.remove(xz_download_path)
    os.remove(top_level_deps_path)
    shutil.rmtree(link_folder_path)


def test_calculate_hash_from_path(empty_folder, file_and_hash,
                                  non_existent_path):
    file_name, file_path, file_hash = file_and_hash
    assert action.calculate_sha1(file_path) == file_hash
    assert action.calculate_sha1(non_existent_path) == ""
    assert action.calculate_sha1(empty_folder) == ""


def test_verify_sha1(empty_folder, file_and_hash, non_existent_path):
    file_name, file_path, file_hash = file_and_hash
    assert action.verify_sha1(file_path, file_hash)
    assert action.verify_sha1(non_existent_path, "")
    assert action.verify_sha1(empty_folder, "")


def test_download_file(download_folder, local_server, non_existent_path,
                       xz_file_and_hash):
    save_path = os.path.join(download_folder, "downloaded_file")
    xz_name, xz_path, xz_hash = xz_file_and_hash
    assert action.download_file(server_address + xz_path, save_path)
    assert action.verify_sha1(save_path, xz_hash)
    os.remove(save_path)
    assert not action.download_file(server_address + non_existent_path,
                                    save_path)
    # invalid address
    assert not action.download_file("http:/abc", save_path)


def test_extract_tar_xz(empty_folder, file_and_hash, non_existent_path,
                        xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    assert action.extract_tar_xz(xz_path, empty_folder)
    assert action.verify_sha1(os.path.join(empty_folder, file_name), file_hash)
    assert not action.extract_tar_xz(file_path, empty_folder)
    assert not action.extract_tar_xz(non_existent_path, empty_folder)


def test_delete_extracted_files(empty_folder, file_and_hash, xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    # TODO move this out of here
    extracted_file = os.path.join(empty_folder, file_name)
    assert action.extract_tar_xz(xz_path, empty_folder)
    assert os.path.isfile(extracted_file)
    action.delete_extracted_files(xz_path, empty_folder)
    assert not os.path.exists(extracted_file)


def test_has_archive_name():
    assert action.has_archive_name("abc.xz")
    assert action.has_archive_name("abc.tar.xz")
    assert not action.has_archive_name("file.xzy")


def test_get_dep(empty_folder, file_and_hash, local_server, xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    download_file_address = server_address + xz_path
    download_path = action.get_download_path(empty_folder, xz_name)
    extracted_file = os.path.join(empty_folder, file_name)
    # invalid address
    assert not action.get_dep({
        "file_name": xz_name,
        "folder": empty_folder,
        "url": "http://abc",
        "sha1": xz_hash
    })
    # wrong hash
    assert not action.get_dep({
        "file_name": xz_name,
        "folder": empty_folder,
        "url": download_file_address,
        "sha1": ""
    })
    assert os.path.isfile(download_path)
    os.remove(download_path)
    # correct hash
    assert action.get_dep({
        "file_name": xz_name,
        "folder": empty_folder,
        "url": download_file_address,
        "sha1": xz_hash
    })
    assert os.path.isfile(extracted_file)
    # Change extracted file content
    with open(extracted_file, "w") as f:
        f.write("")
    new_hash = action.calculate_sha1(extracted_file)
    assert (new_hash != file_hash)
    assert action.get_dep({
        "file_name": xz_name,
        "folder": empty_folder,
        "url": download_file_address,
        "sha1": xz_hash
    })
    # Check the new file is overwritten.
    assert action.verify_sha1(extracted_file, file_hash)


def test_clean(empty_folder, file_and_hash, local_server, xz_file_and_hash):
    file_name, file_path, file_hash = file_and_hash
    xz_name, xz_path, xz_hash = xz_file_and_hash
    download_file_address = server_address + xz_path
    download_path = action.get_download_path(empty_folder, xz_name)
    extracted_file = os.path.join(empty_folder, file_name)
    action.get_dep({
        "file_name": xz_name,
        "folder": empty_folder,
        "url": download_file_address,
        "sha1": xz_hash
    })
    assert os.path.isfile(download_path)
    assert os.path.isfile(extracted_file)
    action.clean({"file_name": xz_name, "folder": empty_folder})
    assert not os.path.isfile(download_path)
    assert not os.path.isfile(extracted_file)


def test_sync_action(deps_files):
    top_level_deps_dir, downloaded_files = deps_files
    # sync
    action.run_action("sync", top_level_deps_dir)
    for file in downloaded_files:
        download_path = action.get_download_path(file["folder"],
                                                 file["file_name"])
        assert action.verify_sha1(download_path, file["sha1"])


def test_re_extract(deps_files):
    top_level_deps_dir, downloaded_files = deps_files
    action.run_action("sync", top_level_deps_dir)
    for file in downloaded_files:
        file_name = file["file_name"]
        folder = file["folder"]
        if action.has_archive_name(file_name):
            download_path = action.get_download_path(folder, file_name)
            action.delete_extracted_files(download_path, folder)
    action.run_action("sync", top_level_deps_dir)
    for file in downloaded_files:
        file_name = file["file_name"]
        folder = file["folder"]
        if action.has_archive_name(file_name):
            download_path = action.get_download_path(folder, file_name)
            with lzma.open(download_path) as f:
                with tarfile.open(fileobj=f) as tar:
                    for file_in_archive in tar.getnames():
                        assert os.path.exists(
                            os.path.join(folder, file_in_archive))


def test_archive_download_location(empty_folder, local_server,
                                   xz_file_and_hash):
    xz_name, xz_path, xz_hash = xz_file_and_hash
    action.get_dep({
        "file_name": xz_name,
        "folder": empty_folder,
        "url": server_address + xz_path,
        "sha1": xz_hash
    })
    download_path = os.path.join(action.tmp_folder_name, xz_name)
    assert os.path.exists(download_path)
    os.remove(download_path)
