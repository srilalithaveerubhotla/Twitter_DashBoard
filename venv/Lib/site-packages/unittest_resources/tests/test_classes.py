# -*- coding: utf-8 -*-
"""Test suite for :mod:`unittest_resources`. Not part of the public API."""

import sys
import os
import os.path
import shutil
import io
import contextlib
import re
import tempfile
import unittest

import six

import unittest_resources
import unittest_resources.testing

try:  # python 3.5+
    import typing
except ImportError:
    pass

try:  # python 3.7+
    import importlib.resources as res
except ImportError:
    import importlib_resources as res  # type: ignore  # noqa


class TestResourceTestMeta(unittest.TestCase):
    """TestCase covering :class:` unittest_resources.ResourceTestMeta`."""

    meta_class = unittest_resources.ResourceTestMeta

    def test_resource_methods(self):
        class MyTestCase(six.with_metaclass(self.meta_class)):
            pass

        for name in self.meta_class.resource_methods:
            method = getattr(MyTestCase, name, None)
            self.assertTrue(callable(method))
            self.assertIs(method, getattr(res, name))

    def test_resource_test(self):
        class MyTestCase(six.with_metaclass(self.meta_class)):
            meta_module = 'unittest_resources.tests'
            meta_prefix = 'checking'
            meta_resource_pattern = re.compile(r'\.py$')

        method = getattr(MyTestCase, 'test_checking_test_classes_py', None)
        self.assertTrue(callable(method))

    def test_resource_skip(self):
        class MyTestCase(six.with_metaclass(self.meta_class)):
            meta_module = 'unittest_resources.tests'
            meta_prefix = 'checking'
            meta_resource_pattern = re.compile(r'\.java$')

        self.assertFalse(hasattr(MyTestCase, 'test_checking_test_classes_py'))


class TestResourceTestCase(unittest.TestCase):
    """TestCase covering :class:` unittest_resources.ResourceTestCase`."""

    base_class = unittest_resources.ResourceTestCase

    def test_abstract(self):
        class MyTestCase(self.base_class):
            def runTest(self):
                pass

            meta_module = 'unittest_resources.tests'
            meta_prefix = 'not_implemented'
            meta_resource_pattern = re.compile(r'\.py$')

        with self.assertRaises(NotImplementedError):
            MyTestCase().test_not_implemented_test_classes_py()


class TestBaseClass(unittest.TestCase):
    """TestCase covering :mod:` unittest_resources.testing` classes."""

    module = unittest_resources.testing

    def dedent(self, data):
        # type: (str) -> str
        lines = data.splitlines(True)
        base = min(
            len(line) - len(line.lstrip())
            for line in lines
            if line.strip()
            )
        return ''.join(line[base:] for line in lines)

    @contextlib.contextmanager
    def create_module(self, data):
        # type: (typing.Dict[str, str]) -> typing.Generator[str, None, None]
        directory = tempfile.mkdtemp()
        try:
            for path, content in data.items():
                path = os.path.join(directory, path)
                dirname = os.path.dirname(path)
                if dirname and not os.path.exists(dirname):
                    os.makedirs(dirname)

                if six.PY2:
                    content = content.decode('utf-8')

                with io.open(path, 'w', encoding='utf-8') as f:
                    f.writelines(self.dedent(content))
            try:
                sys.path.insert(0, directory)
                yield directory
            finally:
                sys.path.remove(directory)
        finally:
            shutil.rmtree(directory)

    def test_complexity_index(self):
        data = {
            'complex_module/__init__.py': '''
                def my_fnc(*values):
                    pairs = [
                        (i, j)
                        for i in values
                        for j in values[::-1]
                        ]
                    for i, (a, b) in enumerate(pairs):
                        if i % 2:
                            pairs[i] = b, a
                        if i % 3:
                            pairs[i] = a, b, a
                        if i % 4:
                            pairs[i] = a, b, a, b
                    for pair in pairs:
                        yield pair
                ''',
            'complex_module/other_resource.txt': '''
                No test should be generated because of this resource.
                ''',
            'complex_module/submodule/__init__.py': '''
                class Something(object):
                    pass
                ''',
            }
        with self.create_module(data):
            class MyCodeComplexityTestCase(self.module.CodeComplexityTestCase):
                meta_module = 'complex_module'
                max_complexity = 3

            tests = [
                name
                for name in dir(MyCodeComplexityTestCase)
                if name.startswith('test_')
                ]
            self.assertEqual(tests, [
                'test_complexity_init_py',
                'test_complexity_submodule_init_py',
                ])

            test = MyCodeComplexityTestCase
            suite = unittest.TestLoader().loadTestsFromTestCase(test)

            stream_class = io.BytesIO if six.PY2 else io.StringIO
            with stream_class() as f:
                runner = unittest.TextTestRunner(stream=f, verbosity=2)
                results = runner.run(suite)

            self.assertEqual(results.testsRun, 2)
            self.assertEqual(len(results.errors), 0)
            self.assertEqual(len(results.failures), 1)
