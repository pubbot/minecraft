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

from pubbot.chunk import Chunk
from pubbot.vector import Vector


NORTH = Vector(-1, 0, 0)
EAST = Vector(0, 0, -1)
SOUTH = Vector(1, 0, 0)
WEST = Vector(1, 0, 0)
UP = Vector(0, 1, 0)
DOWN = Vector(0, -1, 0)


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

    def available(self, pos):
        transforms = [
            NORTH, EAST, SOUTH, WEST, DOWN, UP,
            ]

        for transform in transforms:
            if self.allowed(pos+transform):
                yield pos+transform

    def allowed(self, pos, allow_fly=True):
        block = self.get_block(pos)
        if block.solid:
            return False

        # Check block above (for head clearance)
        above_pos = pos.copy() + Vector(0, 1, 0)
        if above_pos.y < 127:
            above = self.get_block(above_pos)
            if above.solid:
                return False

        # Stick to the ground
        if allow_fly:
            below_pos = pos.copy() - Vector(0, 1, 0)
            below = self.get_block(below_pos)
            if not below.solid and not below.liquid:
                 return False

        return True

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

