
from struct import pack, unpack

from twisted.internet import defer
from twisted.internet.protocol.Protocol import BaseProtocol
from twisted.web.client import getPage


class MinecreaftReader(object):

    def __init__(self, data):
        self.data = data
        self.length_wanted = 0
        self.callback = None

    def dataReceived(self, data):
        self.data += data

        if self.callback and len(self.data) >= self.length_wanted:
            callback, self.callback = self.callback, None
            callback.callback(None)

    @defer.inlineCallbacks
    def read_raw(self, num_bytes):
        """
        I read x bytes from the server, if there isnt enough data then i yield a Deferred
        effectively pausing the current code until the rest of the data is available
        """
        if len(self.data) <= num_bytes:
             # Not enough data: Pause this function until there is
             self.length_wanted = num_bytes
             self.callback = defer.Deferred()
             yield self.callback

        # Pop the data off the front of data and return it
        data = self.data[0:num_bytes]
        self.data = self.data[num_bytes:]
        defer.returnValue(data)

    @defer.inlineCallbacks
    def read_packet_id(self):
        val = unpack(">B", yield self.read_raw(1))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_byte(self):
        val = unpack(">b", yield self.read_raw(1))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_short(self):
        val = unpack(">h", yield self.read_raw(2))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_int(self):
        val = unpack(">i", yield self.read_raw(4))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_long(self):
        val = unpack(">l", yield self.read_raw(8))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_float(self):
        val = unpack(">f", yield self.read_raw(4))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_double(self):
        val = unpack(">d", yield self.read_raw(8))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_string(self):
        length = yield self.read_short()
        val = unpack(">%ds" % length, self.read_raw(length))
        defer.returnValue(val)

    @defer.inlineCallbacks
    def read_bool(self):
        val = yield self.read_byte()
        if val:
            return True
        else:
            return False

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
        self.reader = MinecraftReader()
        self.dataReceived = self.reader.dataReceived

        self.send_handshake(self.username)

    @defer.inlineCallbacks
    def read_loop(self):
        """
        I constantly read incoming packets off the wire. I magically suspend when there is no more data
        and resume when there is (see MinecraftReader for how that is implemented)
        """
        while True:
            packet_id = yield self.reader.read_packet_id()

            if packet_id == 0x01:
                unknown1 = yield self.reader.read_int()
                unknown2 = yield self.reader.read_string()
                unknown3 = yield self.reader.read_string()
                self.on_login_response(unknown1, unknown2, unknown3)

            elif packet_id == 0x02:
                connection_hash = yield self.reader.read_string()
                self.on_handshake(connection_hash)

            elif packet_id == 0x03:
                message = yield self.reader.read_string()
                self.on_message(message)

            elif packet_id == 0x04:
                time = yield self.read_long()
                self.on_time(time)

            elif packet_id == 0x05:
                type = yield self.reader.read_int()
                count = yield self.reader.read_short()
                payload = yield self.reader.read_raw(count)
                self.on_player_inventory(type, count, payload)

            elif packet_id == 0x06:
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
                self.on_spawn_position(x, y, z)

            elif packet_id == 0x0D:
                x = yield self.reader.read_double()
                stance = yield self.reader.read_double()
                y = yield self.reader.read_double()
                z = yield slef.reader.read_double()
                yaw = yield self.reader.read_float()
                pitch = yield self.reader.read_pitch()
                on_ground = yield self.reader.read_bool()
                self.on_player_position_and_look(x, stance, y, z, yaw, pitch, on_ground)

            elif packet_id == 0x11:
                item_type = yield self.reader.read_short()
                count = yield self.reader.read_byte()
                life = yield self.reader.read_short()
                self.on_add_to_inventory(item_type, count, life)

            elif packet_id == 0x12:
                eid = yield self.reader.read_int()
                animate = yield self.reader.read_bool()
                self.on_arm_animation(eid, animate)

            elif packet_id == 0x14:
                eid = yield self.reader.read_int()
                player_name = yield self.reader.read_string()
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
                rotation = yield self.reader.read_byte()
                pitch = yield self.reader.read_pitch()
                current_item = yield self.reader.read_short()
                self.on_named_entity_spawn(eid, player_name, x, y, z, rotation, pitch, current_item)

            elif packet_id == 0x15:
                eid = yield self.reader.read_int()
                item = yield self.reader.read_short()
                count = yield self.reader.read_byte()
                x = yield self.read_int()
                y = yield self.read_int()
                z = yield self.read_int()
                rotation = yield self.reader.read_byte()
                pitch = yield self.reader.read_byte()
                roll = yield self.reader.read_byte()
                self.on_pickup_spawn(eid, item, count, x, y, z, rotation, pitch, roll)

            elif packet_id == 0x16:
                collected_eid = yield self.reader.read_int()
                collector_eid = yield self.reader.read_int()
                self.on_collect_item(collected_eid, collector_eid)

            elif packet_id == 0x17:
                eid = yield self.reader.read_int()
                type = yield self.reader.read_byte()
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
                self.on_add_object_vehicle(eid, type, x, y, z)

            elif packet_id == 0x18:
                eid = yield self.reader.read_int()
                type = yield self.reader.read_byte()
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
                yaw = yield self.reader.read_byte()
                pitch = yield self.reader.read_byte()
                self.on_mob_spawn(eid, type, x, y, z, yaw, pitch)

            elif packet_id == 0x1D:
                eid = yield self.reader.read_int()
                self.on_destroy_entity(eid)

            elif packet_id == 0x1E:
                eid = yield self.reader.read_int()
                self.on_entity(eid)

            elif packet_id == 0x1F:
                eid = yield self.reader.read_int()
                x = yield self.reader.read_byte()
                y = yield self.reader.read_byte()
                z = yield self.reader.read_byte()
                self.on_entity_relative_move(eid, x, y, z)

            elif packet_id == 0x20:
                eid = yield self.reader.read_int()
                yaw = yield self.reader.read_byte()
                pitch = yield self.reader.read_byte()
                self.on_entity_look(eid, yaw, pitch)

            elif packet_id == 0x21:
                eid = yield self.reader.read_int()
                x = yield self.reader.read_byte()
                y = yield self.reader.read_byte()
                z = yield self.reader.read_byte()
                yaw = yield self.read_byte()
                pitch = yield self.read_byte()
                self.on_entity_look_and_relative_move(eid, x, y, z, yaw, pitch)

            elif packet_id == 0x22:
                eid = yield self.reader.read_int()
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
                yaw = yield self.reader.read_byte()
                pitch = yield self.reader.read_byte()
                self.on_entity_teleport(eid, x, y, z, yaw, pitch)

            elif packet_id == 0x32:
                x = yield self.reader.read_int()
                z = yield self.reader.read_int()
                mode = yield self.reader.read_bool()
                self.on_pre_chunk(x, z, mode)

            elif packet_id == 0x33:
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
                size_x = yield self.reader.read_byte()
                size_y = yield self.reader.read_byte()
                size_z = yield self.reader.read_byte()
                compressed_chunk_size = yield self.reader.read_int()
                compressed_chunk = yield self.read_raw(compressed_chunk_size)
                self.on_map_chunk(self, x, y, z, slice_x, slice_y, slice_z, compressed_chunk_size, compressed_chunk)

            elif packet_id == 0x34:
                chunk_x = yield self.reader.read_int()
                chunk_z = yield self.reader.read_int()
                array_size = yield self.reader.read_short()
                coordinate_array = yield self.reader.read_raw(1 * array_size)
                type_array = yield self.reader.read_raw(1 * array_size)
                metadata_array = yield self.reader.read_raw(1 * array_size)
                self.on_multi_block_change(chunk_x, chunk_z, array_size, coordinate_array, type_array, metadata_array)

            elif packet_id == 0x35:
                x = yield self.reader.read_int()
                y = yield self.reader.read_byte()
                z = yield self.reader.read_int()
                type = yield self.reader.read_byte()
                metadata = yield self.reader.read_byte()
                self.on_block_change(x, y, z, type, metadata)

            elif packet_id == 0x3B:
                x = yield self.reader.read_int()
                y = yield self.reader.read_short()
                z = yield self.reader.read_int()
                payload_size = yield self.reader.read_short()
                payload = yield self.reader.read_raw(payload_size)
                self.on_complex_entities(x, y, z, payload_size, payload)

            elif packet_id == 0xFF:
                reason = yield self.reader.read_string()
                self.on_kick(reason)
                defer.returnValue(None)

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

