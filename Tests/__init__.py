
import time
import unittest

class FunctionalTests(unittest.TestCase):
    def test_upper(self):
        time.sleep(2)
        self.assertEqual('foo'.upper(), 'FOsO')
        time.sleep(2)
    def test_uppers(self):
        time.sleep(4)
        self.assertEqual('foo'.upper(), 'FOO')
        time.sleep(4)
    def test_upperss(self):
        time.sleep(6)
        self.assertEqual('foo'.upper(), 'FOsO')
        time.sleep(6)
    def test_uppersss(self):
        time.sleep(8)
        self.assertEqual('foo'.upper(), 'FOO')
        time.sleep(8)

class SanityTests(unittest.TestCase):
    def test_upperss(self):
        time.sleep(60)
        self.assertEqual('foo'.upper(), 'FOsO')
        time.sleep(6)
    def test_uppersss(self):
        time.sleep(8)
        self.assertEqual('foo'.upper(), 'FOO')
        time.sleep(8)