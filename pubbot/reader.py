from struct import unpack
from twisted.internet import defer

class MinecraftReader(object):

    def __init__(self):
        self.data = ""
        self.length_wanted = 0
        self.callback = None

    def dataReceived(self, data):
        self.data += data
        if self.callback and len(self.data) >= self.length_wanted:
            callback, self.callback = self.callback, None
            callback.callback(None)

    @defer.inlineCallbacks
    def read_raw(self, num_bytes):
        """
        I read x bytes from the server, if there isnt enough data then i yield a Deferred
        effectively pausing the current code until the rest of the data is available
        """
        if len(self.data) < num_bytes:
             # Not enough data: Pause this function until there is
             self.length_wanted = num_bytes
             self.callback = defer.Deferred()
             yield self.callback

        # Pop the data off the front of data and return it
        data = self.data[0:num_bytes]
        self.data = self.data[num_bytes:]
        defer.returnValue(data)

    @defer.inlineCallbacks
    def read_packet_id(self):
        val = unpack(">B", (yield self.read_raw(1)))[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_byte(self):
        val = unpack(">b", (yield self.read_raw(1)))[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_short(self):
        val = unpack(">h", (yield self.read_raw(2)))[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_int(self):
        val = unpack(">i", (yield self.read_raw(4)))[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_long(self):
        val = unpack(">q", (yield self.read_raw(8)))[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_float(self):
        val = unpack(">f", (yield self.read_raw(4)))[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_double(self):
        val = unpack(">d", (yield self.read_raw(8)))[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_string(self):
        length = yield self.read_short()
        data = yield self.read_raw(length)
        val = unpack(">%ds" % length, data)[0]
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_bool(self):
        val = yield self.read_byte()
        if val:
            defer.returnValue(True)
        else:
            defer.returnValue(False)


