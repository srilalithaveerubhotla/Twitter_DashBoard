# Copyright 2017 Morgan Delahaye. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Various utils."""

from importlib import import_module


SCHEME_ALIAS = {
    '':      'file',
    'https': 'http',
}


def dispatch(meth):
    """A decorator to dispatch a method.

    The dispatch is based on the scheme of the path.
    """
    def wrapper(self, *args, **kwargs):
        scheme = SCHEME_ALIAS.get(self.scheme, self.scheme)

        try:
            module = import_module('urlpathlib.schemes.%s' % scheme)
            func = getattr(module, meth.__name__)
        except (ImportError, AttributeError):
            return meth(self, *args, **kwargs)

        return func(self, *args, **kwargs)

    return wrapper
