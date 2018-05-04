# What is ezdeps?
ezdeps is a script used to manage binaries file for a project.
# How does it work?
ezdeps runs DEPS file in current directory (or you can pass a directory using -d or --dir)
Each DEPS file is just a normal python script, but there are some important variables:
* links: path to relative directories to the current DEPS file directory that contains other DEPS files.
* deps: list of dependencies which are objects like this
```
{
    "file": "save file name in same directory as DEPS",
    "url": "download url",
    "sha1": "sha1 of the file",
}
```
* Before top level DEPS file is run, ezdeps create _config.py that contains following variables that can be used in DEPS file:
```
host_platform = str
host_arch = str
target_platform = str
target_arch = str
is_win = bool
is_linux = bool
```
Variables can can be set from multiple places, so the priorities are:

default < existing value in file < command line

You can skip loading value from _config.py (force recreate _config.py) by using flag --skip_config