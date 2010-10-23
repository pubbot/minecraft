from struct import pack

class MinecraftWriter(object):

    def __init__(self, transport):
        self.transport = transport

    def write_packet_id(self, val):
        self.transport.write(pack(">B", val))

    def write_byte(self, val):
        self.transport.write(pack(">b", val))

    def write_short(self, val):
        self.transport.write(pack(">h", val))

    def write_int(self, val):
        self.transport.write(pack(">i", val))

    def write_long(self, val):
        self.transport.write(pack(">q", val))

    def write_float(self, val):
        self.transport.write(pack(">f", val))

    def write_double(self, val):
        self.transport.write(pack(">d", val))

    def write_string(self, val):
        self.write_short(len(val))
        self.transport.write(pack(">%ds" % len(val), val))

    def write_bool(self, val):
        if val:
            self.write_byte(1)
        else:
            self.write_byte(0)

