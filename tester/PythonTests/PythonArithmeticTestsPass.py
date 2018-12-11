
import time
import unittest

from .src import pythonsrc

class PythonArithmeticTestsPass(unittest.TestCase):

    def test_addition(self):
        time.sleep(4)
        self.assertEqual(int(pythonsrc.addition(1, 2)), 3)
        time.sleep(4)

    def test_division(self):
        time.sleep(8)
        self.assertEqual(int(pythonsrc.division(10, 2)), 5)
        time.sleep(8)
