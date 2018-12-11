import os
import time
import unittest

from tester import BashScript
scriptPath = os.path.dirname(os.path.realpath(__file__)) + "/src/Arithmetic.sh"
script = BashScript(scriptPath)

toInt = lambda x: int(filter(str.isdigit, x) or 0)

class BashArithmeticTestsPass(unittest.TestCase):

    def test_addition(self):
        time.sleep(4)
        self.assertEqual(toInt(script.addition(1, 2)), 3)
        time.sleep(4)

    def test_division(self):
        time.sleep(8)
        self.assertEqual(toInt(script.division(10, 2)), 5)
        time.sleep(8)

