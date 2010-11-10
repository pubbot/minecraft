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
from twisted.python import log

from pubbot.chunk import Chunk
from pubbot.vector import Vector


NORTH = Vector(-1, 0, 0)
EAST = Vector(0, 0, -1)
SOUTH = Vector(1, 0, 0)
WEST = Vector(0, 0, 1)
UP = Vector(0, 1, 0)
DOWN = Vector(0, -1, 0)


class World(object):

    def __init__(self):
        self.dump_map_chunks = True
        self.dump_serial = 0

        self.chunks = {}

    def get_block(self, pos):
        return self.get_chunk(pos).get_absolute_block(pos)

    def has_chunk(self, pos):
        pos = pos.floor()
        key = (pos.x // 16, 0, pos.z // 16)
        return key in self.chunks

    def get_chunk(self, pos):
        pos = pos.floor()
        key = (pos.x // 16, 0, pos.z // 16)
        try:
            return self.chunks[key]
        except KeyError:
            raise KeyError("No chunk for region %s" % pos)

    def available(self, pos):
        transforms = [
            NORTH, EAST, SOUTH, WEST, #DOWN, UP,
            NORTH+DOWN, EAST+DOWN, SOUTH+DOWN, WEST+DOWN,
            NORTH+UP, EAST+UP, SOUTH+UP, WEST+UP,
            ]

        for transform in transforms:
            if self.allowed(pos.floor()+transform):
                res = pos.floor()+transform
                log.msg(res)
                yield res

    def allowed(self, pos, allow_fly=True):
        pos = pos.floor()

        block = self.get_block(pos)
        if block.solid:
            log.msg("%s is solid" % pos)
            return False

        # Check block above (for head clearance)
        above_pos = pos.copy() + Vector(0, 1, 0)
        if above_pos.y < 127:
            above = self.get_block(above_pos)
            if above.solid:
                log.msg("above %s is solid" % pos)
                return False

        # Stick to the ground
        if not allow_fly:
            below_pos = pos.copy() - Vector(0, 1, 0)
            below = self.get_block(below_pos)
            if not below.solid and not below.liquid:
                 log.msg("below %s is not solid or liquid" % pos)
                 return False

        return True

    def on_pre_chunk(self, x, z, mode):
        #if mode and not (x, 0, z) in self.chunks:
        #    c = Chunk(x, 0, z)
        #    self.chunks[(x, 0, z)] = c
        #    log.msg("PRECHUNK", x, 0, z)
        #FIXME: Chunk unloading and reloading!!
        pass

    def on_map_chunk(self, x, y, z, sx, sy, sz, compressed_chunk_size, compressed_chunk):
        # x,y,z is the start position of the region, in world block coordinates.
        # To find which chunk is affected, in the same coordinates given by packet 0x32, we shift
        # Whats left is the offset within a chunk
        cx, stx = x >> 4, x & 15
        cy, sty = y >> 7, y & 127
        cz, stz = z >> 4, z & 15

        c = Chunk(cx, cy, cz)
        c.set_compressed(stx, sty, stz, sx, sy, sz, compressed_chunk)
        self.chunks[(cx, cy, cz)] = c

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coord_array, type_array, metadata_array):
        key = (chunk_x, 0, chunk_z)

        if not key in self.chunks:
            #FIXME: Queue these somewhre (VERIFY THEY DONT PREDATE THE MAP CHUNK!!)
            return

        c = self.chunks[(chunk_x, 0, chunk_z)]
        c.multi_change(array_size, coord_array, type_array, metadata_array)

    def on_block_change(self, x, y, z, type, metadata):
        key = (x // 16, 0, z // 16)
        if not key in self.chunks:
            #FIXME: Queue these somewhere (VERIFY THEY DONT PREDATE THE MAP CHUNK!!)
            return

        self.chunks[key].change(Vector(x,y,z), type, metadata)

