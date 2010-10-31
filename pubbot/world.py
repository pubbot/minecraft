# Copyright 2010 John Carr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Provides a world object which provides access to block data, which is segmented
# by minecraft in to chunks

import os, zlib, math

from twisted.internet import threads

from pubbot.vector import Vector
from pubbot.blocks import blocks


class Block(object):

    __slots__ = ("pos", "kind", "metadata")

    def __init__(self, pos, kind, metadata):
        self.pos = pos
        self.kind = kind
        self.metadata = metadata

    @property
    def preferred_tool(self):
        return blocks[self.kind]["preferred_tool"]

    @property
    def ttl(self):
        return blocks[self.kind]["times"][self.preferred_tool]

    @property
    def ftl(self):
        return int(math.ceil(self.ttl * 10))

    @property
    def name(self):
        return blocks[self.kind]["name"]

    def get_face(self, observer):
        """
        Given the vector of an observer, work out which of my sides they can best see

        Returns a list of faces they can see, with the nearest first

        0    -Y
        1    +Y
        2    -Z
        3    +Z
        4    -X
        5    +X
        """
        dir = self.pos - observer

        # Discard the 3 faces we definitely can't see
        xf = 4 if dir.x < 0 else 5
        yf = 0 if dir.y < 0 else 1
        zf = 2 if dir.z < 0 else 3

        # Garys law: Largest magnitude of change in a vector component leads us to the nearest face
        # Drop the sign first of all axis
        if dir.x < 0:
            dir.x *= -1
        if dir.y < 0:
            dir.y *= -1
        if dir.z < 0:
            dir.z *= -1

        # Sort biggest first - as its such a small loop ive manually unrolled the loop
        # Yet another thing about this code that will haunt me for years
        if dir.z > dir.y:
            if dir.y > dir.z:
                return (zf, yf, xf)
            else:
                return (zf, xf, yf)
        elif dir.y > dir.x:
            if dir.x > dir.z:
                return (yf, xf, zf)
            else:
                return (yf, zf, xf)
        else:
            if dir.z > dir.y:
                return (xf, zf, yf)
            else:
                return (xf, yf, zf)


class Chunk(object):

    __slots__ = ("pos", "sx", "sy", "sz", "blocks")

    def __init__(self, x, y, z, sx, sy, sz):
        # Record start of chunk.
        self.pos = Vector(x, y, z)

        # Record size of this chunk
        self.sx = sx
        self.sy = sy
        self.sz = sz

        self.blocks = {}

    def dump_chunk(self, payload):
        if not os.path.exists("/tmp/chunks"):
            os.makedirs("/tmp/chunks")

        path = "/tmp/chunks/0"
        i = 0
        while not os.path.exists(path):
            path = os.path.join("/tmp/chunks", i)
            i = i + 1

        open(path, "wb").write(payload)
        open("/tmp/chunks/index", "a").write("\t".join([str(x) for x in (i, self.x, self.y, self.z, self.sx, self.sy, self.sz)]) + "\n")

    def load_chunk(self, compressed_chunk):
        payload = zlib.decompress(compressed_chunk)

        self.blocks = {}
        for x in range(self.sx+1):
            for z in range(self.sz+1):
                for y in range(self.sy+1):
                    index = y + (z*128) + (x*128*16)
                    #print index, len(payload)
                    kind = ord(payload[index])
                    self.blocks[(x, y, z)] = Block(Vector(x, y, z), kind, 0)

    def multi_change(self, array_size, coords, kinds, metadatas):
        for i in range(array_size):
             # coord is a short comprised of 4 bits of X, 4 bits of Z and 8 bits of Y
             coord = coords[i]
             kind = kinds[i]
             metadata = metadatas[i]

             #b = self.get_relative_block(Vector(x, y, z))
             #b.kind = kind
             #b.metadata = metadata

    def change(self, pos, kind, metadata):
        b = self.get_absolute_block(pos)
        b.kind = kind
        b.metadata = metadata

    def get_relative_block(self, vector):
        v = vector.floor()
        return self.blocks[(v.x, v.y, v.z)]

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

    def get_block(self, pos):
        return self.get_chunk(pos).get_absolute_block(pos)

    def get_chunk(self, pos):
        for chunk in self.chunks:
            if chunk.point_in_chunk(pos):
                return chunk
        raise KeyError("No chunk for region %s" % pos)

    def on_pre_chunk(self, x, z, mode):
        #FIXME: Save incoming chunks to disk and load them in and out of memory depending on where in map we are?
        pass

    def on_map_chunk(self, x, y, z, sx, sy, sz, compressed_chunk_size, compressed_chunk):
        c = Chunk(x, y, z, sx, sy, sz)
        c.load_chunk(compressed_chunk)
        self.chunks.append(c)

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coord_array, type_array, metadata_array):
        pos = Vector(chunk_x * 16, 0, chunk_z * 16)
        c = self.get_chunk(pos)
        c.multi_change(array_size, coord_array, type_array, metadata_array)

    def on_block_change(self, x, y, z, type, metadata):
        pos = Vector(x, y, z)
        self.get_chunk(pos).change(pos, type, metadata)

