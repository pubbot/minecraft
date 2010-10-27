from math import atan2, cos, sin, sqrt, pi, floor

RAD2DEGREE = 180.0 / pi
DEGREE2RAD = pi / 180.0

class Vector(object):

    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def normalize(self):
        length = self.length()
        if not length:
            return Vector(0, 0, 0)
        scale = 1.0 / length
        return Vector(self.x * scale, self.y * scale, self.z * scale)

    def to_angles(self):
        if self.x == 0 and self.z == 0:
            yaw = 0
            if self.y > 0:
                pitch = 90
            else:
                pitch = 270
        else:
            if self.x:
                yaw = atan2(self.x * -1.0, self.z) * RAD2DEGREE
            elif self.z > 0:
                yaw = 90
            else:
                yaw = 270

        forward = sqrt(self.x*self.x + self.z*self.z)
        pitch = atan2(self.y, forward) * RAD2DEGREE

        return (yaw+180, pitch)

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

    def __idiv(self, other):
        self.x /= other
        self.y /= other
        self.z /= other
        return self


def dot_product(a, b):
    return a.x*b.x + a.y*b.y + a.z*b.z

def cross_product(a, b):
    return Vector(a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x)


def forward(yaw, pitch):
    #PLZ FIXY ME
    yaw *= DEGREE2RAD
    pitch *= DEGREE2RAD
    return Vector(-1 * cos(pitch) * cos(yaw), -sin(pitch), cos(pitch) * sin(yaw))

