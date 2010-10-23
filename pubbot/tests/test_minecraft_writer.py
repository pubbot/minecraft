# MinecraftWriter(transport) is a layer that sits on top of a dataReceived callback and provides read_string, read_int etc
# functionality

from twisted.trial.unittest import TestCase
from twisted.internet import defer

from pubbot.writer import MinecraftWriter


class MockTransport(object):

    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data


class TestMinecraftWriter(TestCase):

    def setUp(self):
        self.transport = MockTransport()
        self.w = MinecraftWriter(self.transport)

    def test_write_byte(self):
        self.w.write_byte(0)
        self.failUnlessEqual(self.transport.data, "\x00")

    def test_write_short(self):
        self.w.write_short(0)
        self.failUnlessEqual(self.transport.data, "\x00\x00")

    def test_write_int(self):
        self.w.write_int(0)
        self.failUnlessEqual(self.transport.data, "\x00" * 4)

    def test_write_long(self):
        self.w.write_long(0)
        self.failUnlessEqual(self.transport.data, "\x00" * 8)

    def test_write_float(self):
        self.w.write_float(0.0)
        self.failUnlessEqual(self.transport.data, "\x00" * 4)

    def test_write_double(self):
        self.w.write_double(0.0)
        self.failUnlessEqual(self.transport.data, "\x00" * 8)

    def test_write_string(self):
        self.w.write_string("minecraft")
        self.failUnlessEqual(self.transport.data, "\x00\x09minecraft")

    def test_write_bool_false(self):
        self.w.write_bool(False)
        self.failUnlessEqual(self.transport.data, "\x00")

    def test_write_bool_true(self):
        self.w.write_bool(True)
        self.failUnlessEqual(self.transport.data, "\x01")


