
class BaseEntity(object):

    def __init__(self, eid, x, y, z, yaw, pitch, roll):
        self.eid = eid
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll


class NamedEntity(BaseEntity):

    def __init__(self, eid, x, y, z, yaw, pitch, player_name, current_item):
        super(NamedEntity, self).__init__(eid, x, y, z, yaw, pitch, 0)
        self.player_nane = player_name
        self.current_item = current_item


class Entities(object):

    def __init__(self):
        self.entities = {}
        self.names = {}

    def on_named_entity_spawn(self, eid, player_name, x, y, z, yaw, pitch, current_item):
        e = NamedEntity(eid, x, y, z, yaw, pitch, player_name, current_item)
        self.entities[eid] = e
        self.names[player_name] = eid

    def on_entity_relative_move(self, eid, x, y, z):
        e = self.entities[eid]
        e.x += x
        e.y += y
        e.z += z

    def on_entity_look(self, eid, yaw, pitch):
        e = self.entites[eid]
        e.yaw = yaw
        e.pitch = pitch

    def on_entity_look_and_relative_move(self, eid, x, y, z, yaw, pitch):
        self.on_entity_look(eid, yaw, pitch)
        self.on_entity_relative_move(eid, x, y, z)

    def on_entity_teleport(self, eid, x, y, z, yaw, pitch):
        e = self.entities[eid]
        e.x = x
        e.y = y
        e.z = z
        e.yaw = yaw
        e.pitch = pitch


