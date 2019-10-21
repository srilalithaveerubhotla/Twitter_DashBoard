# -*- coding: utf-8 -*-
"""
Test suite for :mod:`unittest_resources`.

Not part of the public API.

This :class:`unittest.TestCase`-based test classes can serve
as an example on how code style from any module can be covered using
:mod:`unittest_resources.testing`.
"""

import re

import unittest_resources.testing as bases


class TypingTestCase(bases.TypingTestCase):
    """TestCase checking :mod:`mypy`."""

    meta_module = 'unittest_resources'


class CodeStyleTestCase(bases.CodeStyleTestCase):
    """TestCase checking :mod:`pycodestyle`."""

    meta_module = 'unittest_resources'


class DocStyleTestCase(bases.DocStyleTestCase):
    """TestCase checking :mod:`pydocstyle`."""

    meta_module = 'unittest_resources'
    meta_module_pattern = re.compile(r'^meta_module(?!.tests)')


class MaintainabilityIndexTestCase(bases.MaintainabilityIndexTestCase):
    """TestCase checking :mod:`radon` maintainability index."""

    meta_module = 'unittest_resources'


class CodeComplexityTestCase(bases.CodeComplexityTestCase):
    """TestCase checking :mod:`radon` code complexity."""

    meta_module = 'unittest_resources'
    max_class_complexity = 8
    max_function_complexity = 6
