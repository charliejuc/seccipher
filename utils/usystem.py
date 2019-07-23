import os

_is_windows = os.name == 'nt'
_is_linux = os.name == 'posix'

def is_windows():
    return _is_windows

def is_linux():
    return _is_linux