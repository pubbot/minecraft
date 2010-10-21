from twisted.trial.unittest import TestCase

from mock import Mock

from pubbot.actions import Action
from pubbot.bot import Bot

class TestActionMachinery(TestCase):

    def test_queue_action(self):
        bot = Bot(Mock())

        # queue three mocks
        a, b, c = Mock(), Mock(), Mock()
        bot.queue_immediate_actions(c)
        bot.queue_immediate_actions(b)
        bot.queue_immediate_actions(a)

        self.failUnlessEqual(bot.actions, [a, b, c])

    def test_do_action(self):
        bot = Bot(Mock())
        a, b = Mock(), Mock()
        a.do.return_value = b.do.return_value = None
        bot.actions = [a,b]
        bot.execute_actions()
        bot.execute_actions()
        self.failUnlessEqual(len(bot.actions), 0)

    def test_do_action_empty_list(self):
        bot = Bot(Mock())
        bot.execute_actions()
