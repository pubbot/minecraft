
from twisted.trial.unittest import TestCase
from twisted.internet import defer

from mock import Mock

from pubbot import actions

class TestIdle(TestCase):

    def test_idle_for_ten_iterations(self):
        a = actions.Idle(Mock(), 10)
        for i in range(9):
            self.failUnlessEqual(a.do(), a)
        self.failUnlessEqual(a.do(), None)


class TestSay(TestCase):

    def test_say(self):
        a = actions.Say(Mock(), "hello everybody")
        result = a.do()
        self.failUnlessEqual(result, None)
        self.failUnlessEqual(a.bot.protocol.send_chat_message.call_args[0][0], "hello everybody")
