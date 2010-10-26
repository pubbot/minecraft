
import os, zlib


class World(object):

    def __init__(self):
        self.dump_map_chunks = True
        self.dump_serial = 0

    def dump_map_chunk(self, x, y, z, sx, sy, sz, payload):
        if not os.path.exists("/tmp/chunks"):
            os.makedirs("/tmp/chunks")
        open("/tmp/chunks/%d" % self.dump_serial, "wb").write(payload)
        open("/tmp/chunks/index", "a").write("\t".join([str(x) for x in (self.dump_serial, x, y, z, sx, sy, sz)]) + "\n")
        self.dump_serial += 1

    def on_pre_chunk(self, x, z, mode):
        pass

    def on_map_chunk(self, x, y, z, sx, sy, sz, compressed_chunk_size, compressed_chunk):
        payload = zlib.decompress(compressed_chunk)

        if self.dump_map_chunks:
            self.dump_map_chunk(x, y, z, sx, sy, sz, payload)

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coord_array, type_array, metadata_array):
        pass

    def on_block_change(self, x, y, z, type, metadata):
        pass


