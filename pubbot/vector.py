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

# Maths stuff. Totally a NIH, to try and learn stuff.

from math import atan2, cos, sin, sqrt, pi, floor, degrees, radians


class Vector(object):

    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def manhattan_length(self):
        return abs(self.x) + abs(self.y) + abs(self.z)

    def normalize(self):
        length = self.length()
        if not length:
            return Vector(0, 0, 0)
        scale = 1.0 / length
        return Vector(self.x * scale, self.y * scale, self.z * scale)

    def to_angles(self):
        forward = sqrt(self.x*self.x + self.z*self.z)
        yaw = degrees(atan2(self.x * -1.0, self.z))
        pitch = 360 - degrees(atan2(self.y, forward))

        while yaw > 360:
            yaw -= 360
        while yaw < 0:
            yaw += 360

        while pitch > 360:
            pitch -= 360
        while pitch < 0:
            pitch += 360

        return (yaw, pitch)

    def floor(self):
        return Vector(int(floor(self.x)), int(floor(self.y)), int(floor(self.z)))

    def copy(self):
        return Vector(self.x, self.y, self.z)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y, self.z-other.z)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        self.z *= other
        return self

    def __div__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

    def __idiv__(self, other):
        self.x /= other
        self.y /= other
        self.z /= other
        return self

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Vector(%s, %s, %s)" % (self.x, self.y, self.z)

    def __hash__(self):
        return id(",".join(str(x) for x in (self.x, self.y, self.z)))


def dot_product(a, b):
    return a.x*b.x + a.y*b.y + a.z*b.z

def cross_product(a, b):
    return Vector(a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x)


def forward(yaw, pitch):
    yaw = radians(yaw)
    pitch = radians(pitch)

    x = -1 * cos(pitch) * sin(yaw)
    y = -sin(pitch)
    z = cos(yaw) * cos(pitch)

    return Vector(x, y, z)

