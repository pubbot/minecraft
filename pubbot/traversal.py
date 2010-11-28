from math import ceiling, floor

from pubbot.vector import Vector

def walk(start, dir):
    dir = dir.normalize()

    X, Y, Z = floor(start.x), floor(start.y), floor(start.z)
    yield Vector(X, Y, Z)

    pos = start.copy()
    while True:
        dx = ceiling(pos.x) - pos.x
        dy = ceiling(pos.y) - pos.y
        dz = ceiling(pos.z) - pos.z

        if dx <= min(dy, dz):
            ratio = dx / pos.x
        elif dy <= min(dx, dz):
            ratio = dy / pos.y
        else:
            ratio = dz / pos.z

        pos += dir * ratio

        X, Y, Z = floor(pos.x), floor(pos.y), floor(pos.z)
        yield Vector(X, Y, Z)
