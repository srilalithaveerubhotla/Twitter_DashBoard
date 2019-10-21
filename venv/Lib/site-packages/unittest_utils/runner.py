# -*- coding: utf-8 -*-

'''
'''

from unittest2.runner import TextTestRunner
from unittest_utils.result import UtilsResult


class UtilsTextTestRunner(TextTestRunner):
    ''' Uses the result that prints the failed an error with color.
    '''

    resultclass = UtilsResult
