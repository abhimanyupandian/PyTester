import os
import re
import time
import unittest

from tester import BashScript
scriptPath = os.path.dirname(os.path.realpath(__file__)) + "/src/Arithmetic.sh"
script = BashScript(scriptPath)

toInt = lambda x: [int(d) for d in re.findall(r'-?\d+', x)][0]

class BashArithmeticTestsFail(unittest.TestCase):

    def test_subtraction(self):
        time.sleep(4)
        self.assertEqual(toInt(script.subtraction(10, 2)), 32)
        time.sleep(4)

    def test_multiplication(self):
        time.sleep(8)
        self.assertEqual(toInt(script.multiplication(1, 2)), 2)
        time.sleep(8)

