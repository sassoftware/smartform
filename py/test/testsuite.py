#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (c) 2006-2009 rPath, Inc.  All Rights Reserved.
#

import os
import sys

from testrunner import suite, testhandler
class Suite(suite.TestSuite):
    # Boilerplate. We need these values saved in the caller module
    testsuite_module = sys.modules[__name__]
    suiteClass = testhandler.ConaryTestSuite

    execPathVarNames = [
        'SMARTFORM_PATH',
    ]

    def getCoverageDirs(self, handler, environ):
        return [ self.pathManager.getCoveragePath('SMARTFORM_PATH') ]

    def getCoverageExclusions(self, handler, environ):
        return [r'generatedssuper\.py',
                r'gends_user_methods\.py',
                r'xml_.*/.*\.py']

_s = Suite()
setup = _s.setup
main = _s.main

if __name__ == '__main__':
    _s.run()
