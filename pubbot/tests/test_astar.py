import unittest

from pubbot.astar import *


class TestAStar(unittest.TestCase):

    def test_heap(self):
        def sortfn(x):
            return x
        h = Heap(sortfn=sortfn)

        h.push(10)
        h.push(1)
        h.push(3)
        h.push(2)

        self.failUnless(not h.empty())

        self.failUnlessEqual(h.pop(), 1)
        self.failUnlessEqual(h.pop(), 2)
        self.failUnlessEqual(h.pop(), 3)
        self.failUnlessEqual(h.pop(), 10)

        self.failUnless(h.empty())

    def test_straight(self):
        pass

