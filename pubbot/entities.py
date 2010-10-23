from twisted.python import log
from pubbot.vector import Vector

class BaseEntity(object):

    def __init__(self, eid, x, y, z, yaw, pitch, roll):
        self.eid = eid
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll

    @property
    def pos(self):
        return Vector(self.x, self.y, self.z)

    def move(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

    def teleport(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class NamedEntity(BaseEntity):

    def __init__(self, eid, x, y, z, yaw, pitch, player_name, current_item):
        super(NamedEntity, self).__init__(eid, x, y, z, yaw, pitch, 0)
        self.player_name = player_name
        self.current_item = current_item


    def move(self, x, y, z):
        super(NamedEntity, self).move(x, y, z)
        log.msg("%s is moving" % self.player_name)

class Entities(object):

    def __init__(self):
        self.entities = {}
        self.names = {}

    def on_named_entity_spawn(self, eid, player_name, x, y, z, yaw, pitch, current_item):
        e = NamedEntity(eid, x/32.0, y/32.0, z/32.0, yaw, pitch, player_name, current_item)
        self.entities[eid] = e
        self.names[player_name] = e

    def on_entity_relative_move(self, eid, x, y, z):
        if not eid in self.entities:
            return
        e = self.entities[eid]
        e.move(x/32.0, y/32.0, z/32.0)

    def on_entity_look(self, eid, yaw, pitch):
        if not eid in self.entities:
            return
        e = self.entities[eid]
        e.yaw = yaw
        e.pitch = pitch

    def on_entity_look_and_relative_move(self, eid, x, y, z, yaw, pitch):
        self.on_entity_look(eid, yaw, pitch)
        self.on_entity_relative_move(eid, x, y, z)

    def on_entity_teleport(self, eid, x, y, z, yaw, pitch):
        if not eid in self.entities:
            return
        e = self.entities[eid]
        e.teleport(x/32.0, y/32.0, z/32.0)
        e.yaw = yaw
        e.pitch = pitch


