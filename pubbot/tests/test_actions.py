
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from pubbot import actions

class Bot:
    pass

class TestIdle(TestCase):

    def test_idle_for_ten_iterations(self):
        a = actions.Idle(Bot(), 10)
        for i in range(9):
            self.failUnlessEqual(a.do(), a)
        self.failUnlessEqual(a.do(), None)


