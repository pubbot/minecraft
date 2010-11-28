import unittest

from pubbot.vector import Vector
from pubbot.traversal import walk

class TestTraversal(unittest.TestCase):

    def test_foo(self):
        start = Vector(0, 0, 0)
        finish = Vector(4, 6, 0)

        dir = (finish - start).normalize()

        stepper = walk(start, dir)

        self.failUnlessEqual(stepper.next(), Vector(0,0,0))
        self.failUnlessEqual(stepper.next(), Vector(0,1,0))
        self.failUnlessEqual(stepper.next(), Vector(1,1,0))
        self.failUnlessEqual(stepper.next(), Vector(1,2,0))
        self.failUnlessEqual(stepper.next(), Vector(2,2,0))
        self.failUnlessEqual(stepper.next(), Vector(2,3,0))

