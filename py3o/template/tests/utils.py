import sys
from contextlib import ExitStack

if sys.version_info >= (3, 9):
    from importlib.resources import as_file, files
else:
    from importlib_resources import as_file, files

file_manager = ExitStack()


def resource_filename(package, path):
    ref = files(package) / path
    return file_manager.enter_context(as_file(ref))
