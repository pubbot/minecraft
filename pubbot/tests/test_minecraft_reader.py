# MinecraftReader is a layer that sits on top of a dataReceived callback and provides read_string, read_int etc
# functionality

from twisted.trial.unittest import TestCase
from twisted.internet import defer

from pubbot.protocol import MinecraftReader


class TestMinecraftReader(TestCase):

    @defer.inlineCallbacks
    def test_read_raw(self):
        r = MinecraftReader()
        d = r.read_raw(5)
        r.dataReceived("12345")
        result = yield d
        self.failUnlessEqual(result, "12345")


