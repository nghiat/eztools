##----------------------------------------------------------------------------##
## eztools/ezdeps/action.py                                                   ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import hashlib
import lzma
import os
import shutil
import tarfile
import urllib.error
import urllib.request

from eztools.ezdeps.utils import import_from_path

tmp_folder_name = ".tmp"


def get_download_path(folder, file_name):
    file_path = os.path.join(folder, file_name)
    if has_archive_name(file_name):
        file_path = os.path.join(tmp_folder_name, file_name)
    return file_path


def calculate_sha1(path):
    hash_sha1 = hashlib.sha1()
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest().lower()


def verify_sha1(path, checksum):
    return calculate_sha1(path) == checksum.lower()


def download_file(url, save_path):
    """Downloads file from url then saves to save_path.
    Returns True if succeeded"""
    folder = os.path.dirname(os.path.abspath(save_path))
    os.makedirs(folder, exist_ok=True)
    try:
        res = urllib.request.urlopen(url)
        with open(save_path, "wb") as f:
            f.write(res.read())
    except (urllib.error.URLError, urllib.error.HTTPError):
        print("Cannot download from: " + url)
        return False
    except IOError:
        print("Cannot save downloaded data to: " + save_path)
        return False
    return True


def extract_tar_xz(tar_xz_path, extract_path):
    if os.path.exists(tar_xz_path):
        try:
            with lzma.open(tar_xz_path) as f:
                with tarfile.open(fileobj=f) as tar:
                    if not os.path.isdir(extract_path):
                        os.makedirs(extract_path)
                    tar.extractall(extract_path)
                    return True
        except (lzma.LZMAError, tarfile.TarError, EOFError):
            pass
    return False


def delete_extracted_files(xz_path, extract_path):
    """Get list of files/folders from an archive and
    try to delete those files/folders if they have been extracted"""
    try:
        with lzma.open(xz_path) as f:
            with tarfile.open(fileobj=f) as tar:
                message = 'Deleting files extracted from "{}"'.format(xz_path)
                has_printed_message = False
                for extracted_file in tar.getnames():
                    extracted_file_path = os.path.join(extract_path,
                                                       extracted_file)
                    if os.path.exists(extracted_file_path):
                        if not has_printed_message:
                            print(message)
                            has_printed_message = True
                        print('Deleting "{}"'.format(extracted_file_path))
                        if os.path.isfile(extracted_file_path):
                            os.remove(extracted_file_path)
                        else:
                            shutil.rmtree(extracted_file_path)
    except (lzma.LZMAError, tarfile.TarError, EOFError):
        return


def has_archive_name(path):
    if path[-2:] == "xz":
        return True
    return False


def get_dep(dep):
    """If the file is not an archive, exists and the hash matches, then do nothing.
    If the file is an archive, exists in |tmp_dir|, and the hash matches, then re-extract the file.
    Otherwise, re-download the file and extract it if it is an archive.
    Returns True if there is no error, False otherwise.
    """
    file_name = dep["file_name"]
    folder = dep["folder"]
    url = dep["url"]
    sha1 = dep["sha1"]
    is_archive = has_archive_name(file_name)
    download_path = get_download_path(folder, file_name)
    if os.path.exists(download_path):
        if verify_sha1(download_path, sha1):
            if is_archive:
                if not extract_tar_xz(download_path, folder):
                    print('Cannot extract "{}" even when sha1 is matched'
                          .format(file_name))
                    return False
            return True
        else:
            print('File "{}" sha1 is not matched'.format(file_name))
            if is_archive:
                delete_extracted_files(download_path, folder)
            os.remove(download_path)
            print('Re-downloading "{}"'.format(file_name))
    else:
        print('Downloading "{}"'.format(file_name))
    if not download_file(url, download_path):
        return False
    print('Downloaded "{}"'.format(file_name))
    if not verify_sha1(download_path, sha1):
        print('Failed to verify sha1 of "{}" even after downloading'
              .format(file_name))
        return False
    if is_archive and not extract_tar_xz(download_path, folder):
        print('Cannot extract "{}" even after downloading'.format(file_name))
        return False
    print('Processed "{}" successfully'.format(file_name))
    return True


def clean(dep):
    """Delete a file and if the file is an archive,
    then delete all files extracted from that file
    Args:
        file (str): path to file you want to delete
    """
    file_name = dep["file_name"]
    folder = dep["folder"]
    is_archive = has_archive_name(file_name)
    download_path = get_download_path(folder, file_name)
    message = 'Deleting "{}"'
    if is_archive:
        message = 'Deleting "{}" and its contents'
    print(message.format(file_name))
    if os.path.exists(download_path):
        if is_archive:
            delete_extracted_files(download_path, folder)
    os.remove(download_path)
    print('Deleted "{}"'.format(file_name))


def load_deps(relpath_to_toplevel, global_deps):
    """Run DEPS.py file in \relpath_to_toplevel.
    Each DEPS.py is a python script but there are some important variables:
    - links: path to relative directories to the current DEPS.py file directory
             that contains other DEPS.py files.
    - deps: list of dependencies which are objects like this
            {
                "file_name": "file_name",
                "folder": "save or extract location which is relative to DEPS.py",
                "url": "download url",
                "sha1": "sha1 of the file",
            }
            All objects will be save to global_deps to return to upper level
    Returns:
        Lists of deps of current DEPS.py and all links DEPS.py files.
    """
    deps_path = os.path.join(relpath_to_toplevel, "DEPS.py")
    deps = import_from_path(deps_path, deps_path)
    if hasattr(deps, "links"):
        for link in deps.links:
            global_deps = load_deps(os.path.join(relpath_to_toplevel, link),
                                    global_deps)
    if hasattr(deps, "deps"):
        for dep in deps.deps:
            dep["folder"] = os.path.join(relpath_to_toplevel, dep["folder"])
            dep["deps_file"] = os.path.join(relpath_to_toplevel, "DEPS.py")
        global_deps.extend(deps.deps)
    return global_deps


def action_get_deps(deps):
    for dep in deps:
        get_dep(dep)


def action_clean(deps):
    for dep in deps:
        clean(dep)


def run_action(action, dir):
    deps = load_deps(dir, [])
    # Choose function depends on action once and for all.
    if action == "sync":
        action_get_deps(deps)
    elif action == "clean":
        action_clean(deps)
