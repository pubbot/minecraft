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

from math import ceil, floor, fabs

from twisted.python import log

from pubbot.vector import Vector

INF = 1.e+20

def walk(start, dir):
    dir = dir.normalize()

    if dir.x < 0:
        mx = (floor(dir.x) - start.x) / dir.x
        sx = -1
        dx = 1 / -dir.x
    elif dir.x > 0:
        mx = (floor(dir.x+1) - start.x) / dir.x
        sx = 1
        dx = 1 / dir.x
    else:
        mx = INF
        sx = 0
        dx = 0

    if dir.y < 0:
        my = (floor(dir.y) - start.y) / dir.y
        sy = -1
        dy = 1 / -dir.y
    elif dir.y > 0:
        my = (floor(dir.y+1) - start.y) / dir.y
        sy = 1
        dy = 1 / dir.y
    else:
        my = INF
        sy = 0
        dy = 0

    if dir.z < 0:
        mz = (floor(dir.z) - start.z) / dir.z
        sz = -1
        dz = 1 / -dir.z
    elif dir.z > 0:
        mz = (floor(dir.z+1) - start.z) / dir.z
        sz = 1
        dz = 1 / dir.z
    else:
        mz = INF
        sz = 0
        dz = 0

    X, Y, Z = floor(start.x), floor(start.y), floor(start.z)
    yield Vector(X, Y, Z)

    while True:
        if mx < min(my, mz):
            X += sx
            mx += dx
        elif my < mz:
            Y += sy
            my += dy
        else:
            Z += sz
            mz += dz

        yield Vector(X, Y, Z)

