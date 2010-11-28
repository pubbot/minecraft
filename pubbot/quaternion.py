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

# http://3dengine.org/Quaternions

from math import sin, cos, radians

from pubbot.vector import Vector

class Quaternion(object):

    __slots__ = ("w", "x", "y", "z")

    def __init__(self, x, y, z, w):
        angle = (w / 180.0) * 3.1415926
        result = sin(angle / 2.0)
        self.w = cos(angle / 2.0)
        self.x = x * result
        self.y = y * result
        self.z = z * result

    @property
    def forward(self):
        x = 1.0 - 2.0 * (self.y * self.y + self.z * self.z)
        y = 2.0 * (self.x * self.y - self.z * self.w)
        z = 2.0 * (self.x * self.z + self.y * self.w)
        return Vector(x, y, z)

    @property
    def up(self):
        x = 2.0 * (self.x * self.y + self.z * self.w)
        y = 1.0 - 2.0 * (self.x * self.x + self.z * self.z)
        z = 2.0 * (self.y * self.z - self.x * self.w)
        return Vector(x, y, z)

    @property
    def right(self):
        x = 2.0 * (self.x * self.z - self.y * self.w)
        y = 2.0 * (self.z * self.y + self.x * self.w )
        z = 1.0 - 2.0 * (self.x * self.x + self.y * self.y)
        return Vector(x, y, z)

    def __mul__(self, b):
        r = Quaternion(0, 0, 0, 0)
        r.w = self.w * b.w - self.x * b.x - self.y * b.y - self.z * b.z
        r.x = self.w * b.x + self.x * b.w + self.y * b.z - self.z * b.y
        r.y = self.w * b.y + self.y * b.w + self.z * b.x - self.x * b.z
        r.z = self.w * b.z + self.z * b.w + self.x * b.y - self.y * b.x
        return r

def directions(yaw, pitch, roll=0):
    return Quaternion(0.0, 0.0, 1.0, pitch) * \
        Quaternion(1.0, 0.0, 0.0, roll) * \
        Quaternion(0.0, 1.0, 0.0, yaw-270)

