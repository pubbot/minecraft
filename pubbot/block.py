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


