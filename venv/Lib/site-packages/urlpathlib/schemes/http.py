# Copyright 2017 Morgan Delahaye. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""All the features specific to the http scheme."""

import urllib.request
import urllib.error
import re


def _dl_text_html_parser(ref, content):
    # extract links from an HTML page.
    match_href = re.compile('<a href="([^"]+)">')
    for match in match_href.findall(content.decode('utf8')):
        yield match


def exists(self):
    request = urllib.request.Request(url=str(self), method='HEAD')
    try:
        urllib.request.urlopen(request)
    except urllib.error.HTTPError:
        return False

    return True


def glob(self, pattern):

    pass


def iterdir(self):

    cls = type(self)

    request = urllib.request.Request(url=str(self), method='HEAD')
    with urllib.request.urlopen(request) as f:
        content_type = f.headers.get_content_type()

    if 'html' in content_type:  # skip non-html pages
        with self.open() as f:
            for match in _dl_text_html_parser(self, f.read()):
                child = cls(match)

                # rebuild the complete url
                if not child.is_absolute():
                    child = self / child

                # ensure the yield depth is 1
                if child.parent == self:
                    yield child


def open(self, mode='rb', buffering=-1, encoding=None, errors=None,
         newline=None):

    if mode != 'rb':
        err_msg = 'http open() only support binary read-only.'
        raise NotImplementedError(err_msg)

    return urllib.request.urlopen(str(self))
