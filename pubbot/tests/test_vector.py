import unittest

from pubbot.vector import Vector

class TestVector(unittest.TestCase):

    def test_hashes(self):
        a = Vector(1,1,1)
        b = a.copy()
        z = set()
        z.add(a)
        z.add(b)
        self.failUnlessEqual(len(z), 1)

    def test_subtract(self):
        self.failUnlessEqual(Vector(2,2,2) - Vector(1,1,1), Vector(1,1,1))

