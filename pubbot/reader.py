from struct import unpack
from twisted.internet import defer

class BaseMinecraftReader(object):

    def read_raw(self, size):
        raise NotImplementedError(self.read_raw)

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
        defer.returnValue(val.decode("UTF-8"))

    @defer.inlineCallbacks
    def read_bool(self):
        val = yield self.read_byte()
        if val:
            defer.returnValue(True)
        else:
            defer.returnValue(False)


class MinecraftReader(object):

    def __init__(self):
        self.length_wanted = 0
        self.data = ""
        self.callback = ""

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


class NBTReader(object):

    self.tagmap = {
        0x01: self.read_byte,
        0x02: self.read_short,
        0x03: self.read_int,
        0x04: self.read_long,
        0x05: self.read_float,
        0x06: self.read_double,
        0x07: self.read_byte_array,
        0x08: self.read_string,
        0x09: self.read_list,
        0x0A: self.read_dict,
        }

    def __init__(self, fp):
        self.fp = gzip.GzipFile(fileobj=fp, mode='rb')

    def read_raw(self, num_bytes):
        return defer.succeed(fp.read(num_bytes))

    @defer.inlineCallbacks
    def read_byte_array(self):
        length = yield self.read_int()
        data = []
        for i in range(length):
            data.append(yield self.read_byte())
        defer.returnValue(data)

    @defer.inlineCallbacks
    def read_list(self):
        tag = yield self.read_byte()
        length = yield self.read_int()

        data = []
        for i in range(length):
            data.append(yield self.tagmap[tag]())

        defer.returnValue(data)

    @defer.inlineCallbacks
    def read_dict(self):
        data = {}

        while True:
            tag = yield self.read_byte()
            if tag == 0x00:
                break
            name = yield self.read_string()
            data[name] = yield self.tagmap[tag]()

        defer.returnValue(data)

