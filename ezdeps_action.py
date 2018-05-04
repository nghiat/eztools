##----------------------------------------------------------------------------##
## ezdeps_action.py                                                           ##
##                                                                            ##
## This file is distributed under the MIT License.                            ##
## See LICENSE.txt for details.                                               ##
## Copyright (C) Tran Tuan Nghia <trantuannghia95@gmail.com> 2018             ##
##----------------------------------------------------------------------------##

import hashlib
import imp
import lzma
import os
import shutil
import tarfile
import urllib.error
import urllib.request


def calculate_sha1(path):
    hash_sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest().lower()


def verify_sha1(path, checksum):
    return calculate_sha1(path) == checksum.lower()


def download_file(url, save_path):
    """Downloads file from url then saves to save_path.
    Returns True if succeeded"""
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


def extract_xz(xz_path, extract_path):
    if os.path.exists(xz_path):
        try:
            with lzma.open(xz_path) as f:
                with tarfile.open(fileobj=f) as tar:
                    tar.extractall(extract_path)
        except (lzma.LZMAError, tarfile.TarError, EOFError):
            return False
    return True


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


def get_dep(file, url, sha1, force_extract=False):
    """If file exists and is sha1 is matched:
       - If force_extract is True, reextract the file if file is an archive.
       - Do nothing otherwise.
       Otherwise, delete and try to download file from url.
    Returns True if there is no error, False otherwise.
    """
    file_folder = os.path.dirname(file)
    if os.path.exists(file):
        if verify_sha1(file, sha1):
            if force_extract and has_archive_name(file):
                if extract_xz(file, file_folder):
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
    if has_archive_name(file) and not extract_xz(file, file_folder):
        print('Cannot extract "{}" even after downloading'.format(file))
        return False
    print('Processed "{}" successfully'.format(file))
    return True


def force_update(file, url):
    """Deletes existing file and files extracted from deleted file.
    Downloads file from url then return the downloaded file hash.
    Returns empty string if there is any error."""
    print('Force updating "{}"'.format(file))
    file_folder = os.path.dirname(file)
    if os.path.exists(file):
        if has_archive_name(file):
            delete_extracted_files(file, file_folder)
        print('Deleting "{}"'.format(file))
        os.remove(file)
    print('Downloading "{}"'.format(file))
    if not download_file(url, file):
        return ""
    if has_archive_name(file) and not extract_xz(file, file_folder):
        print('Cannot extract "{}" even after downloading'.format(file))
        return ""
    print('Forced update "{}" successfully'.format(file))
    return calculate_sha1(file)


def clean(file):
    """Delete a file and if the file is an archive,
    then delete all files extracted from that file
    Args:
        file (str): path to file you want to delete
    """
    print('Cleaning "{}"'.format(file))
    file_folder = os.path.dirname(file)
    if os.path.exists(file):
        if has_archive_name(file):
            delete_extracted_files(file, file_folder)
        print('Deleting "{}"'.format(file))
        os.remove(file)


def load_deps(relpath_to_toplevel, global_deps=[]):
    """Run DEPS file in \relpath_to_toplevel.
    Each DEPS is a normal python script but there are some important variables:
    - links: path to relative directories to the current DEPS file directory
             that contains other DEPS files.
    - deps: list of dependencies which are objects like this
            {
                "file": "save file name in same directory as DEPS",
                "url": "download url",
                "sha1": "sha1 of the file",
            }
            All objects will be save to global_deps to return to upper level
    Returns:
        Lists of deps of current DEPS and all links DEPS files.
    """
    deps_path = os.path.join(relpath_to_toplevel, "DEPS")
    deps = imp.load_source(deps_path, deps_path)
    if hasattr(deps, "links"):
        for link in deps.links:
            global_deps = load_deps(os.path.join(relpath_to_toplevel, link),
                                    global_deps)
    if hasattr(deps, "deps"):
        for dep in deps.deps:
            dep["file"] = os.path.join(relpath_to_toplevel, dep["file"])
        global_deps.extend(deps.deps)
    return global_deps


def run_action(action, dir):
    deps = load_deps(dir)
    # Choose function depends on action once and for all.
    if action == "sync":
        def action_function(file, url, sha1): get_dep(file, url, sha1)
    elif action == "force-extract":
        def action_function(file, url, sha1): get_dep(file, url, sha1, True)
    elif action == "update":
        def action_function(file, url, sha1): force_update(file, url)
    elif action == "clean":
        def action_function(file, url, sha1): clean(file)
    for dep in deps:
        action_function(dep["file"], dep["url"], dep["sha1"])
