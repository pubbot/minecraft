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

# A Chunk is a segment of world containing blocks, up to 16x16x128

import os, zlib, math

from twisted.internet import threads, defer
from twisted.python import log

from pubbot.block import Block
from pubbot.vector import Vector


class Chunk(object):

    __slots__ = ("x", "y", "z", "blocks", "compressed")

    def __init__(self, x, y, z):
        # Record start of chunk.
        self.x = x
        self.y = y
        self.z = z

        # Assume normal size
        #self.sx = 16
        #self.sy = 128
        #self.sz = 16

        self.compressed = None

        self.blocks = {}

    def set_compressed(self, *payload):
        self.compressed = payload

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

        log.msg("Attempting to load", *self.compressed[:-1])

        stx, sty, stz, sx, sy, sz, compressed = self.compressed

        payload = zlib.decompress(compressed)

        if False:
            self.dump_chunk(payload)

        ox, oy, oz = self.x*16, self.y, self.z*16

        self.blocks = {}
        for x in range(stx, sx+1):
            for z in range(stz, sz+1):
                for y in range(sty, sy+1):
                    index = y + (z*(sy+1)) + (x*(sy+1)*(sz+1))
                    #print index, len(payload)
                    kind = ord(payload[index])
                    self.blocks[(x, y, z)] = Block(Vector(ox + x, oy + y, oz + z), kind, 0)

        self.compressed = None

    def multi_change(self, array_size, coords, kinds, metadatas):
        for i in range(array_size):
             # coord is a short comprised of 4 bits of X, 4 bits of Z and 8 bits of Y
             coord = coords[i]
             x = (coord & 0xF000) >> 12
             z = (coord & 0x0F00) >> 8
             y = (coord & 0x00FF)

             kind = kinds[i]
             metadata = metadatas[i]

             b = self.get_relative_block(Vector(x, y, z))
             b.kind = kind
             b.metadata = metadata

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
        rel = vector - Vector(self.x*16, self.y, self.z*16)
        return self.get_relative_block(rel)

    def contains(self, vector):
        if vector.x < self.pos.x or self.pos.x + 16  <= vector.x:
             return False
        if vector.y < self.pos.y or self.pos.z + 128 <= vector.y:
            return False
        if vector.z < self.pos.z or self.pos.z + 16 <= vector.z:
            return False

        return True


