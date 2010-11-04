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

from twisted.internet import threads, defer

from pubbot.vector import Vector
from pubbot.blocks import blocks


class Block(object):

    __slots__ = ("pos", "kind", "metadata")

    faces = (
        Vector(0.5,0.0,0.5),   #0, -Y
        Vector(0.5,1.0,0.5),   #1, +Y
        Vector(0.5,0.5,0.0),   #2, -Z
        Vector(0.5,0.5,1.0),   #3, +Z
        Vector(0.0,0.5,0.5),   #4, -X
        Vector(1.0,0.5,0.5),   #5, +X
        )

    def __init__(self, pos, kind, metadata):
        self.pos = pos
        self.kind = kind
        self.metadata = metadata

    @property
    def preferred_tool(self):
        try:
            return blocks[self.kind]["preferred_tool"]
        except KeyError:
            return 0x104

    @property
    def ttl(self):
        try:
            return blocks[self.kind]["times"][self.preferred_tool]
        except KeyError:
            return 20.0

    @property
    def ftl(self):
        return int(math.ceil(self.ttl * 12))

    @property
    def name(self):
        return blocks[self.kind]["name"]

    def get_faces(self, observer):
        """
        Given the vector of an observer, work out which of my sides they can best see

        Returns a list of faces they can see, with the nearest first
        """
        faces = [(face, self.pos + self.faces[face]) for face in range(6)]
        faces.sort(key=lambda x: (observer-x[1]).length())
        return faces[0:3]


class Chunk(object):

    __slots__ = ("pos", "sx", "sy", "sz", "blocks", "compressed")

    def __init__(self, pos):
        # Record start of chunk.
        self.pos = pos

        # Assume normal size
        self.sx = 16
        self.sy = 128
        self.sz = 16

        self.blocks = {}

    def set_size(self, sx, sy, sz):
        self.sx = sx
        self.sy = sy
        self.sz = sz

    def set_compressed(self, compressed):
        self.compressed = compressed

    def dump_chunk(self, payload):
        if not os.path.exists("/tmp/chunks"):
            os.makedirs("/tmp/chunks")

        path = "/tmp/chunks/0"
        i = 0
        while os.path.exists(path):
            path = os.path.join("/tmp/chunks", str(i))
            i = i + 1

        open(path, "wb").write(payload)
        open("/tmp/chunks/index", "a").write("\t".join([str(x) for x in (i, self.pos.x, self.pos.y, self.pos.z, self.sx, self.sy, self.sz)]) + "\n")

    def load_chunk(self):
        if not self.compressed:
            return

        payload = zlib.decompress(self.compressed)

        if False:
            self.dump_chunk(payload)

        ox, oy, oz = self.pos.x, self.pos.y, self.pos.z

        self.blocks = {}
        for x in range(self.sx+1):
            for z in range(self.sz+1):
                for y in range(self.sy+1):
                    index = y + (z*(self.sy+1)) + (x*(self.sy+1)*(self.sz+1))
                    #print index, len(payload)
                    kind = ord(payload[index])
                    self.blocks[(x, y, z)] = Block(Vector(ox + x, oy + y, oz + z), kind, 0)

        self.compressed = None

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
        if self.compressed:
            self.load_chunk()
        v = vector.floor()
        return self.blocks[(v.x, v.y, v.z)]

    def get_absolute_block(self, vector):
        rel = vector - self.pos
        return self.get_relative_block(rel)

    def contains(self, vector):
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

    def has_chunk(self, pos):
        for chunk in self.chunks:
            if chunk.contains(pos):
                return True
        return False

    def get_chunk(self, pos):
        for chunk in self.chunks:
            if chunk.contains(pos):
                return chunk
        raise KeyError("No chunk for region %s" % pos)

    def on_pre_chunk(self, x, z, mode):
        #FIXME: Save incoming chunks to disk and load them in and out of memory depending on where in map we are?
        #c = Chunk(x*16, 0, z*16)
        #self.chunks.append(c)
        pass

    def on_map_chunk(self, x, y, z, sx, sy, sz, compressed_chunk_size, compressed_chunk):
        c = Chunk(Vector(x, y, z))
        c.set_size(sx, sy, sz)
        c.set_compressed(compressed_chunk)
        self.chunks.append(c)

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coord_array, type_array, metadata_array):
        pos = Vector(chunk_x * 16, 0, chunk_z * 16)
        if not self.has_chunk(pos):
            #FIXME: Queue these somewhere...
            return
        c = self.get_chunk(pos)
        c.multi_change(array_size, coord_array, type_array, metadata_array)

    def on_block_change(self, x, y, z, type, metadata):
        pos = Vector(x, y, z)
        if not self.has_chunk(pos):
            #FIXME: Queue these somewhere...
            return
        self.get_chunk(pos).change(pos, type, metadata)

