
import time
import unittest

from .src import pythonsrc

class PythonArithmeticTestsFail(unittest.TestCase):

    def test_subtraction(self):
        time.sleep(4)
        self.assertEqual(int(pythonsrc.subtraction(10, 2)), 6)
        time.sleep(4)

    def test_multiplication(self):
        time.sleep(8)
        self.assertEqual(int(pythonsrc.multiplication(1, 2)), 2)
        time.sleep(8)
