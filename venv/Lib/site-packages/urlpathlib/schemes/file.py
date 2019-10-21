# Copyright 2017 Morgan Delahaye. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""All the features specific to the file scheme."""

from pathlib import Path
from functools import partial
from urlpathlib.urlpath import PureUrlPath


def _generic(self, _name, *args, **kwargs):
    func = getattr(Path(self.path), _name)
    return func(*args, **kwargs)


stat = partial(_generic, _name='stat')
chmod = partial(_generic, _name='chmod')
exists = partial(_generic, _name='exists')
group = partial(_generic, _name='group')
is_dir = partial(_generic, _name='is_dir')
is_file = partial(_generic, _name='is_file')
is_symlink = partial(_generic, _name='is_symlink')
is_socket = partial(_generic, _name='is_socket')
is_fifo = partial(_generic, _name='is_fifo')
is_block_device = partial(_generic, _name='is_block_device')
is_char_device = partial(_generic, _name='is_char_device')
lchmod = partial(_generic, _name='lchmod')
lstat = partial(_generic, _name='lstat')
mkdir = partial(_generic, _name='mkdir')
open = partial(_generic, _name='open')
owner = partial(_generic, _name='owner')
read_bytes = partial(_generic, _name='read_bytes')
read_text = partial(_generic, _name='read_text')
rmdir = partial(_generic, _name='rmdir')
touch = partial(_generic, _name='touch')
unlink = partial(_generic, _name='unlink')
write_bytes = partial(_generic, _name='write_bytes')
write_text = partial(_generic, _name='write_text')


def expanduser(self):
    cls = type(self)
    return cls(str(_generic(self, 'expanduser')))


def glob(self, pattern):
    cls = type(self)
    return [cls(str(p)) for p in _generic(self, 'glob', pattern)]


def iterdir(self):
    cls = type(self)
    for child in _generic(self, 'iterdir'):
        yield cls(str(child))


def rename(self, target):
    target = target.path if isinstance(target, PureUrlPath) else str(target)
    Path(self.path).rename(target)


def replace(self, target):
    target = target.path if isinstance(target, PureUrlPath) else str(target)
    Path(self.path).replace(target)


def resolve(self, strict=False):
    cls = type(self)
    return cls(str(_generic(self, 'resolve')))


def rglob(self, pattern):
    cls = type(self)
    return [cls(str(p)) for p in _generic(self, 'rglob', pattern)]


def samefile(self, other_path):
    cls = type(self)
    if isinstance(other_path, PureUrlPath) and other.netloc in ('', 'file'):
        return _generic(self, 'samefile', Path(other_path.path))
    return False


def symlink_to(self, target, target_is_directory=False):
    target = target.path if isinstance(target, PureUrlPath) else str(target)
    return _generic(self, 'symlink_to', target, target_is_directory)
