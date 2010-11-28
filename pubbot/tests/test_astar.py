import unittest

from pubbot.astar import *
from pubbot.vector import Vector

class MockWorld(object):

    def __init__(self, *allowed_pos):
        self.allowed_pos = allowed_pos

    def available(self, pos):
        return list((x,) for x in self.allowed_pos if (pos-x).manhattan_length() <= 1)

    def allowed(self, pos):
        return pos in self.allowed_pos


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

    def test_cost(self):
        p = Path(Vector(0, 0, 0), [Vector(0, 0, 5)], [])
        self.failUnlessEqual(p.cost(), 505)

    def test_straight(self):
        world = MockWorld(
            Vector(0,0,0), Vector(0,0,1), Vector(0,0,2),
            Vector(0,0,3), Vector(0,0,4), Vector(0,0,5))

        route = path(world, Vector(0,0,0), [Vector(0,0,5)])

        self.failUnlessEqual(len(route), 5)
        self.failUnlessEqual(route[0], Vector(0, 0, 1))
        self.failUnlessEqual(route[1], Vector(0, 0, 2))
        self.failUnlessEqual(route[2], Vector(0, 0, 3))
        self.failUnlessEqual(route[3], Vector(0, 0, 4))
        self.failUnlessEqual(route[4], Vector(0, 0, 5))

    def test_hill(self):
        world = MockWorld(
            Vector(0,0,0), Vector(0,0,1), Vector(0,1,1),
            Vector(0,1,2), Vector(0,1,3), Vector(0,1,4),
            Vector(0,0,3), Vector(0,0,4), Vector(0,0,5))

        route = path(world, Vector(0,0,0), [Vector(0,0,5)])

        self.failUnlessEqual(len(route), 7)
        self.failUnlessEqual(route[0], Vector(0, 0, 1))
        self.failUnlessEqual(route[1], Vector(0, 1, 1))
        self.failUnlessEqual(route[2], Vector(0, 1, 2))
        self.failUnlessEqual(route[3], Vector(0, 1, 3))
        self.failUnlessEqual(route[4], Vector(0, 1, 4))
        self.failUnlessEqual(route[5], Vector(0, 0, 4))
        self.failUnlessEqual(route[6], Vector(0, 0, 5))

