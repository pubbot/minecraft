
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from mock import Mock

from pubbot.vector import Vector
from pubbot.block import Block

class TestBlock(TestCase):

    def test_ftl(self):
        b = Block(Vector(0,0,0), 4, 0)
        self.failUnlessEqual(b.digs, 9)

    def test_name(self):
        b = Block(Vector(0,0,0), 4, 0)
        self.failUnlessEqual(b.name, "cobblestone")

    def test_face_neg_y(self):
        b = Block(Vector(0, 0, 0), 4, 0)
        self.failUnlessEqual(b.get_faces(Vector(0.5,-2,0.5))[0][0], 0)

    def test_face_pos_y(self):
        b = Block(Vector(0, 0, 0), 4, 0)
        self.failUnlessEqual(b.get_faces(Vector(0.5,2,0.5))[0][0], 1)

    def test_face_neg_z(self):
        b = Block(Vector(0, 0, 0), 4, 0)
        self.failUnlessEqual(b.get_faces(Vector(0.5,0,-2))[0][0], 2)

    def test_face_pos_z(self):
        b = Block(Vector(0, 0, 0), 4, 0)
        self.failUnlessEqual(b.get_faces(Vector(0.5,0,2))[0][0], 3)

    def test_face_neg_x(self):
        b = Block(Vector(0,0,0), 4, 0)
        self.failUnlessEqual(b.get_faces(Vector(-2,0,.5))[0][0], 4)

    def test_face_pos_x(self):
        b = Block(Vector(0, 0, 0), 4, 0)
        self.failUnlessEqual(b.get_faces(Vector(2,0,0.5))[0][0], 5)


