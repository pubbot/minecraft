
from struct import pack, unpack

from twisted.internet import defer
from twisted.internet.protocol.Protocol import BaseProtocol
from twisted.web.client import getPage


class MinecraftWriter(object):

    def __init__(self, transport):
        self.transport = transport

    def write_packet_id(self, val):
        self.transport.write(pack(">B", val))

    def write_byte(self, val):
        self.transport.write(pack(">b", val))

    def write_short(self, val):
        self.transport.write(pack(">h", val))

    def write_int(self, val):
        self.transport.write(pack(">i", val))

    def write_long(self, val):
        self.transport.write(pack(">l", val))

    def write_float(self, val):
        self.transport.write(pack(">f", val))

    def write_double(self, val):
        self.transport.write(pack(">d", val))

    def write_string(self, val):
        self.write_short(len(val))
        self.trasnport.write(pack(">%ds" % len(val), val))

    def write_bool(self, val):
        if val:
            self.write_byte(1)
        else:
            self.write_byte(0)


class MinecraftClientProtocol(BaseProtocol):

    server_password = None

    #def makeConnection(self, transport):
    #    pass

    def connectionMade(self):
        """
        I am called when a connection has been established to a Minecraft server
        """
        self.writer = MinecraftWriter(self.transport)
        self.send_handshake(self.username)

    def dataReceived(self, data):
        pass

    def on_login_response(self, some_int, some_string_1, some_string_2):
        """
        I am sent by the server if it accepts the login request
        """
        pass

    @defer.inlineCallback
    def on_handshake(self, connection_hash):
        """
        I am the first packet sent when the client connects and am used for user authentication
        """
        if connection_hash == "-":
            pass
        elif connection_hash == "+":
            pass
        else:
            # If hash isnt "-" or "+" then we have an hash we need to pass to the minecraft servers to authenticate this user
            page = yield getPage("http://www.minecraft.net/game/getversion.jsp?user=%s&password=%s&version=11" % (self.username, self.password))
            try:
                version, ticket, self.username, self.session_id = page.split(":")
            except:
                raise ValueError("Need to raise a better exception, but '%s' isnt a valid handshake.." % page)

            # Name verification call...
            confirmation = yield getPage("http://www.minecraft.net/game/joinserver.jsp?user=<username>&sessionId=<session id>&serverId=<server hash>" % (self.username, self.session_id, connection_hash))
            if confirmation != "ok":
                raise ValueError("Minecraft.net says no")

        self.send_login_request(2, self.username, self.server_password)

    def on_chat_message(self, message):
        """
        I am called when the client is sent a chat message
        """
        pass

    def on_time_update(self, time):
        """
        I am called with the world or region time in minutes
        """
        pass

    def on_player_inventory(self, inv_type, num_items, payload):
        pass

    def on_spawn_position(self, X, Y, Z):
        pass

    def on_player_position_and_look(self, X, stance, Y, Z, yaw, pitch, onground):
        pass

    def on_add_to_inventory(self, item_type, count, life):
        pass

    def on_arm_animation(self, eid, animate):
        pass

    def on_named_entity_spawn(self, eid, player_name, x, y, z, rotation, pitch, current_item):
        pass

    def on_pickup_spawn(self, eid, item, count, x, y, z, rotation, pitch, roll):
        pass

    def on_collect_item(self, collected_eid, collector_eid):
        pass

    def on_add_object_vehicle(self. eid, type, x, y, z):
        pass

    def on_mob_spawn(self, eid, type, x, y, z yaw, pitch):
        pass

    def on_destroy_entity(self, eid):
        pass

    def on_entity(self, eid):
        pass

    def on_entity_relative_move(self, eid, x, y, z):
        pass

    def on_entity_look(self, eid, yaw, pitch):
        pass

    def on_entity_look_and_relative_move(self, eid, x, y, z, yaw, pitch):
        pass

    def on_entity_teleport(self, eid, x, y, z, yaw, pitch):
        pass

    def on_pre_chunk(self, x, z, mode):
        pass

    def on_map_chunk(self, x, y, z, size_x, size_y, size_z, compressed_chunk_size, compressed_chunk):
        pass

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coord_array, type_array, metadata_array):
        pass

    def on_complex_entities(self, x, y, z, payload_size, payload):
        pass

    def on_kick(self, reason):
        """
        I am called when the server disconnects a client
        """
        self.transport.loseConnection()

    def send_keep_alive(self):
        self.writer.write_packet_id(0x00)

    def send_login_request(self, protocol_version, username, password):
        self.writer.write_packet_id(0x01)
        self.writer.write_int(protocol_version)
        self.writer.write_string(username)
        self.writer.write_string(password)

    def send_handshake(self, username):
        self.writer.write_packet_id(0x02)
        self.writer.write_string(username)

    def send_chat_message(self, message):
        self.writer.write_packet_id(0x03)
        self.writer.write_string(message)

    def send_player_inventory(self, type, count, payload):
        assert False, "Not figured out size/structure of payload yet"
        self.writer.write_packet_id(0x05)
        self.writer.write_int(type)
        self.writer.write_short(count)
        self.writer.write_xxxx(payload)

    def send_player(self, on_ground):
        self.writer.write_packet_id(0x0A)
        self.writer.write_bool(on_ground)

    def send_player_position(self, s, y, stance, z, on_ground):
        self.writer.write_packet_id(0x0B)
        self.writer.write_double(x)
        self.writer.write_double(y)
        self.writer.write_double(stance)
        self.writer.write_double(z)

    def send_player_look(self, yaw, pitch, on_ground):
        self.writer.write_packet_id(0x0C)
        self.writer.write_float(yaw)
        self.writer.write_float(pitch)
        self.writer.write_bool(on_ground)

    def send_player_position_and_look(self, x, y, stance, z, yaw, pitch, on_ground):
        self.writer.write_packet_id(0x0D)
        self.writer.write_double(x)
        self.writer.write_double(y)
        self.writer.write_double(stance)
        self.writer.write_double(z)
        self.writer.write_float(yaw)
        self.writer.write_pitch(pitch)
        self.writer.write_bool(on_ground)

    def send_player_digging(self, status, x, y, z, face):
        assert status >= 0 and status <= 3
        assert face >= 0 and face <= 5
        self.writer.write_packet_id(0x0E)
        self.writer.write_byte(status)
        self.writer.write_int(x)
        self.writer.write_byte(y)
        self.writer.write_int(z)
        self.writer.write_byte(face)

    def send_player_block_placement(self, block_id, x, y, z, direction):
        assert direction >= 0 and direction <= 5
        self.writer.write_packet_id(0x0F)
        self.writer.write_short(block_id)
        self.writer.write_int(x)
        self.writer.write_byte(y)
        self.writer.write_int(z)
        self.writer.write_byte(direction)

    def send_holding_change(self, unused, block_id):
        self.writer.write_packet_id(0x10)
        self.writer.write_int(unused)
        self.writer.write_short(block_id)

    def send_disconnect(self, reason):
        self.writer.write_packet_id(0xFF)
        self.writer.write_string("I'm outta here")

        self.transport.loseConnection()

