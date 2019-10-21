# -*- coding: utf-8 -*-

''' Extends the ``unittest2.TestCase`` to so get better string difference.

It will show the string difference on RED color.
'''

from unittest2 import TestCase
from termcolor import colored


class UtilsTestCase(TestCase):
    ''' Adds a custom method to get a better output when checking
    for long strings
    '''

    # the number of chars of the strings that should be colorized, when
    # there is a difference
    COLORED_CHARS = 5

    # the total number of chars that should be shown from each string
    # to get the difference (from the left and from the right)
    TOTAL_CHARS = 25

    # the color in which the difference will be shown.
    DIFFERENCE_COLOR = 'red'

    def assertEqual(self, first, second, msg=None):
        ''' Extends the assertEqualto get a better output on the string
        difference when both values are strings (or unicode)
        '''

        if isinstance(first, basestring) and isinstance(second, basestring):
            # check if the string are multine. In that case use the
            # default solution
            if not '\n' in first and not '\n' in second:
                if first != second:
                    # if the aren't multi line, then use the custom string
                    # difference report
                    standardMsg = self._search_string_difference(first, second)
                    msg = self._formatMessage(msg, standardMsg)
                    raise self.failureException(msg)
            else:
                return super(UtilsTestCase, self).assertEqual(first, second,
                                                              msg)

        return super(UtilsTestCase, self).assertEqual(first, second, msg)

    # override the assertEquals
    assertEquals = assertEqual

    def _search_string_difference(self, first, second):
        ''' Given two strings it searches for the string difference on
        a readable manner.
        '''
        index = 0
        min_length = min(len(first), len(second))
        res = ""
        while index < min_length:
            if first[index] == second[index]:
                index += 1
                continue

            res = "'%s' != '%s'" % (
                            self._show_string_difference(first, index),
                            self._show_string_difference(second, index)
                            )
            break

        if not res:
            # entonces uno es mas largo que otro
            shortest = first
            longest = second
            if len(first) > len(second):
                longest = first
                shortest = second

            res = "'%s' != '%s'" % (
                            self._show_string_difference(shortest, index),
                            self._show_string_difference(longest, index)
                            )

        return res

    def _show_string_difference(self, value, index):
        res = value[index-self.TOTAL_CHARS: index-self.COLORED_CHARS]
        res += colored(value[index-self.COLORED_CHARS:index+self.COLORED_CHARS],
                        self.DIFFERENCE_COLOR,
                        attrs=['bold'])
        res += value[index+self.COLORED_CHARS:index+self.TOTAL_CHARS]
        return res
