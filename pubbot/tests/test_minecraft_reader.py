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
        self.failUnlessEqual((yield d), "12345")

    @defer.inlineCallbacks
    def test_read_byte(self):
        r = MinecraftReader()
        d = r.read_byte()
        r.dataReceived("\x00")
        self.failUnlessEqual((yield d), 0)

    @defer.inlineCallbacks
    def test_read_short(self):
        r = MinecraftReader()
        d = r.read_short()
        r.dataReceived("\x00\x00")
        self.failUnlessEqual((yield d), 0)

    @defer.inlineCallbacks
    def test_read_int(self):
        r = MinecraftReader()
        d = r.read_int()
        r.dataReceived("\x00\x00\x00\x00")
        self.failUnlessEqual((yield d), 0)

    @defer.inlineCallbacks
    def test_read_long(self):
        r = MinecraftReader()
        d = r.read_long()
        r.dataReceived("\x00\x00\x00\x00\x00\x00\x00\x00")
        self.failUnlessEqual((yield d), 0)

    @defer.inlineCallbacks
    def test_read_float(self):
        r = MinecraftReader()
        d = r.read_float()
        r.dataReceived("\x00\x00\x00\x00")
        self.failUnlessEqual((yield d), 0)

    @defer.inlineCallbacks
    def test_read_double(self):
        r = MinecraftReader()
        d = r.read_double()
        r.dataReceived("\x00\x00\x00\x00\x00\x00\x00\x00")
        self.failUnlessEqual((yield d), 0)

    @defer.inlineCallbacks
    def test_read_string(self):
        r = MinecraftReader()
        d = r.read_string()
        r.dataReceived("\x00\x09minecraft1234567890")
        self.failUnlessEqual((yield d), "minecraft")


    @defer.inlineCallbacks
    def test_read_bool(self):
        r = MinecraftReader()
        d = r.read_bool()
        r.dataReceived("\x00")
        self.failUnlessEqual((yield d), False)
        d = r.read_bool()
        r.dataReceived("\x01")
        self.failUnlessEqual((yield d), True)


