# Copyright 2017 Morgan Delahaye. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Implementation of the UrlPath object."""

import os
import sys
import fnmatch
from urllib.parse import urlparse
from urlpathlib.utils import dispatch

# TODO: handle params, query and fragment in URLs.


class PureUrlPath:
    """PureUrlPath represents a local or remote resource as a filesystem path.

    PureUrlPath offers operation which don't imply any actual I/O operations.
    """

    sep = '/'

    def __new__(cls, *args):
        """Create a new PureUrlPath instance."""
        parts = cls._parse_args(args)
        rv = object.__new__(cls)
        rv.scheme, rv.netloc, rv._root, rv._parsed = rv._parse_parts(parts)
        return rv

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        # scheme transparency for file:
        parts = self.parts if self.scheme else ('file:',) + self.parts
        o_parts = other.parts if other.scheme else ('file:',) + other.parts

        return parts == o_parts

    def __truediv__(self, other):

        parts = list(self.parts)
        parts += self._parse_args((other,))

        cls = type(self)
        return cls(*parts)

    def __str__(self):
        return self._format_parsed_parts(
            self.scheme, self.netloc, self.root, self._parsed)

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self)

    def _parser(self, part):
        # Parse a URL part.
        # Return a tuple scheme, netloc, root, path
        sep = self.sep

        url = urlparse(part)
        if url.netloc or url.scheme or (url.path and url.path[0] == sep):
            return url.scheme, url.netloc, sep, url.path.lstrip(sep)

        return '', '', '', url.path

    @classmethod
    def _format_parsed_parts(cls, scheme, netloc, root, parts):
        rv = '%s%s' % (root, cls.sep.join(parts))
        if scheme or netloc:
            rv = '%s://%s%s' % (scheme, netloc, rv)
        return rv

    @classmethod
    def _parse_args(cls, args):
        parts = []
        for a in args:
            if isinstance(a, cls):
                parts += a.parts
            elif isinstance(a, str):
                # handle str subclasses
                parts.append(str(a))
            else:
                err_msg = 'argument should be a path or str object, not %r'
                raise TypeError(err_msg % type(a))
        return parts

    def _search_scheme(self, parts):
        scheme = ''
        it = reversed(parts)
        for part in it:
            if not part:
                continue
            scheme = self._parser(part)[0]
            if scheme:
                break

        return scheme

    def _search_netloc(self, parts):
        netloc = ''
        it = reversed(parts)
        for part in it:
            if not part:
                continue
            netloc = self._parser(part)[1]
            if netloc:
                break

        return netloc

    def _parse_parts(self, parts):
        parsed = []
        sep = self.sep
        scheme = netloc = root = ''
        it = reversed(parts)

        for part in it:
            if not part:
                continue

            scheme, netloc, root, rel = self._parser(part)
            if sep in rel:
                for x in reversed(rel.split(sep)):
                    if x and x != '.':
                        parsed.append(sys.intern(x))
            elif rel and rel != '.':
                parsed.append(sys.intern(rel))

            if root:
                # Search for a scheme or netloc if none are set when the root
                # has been found.
                if not (scheme and netloc):
                    scheme = self._search_scheme(parts)
                    netloc = self._search_netloc(parts)

                break

        parsed.reverse()
        return scheme, netloc, root, parsed

    @property
    def root(self):
        """Return the root of the path."""
        return getattr(self, '_root', '')

    @property
    def name(self):
        """A string representing the final path component."""
        if len(self._parsed) > 1:
            return self._parsed[-1]
        return ''

    @property
    def parent(self):
        """The logical parent of the path."""
        rv = tuple(self._parsed)[:-1]

        if self.root:
            rv = (self.root, ) + rv

        if self.netloc:
            rv = ('//%s' % self.netloc,) + rv

        if self.scheme:
            rv = ('%s:' % self.scheme,) + rv

        cls = type(self)
        return cls(*rv)

    @property
    def parents(self):
        """An immutable sequence providing access to the logical ancestors."""
        rv = []
        current = self.parent
        while current not in rv:
            rv.append(current)
            current = current.parent
        return tuple(rv)

    @property
    def parts(self):
        """A tuple giving access to the path’s various components."""
        rv = tuple(self._parsed)

        if self.root:
            rv = (self.root, ) + rv

        if self.netloc:
            rv = ('//%s' % self.netloc,) + rv

        if self.scheme:
            rv = ('%s:' % self.scheme,) + rv

        return rv

    @property
    def path(self):
        """The path of the resource."""
        return self.root + self.sep.join(self._parsed)

    @property
    def stem(self):
        """The final path component, without its suffix."""
        return self.name.rsplit('.', maxsplit=1)[0]

    @property
    def suffix(self):
        """The file extension of the final component."""
        return ([''] + self.suffixes)[-1]

    @property
    def suffixes(self):
        """A list of the path’s file extensions."""
        return ['.%s' % s for s in self.name.split('.')[1:] if s]

    def as_uri(self):
        """Return whether the path is absolute or not."""
        if not self.is_absolute():
            raise ValueError('relative path can\'t be expressed as a file URI')
        scheme = self.scheme or 'file'

        rv = '%s%s' % (self.root, self.sep.join(self._parsed))
        return '%s://%s%s' % (scheme, self.netloc, rv)

    def _casefold(self, value):
        return value.lower()

    def _casefold_parts(self, parts):
        return [p.lower() for p in parts]

    def is_absolute(self):
        """Return whether the path is absolute or not."""
        return bool(self.root)

    def joinpath(self, *args):
        """Join multiple path."""
        parts = list(self.parts)
        parts += self._parse_args(args)

        cls = type(self)
        return cls(*parts)

    def match(self, pattern):
        """Match this path against the provided glob-style pattern."""
        cf = self._casefold

        pattern = cf(pattern)
        scheme, netloc, root, pat_parsed = self._parse_parts((pattern,))
        if not pat_parsed:
            raise ValueError('empty pattern')

        # scheme transparency: self.scheme = '' <=> 'file'
        if scheme and scheme != (cf(self.scheme) or 'file'):
            return False

        if netloc and netloc != cf(self.netloc):
            return False

        parts = self._parsed
        if root and len(pat_parsed) != len(parts):
            return False
        elif len(pat_parsed) > len(parts):
            return False

        for part, pat in zip(reversed(parts), reversed(pat_parsed)):
            if not fnmatch.fnmatchcase(part, pat):
                return False

        return True

    def relative_to(self, *other):
        """Compute a version of this path relative to the other path."""
        if not other:
            raise TypeError('need at least one argument')

        parts = self._parsed
        root = self.root
        netloc = self.netloc
        scheme = self.scheme or 'file'

        if root:
            abs_parts = [scheme, netloc, root] + parts
        else:
            abs_parts = parts

        parts = self._parse_args(other)
        to_scheme, to_netloc, to_root, to_parts = self._parse_parts(parts)
        if to_root:
            to_abs_parts = [to_scheme or 'file', to_netloc, to_root] + to_parts
        else:
            to_abs_parts = to_parts

        n = len(to_abs_parts)
        cf = self._casefold_parts

        if root if n == 0 else cf(abs_parts[:n]) != cf(to_abs_parts):
            formatted = self._format_parsed_parts(
                to_scheme, to_netloc, to_root, to_parts)
            err_msg = '%r does not start with %r'
            raise ValueError(err_msg % (str(self), str(formatted)))

        cls = type(self)
        return cls(root if n == 1 else '', *abs_parts[n:])

    def with_name(self, name):
        """Return a new path with the name changed."""
        if self.parent == self:
            raise ValueError('%r has an empty name' % self)
        return self.parent / name

    def with_suffix(self, suffix):
        """Return a new path with the suffix changed."""
        return self.with_name(self.stem + suffix)


class UrlPath(PureUrlPath):

    @classmethod
    def cwd(cls):
        """Return a new path object representing the current directory."""
        return cls(os.getcwd())

    @classmethod
    def home(cls):
        """Return a new path object representing the user’s home directory."""
        return cls(os.path.expanduser('~'))

    @dispatch
    def touch(self, mode=0o666, exist_ok=True):
        """Create a file at this given path.

        If mode is given, it is combined with the process’ umask value to
        determine the file mode and access flags. If the file already exists,
        the function succeeds if exist_ok is true (and its modification time is
        updated to the current time), otherwise FileExistsError is raised.
        """
        err_msg = 'touch() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def stat(self):
        """Return information about this path."""
        err_msg = 'stat() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def chmod(self, mode):
        """Change the file mode and permissions."""
        err_msg = 'chmod() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def exists(self):
        """Whether the path points to an existing file or directory."""
        err_msg = 'exists() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def group(self):
        """Return the name of the group owning the file."""
        err_msg = 'group() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def is_dir(self):
        """Return True if the path points to a directory."""
        err_msg = 'is_dir() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def is_file(self):
        """Return True if the path points to a regular file."""
        err_msg = 'is_file() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def is_symlink(self):
        """Return True if the path points to a symbolic link."""
        err_msg = 'is_symlink() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def is_socket(self):
        """Return True if the path points to a Unix socket."""
        err_msg = 'is_socket() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def is_fifo(self):
        """Return True if the path points to a FIFO."""
        err_msg = 'is_fifo() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def is_block_device(self):
        """Return True if the path points to a block device."""
        err_msg = 'is_block_device() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def is_char_device(self):
        """Return True if the path points to a character device."""
        err_msg = 'is_char_device() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def lchmod(self, mode):
        """Change the file mode and permissions. Does not follow symlinks."""
        err_msg = 'lchmod() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def lstat(self):
        """Return information about this path. Does not follow symlinks."""
        err_msg = 'lstat() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """Create a new directory at this given path."""
        err_msg = 'mkdir() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def open(self, mode='r', buffering=-1, encoding=None, errors=None,
             newline=None):
        """Open the file pointed to by the path."""
        err_msg = 'open() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def owner(self):
        """Return the name of the user owning the file."""
        err_msg = 'owner() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def read_bytes(self):
        """Return the binary contents of the pointed-to file as bytes."""
        err_msg = 'read_bytes() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def read_text(self, encoding=None, errors=None):
        """Return the binary contents of the pointed-to file as a string."""
        err_msg = 'read_text() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def rmdir(self):
        """Remove this directory. The directory must be empty."""
        err_msg = 'rmdir() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def unlink(self):
        """Remove this file or symbolic link.

        If the path points to a directory, use Path.rmdir() instead.
        """
        err_msg = 'unlink() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def write_bytes(self, data):
        """Open the file in bytes mode, write data to it, and close it."""
        err_msg = 'write_bytes() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def write_text(self, data):
        """Open the file in text mode, write data to it, and close it."""
        err_msg = 'write_text() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def expanduser(self):
        """Return a new path with expanded ~ and ~user constructs."""
        err_msg = 'expanduser() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def glob(self, pattern):
        """Glob the given pattern in this path, yielding all matching files."""
        err_msg = 'glob() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def iterdir(self):
        """Yield path objects of the directory contents."""
        err_msg = 'iterdir() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def rename(self, target):
        """Rename this file or directory to the given target."""
        err_msg = 'rename() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def replace(self, target):
        """Rename this file or directory to the given target."""
        err_msg = 'replace() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def resolve(self, strict=False):
        """Make the path absolute, resolving any symlinks."""
        err_msg = 'resolve() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def rglob(self, pattern):
        """Like Path.glob() with “**” added in front of the given pattern."""
        err_msg = 'rglob() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def samefile(self, other_path):
        """Return whether this path points to the same file as other_path."""
        err_msg = 'samefile() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)

    @dispatch
    def symlink_to(self, target, target_is_directory=False):
        """Make this path a symbolic link to target."""
        err_msg = 'symlink_to() is not available for %r scheme.'
        raise NotImplementedError(err_msg % self.scheme)
