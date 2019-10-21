# -*- coding: utf-8 -*-

''' Extends the ``unittest2.main.TestProgram`` to add the custom options.
'''


from unittest2.main import TestProgram, USAGE_AS_MAIN
from unittest_utils.loader import UtilsTestLoader
from unittest_utils.runner import UtilsTextTestRunner


class UtilsTestProgram(TestProgram):

    def __init__(self, *args, **kwargs):
        ''' Overrides de default TestProgram to use a custom testLoader
        which will load the tests using the line where those are defined.
        '''
        super(UtilsTestProgram, self).__init__(testLoader=UtilsTestLoader(),
                                               testRunner=UtilsTextTestRunner,
                                                *args,
                                                **kwargs)

    def _do_discovery(self, *args, **kwargs):
        return super(UtilsTestProgram, self)._do_discovery(Loader=UtilsTestLoader,
                                                           *args,
                                                           **kwargs)


def _main():
    UtilsTestProgram.USAGE = USAGE_AS_MAIN
    UtilsTestProgram(module=None)
