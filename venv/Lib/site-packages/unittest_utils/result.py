# -*- coding: utf-8 -*-

''' Outputs with color the head of each test which failed.
'''

from termcolor import colored
from unittest2.runner import TextTestResult


class UtilsResult(TextTestResult):
    ''' A custom result which will print the result using colored
    output
    '''

    def color_favour(self, flavour, test):
        msg = '%s: %s' % (flavour, self.getDescription(test))
        return colored(msg, 'red', attrs=['bold'])

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(self.color_favour(flavour, test))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)
