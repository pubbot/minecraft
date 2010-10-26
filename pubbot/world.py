
import os, zlib

from pubbot.vector import Vector

class Chunk(object):

    def __init__(self, x, y, z, sx, sy, sz, payload):
        # Record start of chunk.
        self.pos = Vector(x, y, z)

        # Record size of this chunk
        self.sx = sx
        self.sy = sy
        self.sz = sz

        self.blocks = {}

        for x in range(sx+1):
            for z in range(sy+1):
                for y in range(sz+1):
                    index = y + (z*128) + (x*128*16)
                    block_type = payload[index]
                    self.blocks[(x, y, z)] = block_type

    def get_relative_block(self, vector):
        return self.blocks[(x, y, z)]

    def get_absolute_block(self, vector):
        rel = vector - self.pos
        return self.get_relative_block(rel)

    def point_in_chunk(self, vector):
        if vector.x < self.pos.x or self.pos.x + self.sx  <= vector.x:
             return False
        if vector.y < self.pos.y or self.pos.z + self.sy <= vector.y:
            return False
        if vector.z < self.pos.z or self.pos.z + self.sz <= vector.z:
            return False

        return True


class World(object):

    def __init__(self):
        self.dump_map_chunks = True
        self.dump_serial = 0

        self.chunks = []

    def dump_map_chunk(self, x, y, z, sx, sy, sz, payload):
        if not os.path.exists("/tmp/chunks"):
            os.makedirs("/tmp/chunks")
        open("/tmp/chunks/%d" % self.dump_serial, "wb").write(payload)
        open("/tmp/chunks/index", "a").write("\t".join([str(x) for x in (self.dump_serial, x, y, z, sx, sy, sz)]) + "\n")
        self.dump_serial += 1

    def get_chunk(self, pos):
        for chunk in self.chunls:
            if chunk.point_in_chunk(pos):
                return chunk
        raise KeyError("Cannot find position %s in world!" % pos)

    def on_pre_chunk(self, x, z, mode):
        pass

    def on_map_chunk(self, x, y, z, sx, sy, sz, compressed_chunk_size, compressed_chunk):
        payload = zlib.decompress(compressed_chunk)

        if self.dump_map_chunks:
            self.dump_map_chunk(x, y, z, sx, sy, sz, payload)

        self.chunks.append(Chunk(x, y, z, sx, sy, sz, payload))

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coord_array, type_array, metadata_array):
        pass

    def on_block_change(self, x, y, z, type, metadata):
        pass


