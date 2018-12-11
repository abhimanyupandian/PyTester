import os
import sys
import unittest

import tester
from tester.Tester import _tester
sys.path.insert(0, os.path.dirname(tester.__file__))

class DatabaseTests(unittest.TestCase):

    def setUp(self):
        self.tester = _tester("BashTests")

    def test_getResultsFromDatabase_CorrectTestName(self):
        self.tester.loadTests("BashArithmeticTestsFail")
        self.tester.runTests()
        self.assertNotEqual(self.tester.getResultsFromDatabase("test_multiplication"), None)

    def test_getResultsFromDatabase_IncorrectTestName(self):
        self.tester.loadTests("BashArithmeticTestsFail")
        self.assertEqual(self.tester.getResultsFromDatabase("ABCD"), None)

