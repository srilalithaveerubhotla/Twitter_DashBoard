# -*- coding: utf-8 -*-

''' Extends the custom loader so the test are run by the line
where they are defined and not by thier names.
'''

from unittest2.loader import TestLoader


def sortResultsByLineNumber(testCaseClass, fnName):
    ''' Given a function name of the testCaseClass, return the line
    number of that function
    '''
    return getattr(testCaseClass, fnName).im_func.func_code.co_firstlineno


class UtilsTestLoader(TestLoader):
    ''' Custom loader that will execute the test for a module using
    the line number where the method starts and not the method name.
    '''

    def getTestCaseNames(self, testCaseClass):
        """Return a sorted sequence of method names found within testCaseClass.

        The sequence will be returned by the line number
        """
        testFnNames = super(UtilsTestLoader, self).getTestCaseNames(testCaseClass)
        testFnNames.sort(key=lambda fnName: sortResultsByLineNumber(testCaseClass, fnName))
        return testFnNames

