#!/usr/local/bin/python-32
# vim: set tabstop=4 shiftwidth=4 autoindent smartindent:
import sys, os
import glob
import unittest

## set the path to include parent directory
sys.path.insert(0, os.path.join( os.path.dirname(__file__), '..' ))

def create_test_suite():
        test_file_strings = glob.glob('test_*.py')
        #module_strings = ['test.'+str[5:len(str)-3] for str in test_file_strings]
        module_strings = [str[:len(str)-3] for str in test_file_strings]
        suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in module_strings]
        testSuite = unittest.TestSuite(suites)
        return testSuite

## run all tests
testSuite = create_test_suite()
text_runner = unittest.TextTestRunner().run(testSuite)
