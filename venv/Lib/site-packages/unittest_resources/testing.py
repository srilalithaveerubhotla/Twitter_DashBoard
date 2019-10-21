# -*- coding: utf-8 -*-
"""
Tool-specific :class:`unittest.TestCase` bases for :mod:`unittest_resources`.

This module provides base tests for :mod:`unittest_resources` module
integrating common tools.
"""

import sys
import io
import re
import contextlib
import unittest

import six

import unittest_resources

try:  # python 3.5+
    import typing
except ImportError:
    typing = None  # type: ignore

try:  # python 3.5+
    import mypy.options
    import mypy.build
    import mypy.modulefinder
except ImportError:
    mypy = None  # type: ignore

try:
    import pycodestyle
except ImportError:
    pycodestyle = None

try:
    import pydocstyle
except ImportError:
    pydocstyle = None  # type: ignore

try:
    import radon.metrics
    import radon.visitors
    import radon.complexity
except ImportError:
    radon = None  # type: ignore


__all__ = [
    'TypingTestCase',
    'CodeStyleTestCase',
    'DocStyleTestCase',
    'MaintainabilityIndexTestCase',
    'CodeComplexityTestCase',
    ]


class TypingTestCase(unittest_resources.ResourceTestCase):
    """
    TestCase checking :mod:`mypy` type annotations (:mod:`typing`).

    Override :attr:`meta_module` to point to your own module or
    :attr:`meta_resources` to specify your resources manually.
    """

    meta_prefix = 'typing'
    meta_resource_pattern = re.compile(r'\.py$')

    @property
    def options(self):
        # type: () -> mypy.options.Options
        """
        Generate options object for :func:`mypy.build.build`.

        :return: mypy build options object
        :rtype: mypy.options.Options
        """
        options = mypy.options.Options()
        options.build_type = mypy.options.BuildType.MODULE
        options.disallow_untyped_defs = True
        options.disallow_untyped_calls = True
        options.disallow_incomplete_defs = True
        options.strict_equality = True
        return options

    @unittest.skipIf(typing is None, 'typing is not available')
    @unittest.skipIf(mypy is None, 'mypy is not available')
    def meta_test(self, module, resource):
        # type: (str, str) -> None
        """
        Validate :mod:`mypy` type annotations of given resource.

        :param module: resource module name
        :type module: str
        :param resource: resource name
        :type resource: str
        """
        name = (
            module
            if resource == '__init__.py' else
            '{}.{}'.format(module, resource[:-3])
            if resource.endswith('.py') else
            resource
            )
        data = self.read_text(module, resource)
        source = mypy.modulefinder.BuildSource(None, name, data)
        with io.StringIO() as f:
            mypy.build.build([source], self.options, stdout=f, stderr=f)
            report = f.getvalue().strip()
            self.assertFalse(bool(report), report)


class CodeStyleTestCase(unittest_resources.ResourceTestCase):
    """
    TestCase checking :mod:`pycodestyle`.

    Override :attr:`meta_module` to point to your own module or
    :attr:`meta_resources` to specify your resources manually.
    """

    meta_prefix = 'codestyle'
    meta_resource_pattern = re.compile(r'\.py$')

    error_format = '  [%(row)s:%(col)s] %(code)s: %(text)s'

    @property
    def options(self):
        # type: () -> typing.Dict[str, typing.Any]
        """
        Generate options dictionary for :class:`pycodestyle.StyleGuide`.

        :return: pycodestyle options dict
        :rtype: dict
        """
        return {
            'format': self.error_format,
            'quiet': False,
            }

    @contextlib.contextmanager
    def capture_stdout(self):
        # type: () -> typing.Generator[io.StringIO, None, None]
        """
        Capture everything written on stdout inside context.

        :return: stdout-capturing context-manager
        :rtype: contextlib.AbstractContextManager
        """
        with io.StringIO() as buffer:
            sys.stdout, sys_stdout = buffer, sys.stdout
            yield buffer
            sys.stdout = sys_stdout

    @unittest.skipIf(pycodestyle is None, 'pycodestyle is not available')
    def meta_test(self, module, resource):
        # type: (str, str) -> None
        """
        Check :mod:`pycodestyle` of given resource.

        :param module: resource module name
        :type module: str
        :param resource: resource name
        :type resource: str
        """
        with self.capture_stdout() as buffer:
            style = pycodestyle.StyleGuide(**self.options)
            with self.path(module, resource) as path:
                report = style.check_files([str(path)])
                errors = buffer.getvalue()
        self.assertEqual(report.total_errors, 0, (
            'Code style error{s} (or warning{s}) '
            'on module {module}, file {resource!r}.'
            '\n{errors}'
            ).format(
                s='s' if report.total_errors > 1 else '',
                module=module,
                resource=resource,
                errors=errors,
                )
            )


class DocStyleTestCase(unittest_resources.ResourceTestCase):
    """
    TestCase checking :mod:`pydocstyle`.

    Override :attr:`meta_module` to point to your own module or
    :attr:`meta_resources` to specify your resources manually.
    """

    meta_prefix = 'docstyle'
    meta_resource_pattern = re.compile(r'\.py$')

    error_format = '  [{error.line}] {error.message}'

    @unittest.skipIf(pydocstyle is None, 'pydocstyle is not available')
    def meta_test(self, module, resource):
        # type: (str, str) -> None
        """
        Check :mod:`pydocstyle` of given resource.

        :param module: resource module name
        :type module: str
        :param resource: resource name
        :type resource: str
        """
        with self.path(module, resource) as path:
            errors = list(pydocstyle.check([str(path)]))

        self.assertEqual(len(errors), 0, (
            'Doc style error{s} on module {module}, file {resource!r}.'
            '\n{errors}'
            ).format(
                s='s' if len(errors) > 1 else '',
                module=module,
                resource=resource,
                errors='\n'.join(
                    self.error_format.format(error=error)
                    for error in errors
                    ),
                )
            )


class MaintainabilityIndexTestCase(unittest_resources.ResourceTestCase):
    """
    TestCase checking :mod:`radon` maintainability index.

    Override :attr:`meta_module` to point to your own module or
    :attr:`meta_resources` to specify your resources manually.

    Override :attr:`min_maintainability` to set your custom minimum
    maintainability index score.
    """

    meta_prefix = 'maintainability'
    meta_resource_pattern = re.compile(r'\.py$')

    min_maintainability = 20

    @unittest.skipIf(radon is None, 'radon is not available')
    def meta_test(self, module, resource):
        # type: (str, str) -> None
        """
        Check :mod:`radon` maintainability index of given resource.

        :param module: resource module name
        :type module: str
        :param resource: resource name
        :type resource: str
        """
        data = self.read_text(module, resource, encoding='utf-8')
        if six.PY2:
            data = data.encode('utf-8')

        score = radon.metrics.mi_visit(data, True)
        self.assertGreaterEqual(score, self.min_maintainability, (
            'Maintainability index {score} found (minimum is {min}) '
            'on module {module}, file {resource!r}.').format(
                score=score,
                min=self.min_maintainability,
                module=module,
                resource=resource,
                )
            )


class CodeComplexityTestCase(unittest_resources.ResourceTestCase):
    """
    TestCase checking :mod:`radon` code complexity.

    Override :attr:`meta_module` to point to your own module or
    :attr:`meta_resources` to specify your resources manually.

    Override both :attr:`max_class_complexity` and
    :attr:`max_function_complexity` to set your maximum complexity
    score values.
    """

    meta_prefix = 'complexity'
    meta_resource_pattern = re.compile(r'\.py$')

    error_format = (
        '  [{error.lineno}-{error.endline}] {type} {error.name} '
        'is too complex ({error.complexity})'
        )

    max_class_complexity = 8
    max_function_complexity = 6

    @classmethod
    def collect_errors(cls, node):
        # type: (typing.Any) -> typing.Generator[str, None, None]
        """
        Yield errors from :mod:`radon` complexity visitor result node.

        :param node: radon complexity visitor result node
        :type node: typing.Union[radon.visitors.Class, radon.visitors.Function]
        :return: error message generator
        :rtype: typing.Generator[str, None, None]
        """
        if isinstance(node, radon.visitors.Class):
            max_complexity = cls.max_class_complexity
            children = node[4]
        elif isinstance(node, radon.visitors.Function):
            max_complexity = cls.max_function_complexity
            children = node[6]
        else:
            return

        for child in children:
            for error in cls.collect_errors(child):
                yield error

        if node.complexity > max_complexity:
            yield cls.error_format.format(
                error=node,
                type=type(node).__name__.lower(),
                max_complexity=max_complexity,
                )

    @unittest.skipIf(radon is None, 'radon is not available')
    def meta_test(self, module, resource):
        # type: (str, str) -> None
        """
        Check :mod:`radon` code complexity of given resource.

        :param module: resource module name
        :type module: str
        :param resource: resource name
        :type resource: str
        """
        data = self.read_text(module, resource, encoding='utf-8')
        if six.PY2:
            data = data.encode('utf-8')

        errors = [
            error
            for node in radon.complexity.cc_visit(data)
            for error in self.collect_errors(node)
            ]
        if errors:
            self.assertEqual(len(errors), 0, (
                'Complexity issue{s} on module {module}, file {resource!r}.'
                '\n{errors}'
                ).format(
                    s='s' if len(errors) > 1 else '',
                    module=module,
                    resource=resource,
                    errors='\n'.join(errors),
                    )
                )
