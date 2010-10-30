
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from mock import Mock

from pubbot.vector import Vector
from pubbot.world import Block

class TestBlock(TestCase):

    def test_ftl(self):
        b = Block(Vector(0,0,0), 4, 0)
        self.failUnlessEqual(b.ftl, 7)

    def test_name(self):
        b = Block(Vector(0,0,0), 4, 0)
        self.failUnlessEqual(b.name, "cobblestone")

