##----------------------------------------------------------------------------##
## ezdeps_action.py                                                           ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import hashlib
import importlib.machinery
import json
import lzma
import os
import shutil
import tarfile
import urllib.error
import urllib.request


downloaded_deps_file_name = "_ezdeps_downloaded_deps.json"


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
    folder = os.path.dirname(save_path)
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


def get_dep(dep, force_extract=False):
    """If file exists and is sha1 is matched:
       - If force_extract is True, reextract the file if file is an archive.
       - Do nothing otherwise.
       Otherwise, delete and try to download file from url.
    Returns True if there is no error, False otherwise.
    """
    file = dep["file"]
    url = dep["url"]
    sha1 = dep["sha1"]
    file_folder = os.path.dirname(file)
    if os.path.exists(file):
        if verify_sha1(file, sha1):
            if force_extract and has_archive_name(file):
                if extract_tar_xz(file, file_folder):
                    print('Done force extracting "{}"'.format(file))
                else:
                    print('Cannot extract "{}" even when sha1 is matched'
                          .format(file))
                    return False
            print('Processed "{}" successfully'.format(file))
            return True
        else:
            print('File "{}" sha1 is not matched'.format(file))
            if has_archive_name(file):
                delete_extracted_files(file, file_folder)
            print('Deleting "{}"'.format(file))
            os.remove(file)
            print('Redownloading "{}"'.format(file))
    else:
        print('Downloading "{}"'.format(file))
    if not download_file(url, file):
        return False
    print('Downloaded "{}"'.format(file))
    if not verify_sha1(file, sha1):
        print('Failed to verify sha1 of "{}" even after downloading'
              .format(file))
        return False
    if has_archive_name(file) and not extract_tar_xz(file, file_folder):
        print('Cannot extract "{}" even after downloading'.format(file))
        return False
    print('Processed "{}" successfully'.format(file))
    return True


def clean(dep):
    """Delete a file and if the file is an archive,
    then delete all files extracted from that file
    Args:
        file (str): path to file you want to delete
    """
    file = dep["file"]
    print('Cleaning "{}"'.format(file))
    file_folder = os.path.dirname(file)
    if os.path.exists(file):
        if has_archive_name(file):
            delete_extracted_files(file, file_folder)
        print('Deleting "{}"'.format(file))
        os.remove(file)


def load_deps(relpath_to_toplevel, global_deps):
    """Run DEPS.py file in \relpath_to_toplevel.
    Each DEPS.py is a normal python script but there are some important variables:
    - links: path to relative directories to the current DEPS.py file directory
             that contains other DEPS.py files.
    - deps: list of dependencies which are objects like this
            {
                "file": "save file name in same directory as DEPS.py",
                "url": "download url",
                "sha1": "sha1 of the file",
            }
            All objects will be save to global_deps to return to upper level
    Returns:
        Lists of deps of current DEPS.py and all links DEPS.py files.
    """
    deps_path = os.path.join(relpath_to_toplevel, "DEPS.py")
    deps = importlib.machinery.SourceFileLoader(deps_path, deps_path).\
           load_module()
    if hasattr(deps, "links"):
        for link in deps.links:
            global_deps = load_deps(os.path.join(relpath_to_toplevel, link),
                                    global_deps)
    if hasattr(deps, "deps"):
        for dep in deps.deps:
            dep["file"] = os.path.join(relpath_to_toplevel, dep["file"])
            dep["deps_file"] = os.path.join(relpath_to_toplevel, "DEPS.py")
        global_deps.extend(deps.deps)
    return global_deps


def clean_unused_files(deps, dir):
    """Delete files that were in DEPS.py files but not anymore."""
    downloaded_deps_file_path = os.path.join(dir, downloaded_deps_file_name)
    downloaded_deps = []
    if os.path.exists(downloaded_deps_file_path):
        with open(downloaded_deps_file_path, encoding="utf-8") as f:
            downloaded_deps_obj = json.load(f)
        if "deps" in downloaded_deps_obj:
            downloaded_deps = downloaded_deps_obj["deps"]
    for downloaded_dep in downloaded_deps:
        downloaded_file_path = downloaded_dep["file"]
        if os.path.exists(downloaded_file_path):
            need_deleting = True
            for dep in deps:
                if dep["file"] == downloaded_file_path:
                    need_deleting = False
                    break
            if need_deleting:
                if has_archive_name(downloaded_file_path):
                    delete_extracted_files(downloaded_file_path,
                                           os.path.dirname(downloaded_file_path))
                print('Deleting "{}" that is not in any DEPS.py anymore'.
                      format(downloaded_file_path))
                os.remove(downloaded_file_path)


def action_get_deps(deps, dir, force_extract):
    successfull_deps = []
    for dep in deps:
        if get_dep(dep, force_extract):
            successfull_deps.append(dep)
    if len(successfull_deps):
        with open(os.path.join(dir, downloaded_deps_file_name),
                  "w",
                  encoding="utf-8") as f:
            json.dump({"deps": successfull_deps},
                      f,
                      ensure_ascii=False,
                      indent=4)


def action_clean(deps):
    for dep in deps:
        clean(dep)


def run_action(action, dir):
    deps = load_deps(dir, [])
    clean_unused_files(deps, dir)
    # Choose function depends on action once and for all.
    if action == "sync":
        action_get_deps(deps, dir, False)
    elif action == "force-extract":
        action_get_deps(deps, dir, True)
    elif action == "clean":
        action_clean(deps)
