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

from math import floor
from StringIO import StringIO

from twisted.internet import defer, task
from twisted.internet.protocol import Protocol
from twisted.web.client import getPage
from twisted.python import log

from pubbot.reader import MinecraftReader, NBTReader
from pubbot.writer import MinecraftWriter


class BaseMinecraftClientProtocol(Protocol):

    """
    I am a basic implementation of the client protocol

    I only ensure successful connection to the server, and do some of the heavy
    lifting processing the protocol. My subclasses are responsible for actually 
    implementing useful clients
    """

    server_password = "Password"

    def __init__(self, username, password, session_id):
        self.username = username
        self.password = password
        self.session_id = session_id
        self.state = "not-ready"

    def connectionMade(self):
        """
        I am called when a connection has been established to a Minecraft server
        """
        self.writer = MinecraftWriter(self.transport)
        self.reader = MinecraftReader()
        self.dataReceived = self.reader.dataReceived

        self.read_loop()

        log.msg("ATTEMPTING TO HANDSHAKE")
        self.send_handshake(self.username)

    def connectionLost(self, reason):
        log.msg("connectionLost", reason)

    @defer.inlineCallbacks
    def read_loop(self):
        """
        I constantly read incoming packets off the wire. I magically suspend when there is no more data
        and resume when there is (see MinecraftReader for how that is implemented)
        """
        log.msg("Entering read loop")
        previous_packet_id = -1

        while True:
            packet_id = yield self.reader.read_packet_id()
            #log.msg("Got packet: 0x%02x" % packet_id)

            if packet_id == 0x00:
                self.on_keep_alive()

            elif packet_id == 0x01:
                unknown1 = yield self.reader.read_int()
                unknown2 = yield self.reader.read_string()
                unknown3 = yield self.reader.read_string()
                self.on_login_response(unknown1, unknown2, unknown3)

            elif packet_id == 0x02:
                connection_hash = yield self.reader.read_string()
                self.on_handshake(connection_hash)

            elif packet_id == 0x03:
                message = yield self.reader.read_string()
                self.on_chat_message(message)

            elif packet_id == 0x04:
                time = yield self.reader.read_long()
                self.on_time_update(time)

            elif packet_id == 0x05:
                type = yield self.reader.read_int()
                count = yield self.reader.read_short()

                payload = {}
                for i in range(count):
                    item_id = yield self.reader.read_short()
                    if item_id != -1:
                        count = yield self.reader.read_byte()
                        health = yield self.reader.read_short()
                        payload[i] = (item_id, count, health)

                self.on_player_inventory(type, count, payload)

            elif packet_id == 0x06:
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
                self.on_spawn_position(x, y, z)

            elif packet_id == 0x10:
                eid = yield self.reader.read_int()
                item_id = yield self.reader.read_short()
                #self.on_holding_change(eid, item_id)

            elif packet_id == 0x0D:
                x = yield self.reader.read_double()
                stance = yield self.reader.read_double()
                y = yield self.reader.read_double()
                z = yield self.reader.read_double()
                yaw = yield self.reader.read_float()
                pitch = yield self.reader.read_float()
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
                pitch = yield self.reader.read_byte()
                current_item = yield self.reader.read_short()
                self.on_named_entity_spawn(eid, player_name, x, y, z, rotation, pitch, current_item)

            elif packet_id == 0x15:
                eid = yield self.reader.read_int()
                item = yield self.reader.read_short()
                count = yield self.reader.read_byte()
                x = yield self.reader.read_int()
                y = yield self.reader.read_int()
                z = yield self.reader.read_int()
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
                yaw = yield self.reader.read_byte()
                pitch = yield self.reader.read_byte()
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
                y = yield self.reader.read_short()
                z = yield self.reader.read_int()
                size_x = yield self.reader.read_byte()
                size_y = yield self.reader.read_byte()
                size_z = yield self.reader.read_byte()
                compressed_chunk_size = yield self.reader.read_int()
                compressed_chunk = yield self.reader.read_raw(compressed_chunk_size)
                self.on_map_chunk(x, y, z, size_x, size_y, size_z, compressed_chunk_size, compressed_chunk)

            elif packet_id == 0x34:
                chunk_x = yield self.reader.read_int()
                chunk_z = yield self.reader.read_int()
                array_size = yield self.reader.read_short()
                coords = yield self.reader.read_array(self.reader.read_short, array_size)
                kinds = yield self.reader.read_array(self.reader.read_byte, array_size)
                metadatas = yield self.reader.read_array(self.reader.read_byte, array_size)
                self.on_multi_block_change(chunk_x, chunk_z, array_size, coords, kinds, metadatas)

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
                payload_raw = yield self.reader.read_raw(payload_size)

                #payload = yield NBTReader(StringIO(payload_raw)).read_nbt()
                #print payload
                payload = {}

                self.on_complex_entity(x, y, z, payload)

            elif packet_id == 0xFF:
                reason = yield self.reader.read_string()
                self.on_kick(reason)
                defer.returnValue(None)

            else:
                log.msg("Got unknown packet_id: %x, Previous was: %x" % (packet_id, previous_packet_id))
                self.send_disconnect("I'm sorry Dave, didn't understand that")
                defer.returnValue(None)

            previous_packet_id = packet_id
            #log.msg("Packet processed")

    def on_keep_alive(self):
        self.send_keep_alive()

    def on_login_response(self, some_int, some_string_1, some_string_2):
        """
        I am sent by the server if it accepts the login request
        """
        pass

    @defer.inlineCallbacks
    def on_handshake(self, connection_hash):
        """
        I am the first packet sent when the client connects and am used for user authentication
        """
        log.msg("on_handshake('%s')" % connection_hash)

        if connection_hash == "-":
            pass
        elif connection_hash == "+":
            pass
        else:
            # Name verification call...
            confirmation = yield getPage("http://www.minecraft.net/game/joinserver.jsp?user=%s&sessionId=%s&serverId=%s" % (self.username, self.session_id, connection_hash.encode("UTF-8")))
            if confirmation != "OK":
                raise ValueError("Minecraft.net says no")

        self.send_login_request(3, self.username, self.server_password, 0, 0)

    def on_chat_message(self, message):
        """
        I am called when the client is sent a chat message
        """
        log.msg("Got message: %s" % message)

    def on_time_update(self, time):
        """
        I am called with the world or region time in minutes
        """
        pass

    def on_player_inventory(self, inv_type, num_items, payload):
        pass

    def on_spawn_position(self, X, Y, Z):
        pass

    def on_player_position_and_look(self, x, stance, y, z, yaw, pitch, on_ground):
        if self.state != "ready":
            self.send_player_position_and_look(x, y, stance, z, yaw, pitch, on_ground)

            self.keepalive = task.LoopingCall(self.send_keep_alive)
            self.keepalive.start(40)

            self.state = "ready"

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

    def on_add_object_vehicle(self, eid, type, x, y, z):
        pass

    def on_mob_spawn(self, eid, type, x, y, z, yaw, pitch):
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

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coords, kinds, metadatas):
        pass

    def on_block_change(self, x, y, z, type, metadata):
        pass

    def on_complex_entity(self, x, y, z, payload):
        pass

    def on_kick(self, reason):
        """
        I am called when the server disconnects a client
        """
        log.msg("Got kicked: %s" % reason)
        self.transport.loseConnection()

    def send_keep_alive(self):
        self.writer.write_packet_id(0x00)

    def send_login_request(self, protocol_version, username, password, unknown1, unknown2):
        self.writer.write_packet_id(0x01)
        self.writer.write_int(protocol_version)
        self.writer.write_string(username)
        self.writer.write_string(password)
        self.writer.write_long(unknown1)
        self.writer.write_byte(unknown2)

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

    def send_player_position(self, x, y, stance, z, on_ground):
        self.writer.write_packet_id(0x0B)
        self.writer.write_double(x)
        self.writer.write_double(y)
        self.writer.write_double(stance)
        self.writer.write_double(z)
        self.writer.write_bool(on_ground)

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
        self.writer.write_float(pitch)
        self.writer.write_bool(on_ground)

    def send_player_digging(self, status, x, y, z, face):
        log.msg("dig", status, x, y, z, face)
        assert status >= 0 and status <= 3
        assert face >= 0 and face <= 5
        self.writer.write_packet_id(0x0E)
        self.writer.write_byte(status)
        self.writer.write_int(floor(x))
        self.writer.write_byte(floor(y))
        self.writer.write_int(floor(z))
        self.writer.write_byte(face)

    def send_player_block_placement(self, block_id, x, y, z, direction):
        log.msg("place block", block_id, x, y, z, direction)
        assert direction >= 0 and direction <= 5
        self.writer.write_packet_id(0x0F)
        self.writer.write_short(block_id)
        self.writer.write_int(floor(x))
        self.writer.write_byte(floor(y))
        self.writer.write_int(floor(z))
        self.writer.write_byte(direction)

    def send_holding_change(self, unused, block_id):
        self.writer.write_packet_id(0x10)
        self.writer.write_int(unused)
        self.writer.write_short(block_id)

    def send_arm_animation(self, unused, waving):
        self.writer.write_packet_id(0x12)
        self.writer.write_int(unused)
        self.writer.write_bool(waving)

    def send_disconnect(self, reason):
        self.writer.write_packet_id(0xFF)
        self.writer.write_string("I'm outta here")

        self.transport.loseConnection()


from pubbot import bot, entities, world

class MinecraftClientProtocol(BaseMinecraftClientProtocol):

    """ I am a concrete implementation of the client protocol, providing a simple bot """

    def __init__(self, username, password, session_id):
        BaseMinecraftClientProtocol.__init__(self, username, password, session_id)
        self.bot = bot.Bot(self)
        self.entities = entities.Entities()
        self.world = world.World()

    def on_player_position_and_look(self, x, stance, y, z, yaw, pitch, on_ground):
        should_start = False
        if self.state != "ready":
            should_start = True

        BaseMinecraftClientProtocol.on_player_position_and_look(self, x, stance, y, z, yaw, pitch, on_ground)

        self.bot.x = x
        self.bot.y = y
        self.bot.z = z
        self.bot.stance = stance
        self.bot.yaw = yaw
        self.bot.pitch = pitch
        self.bot.on_ground = on_ground

        if should_start:
            self.bot.start()

    def on_named_entity_spawn(self, eid, player_name, x, y, z, yaw, pitch, current_item):
        self.entities.on_named_entity_spawn(eid, player_name, x, y, z, yaw, pitch, current_item)

    def on_entity_relative_move(self, eid, x, y, z):
        self.entities.on_entity_relative_move(eid, x, y, z)

    def on_entity_look(self, eid, yaw, pitch):
        self.entities.on_entity_look(eid, yaw, pitch)

    def on_entity_look_and_relative_move(self, eid, x, y, z, yaw, pitch):
        self.entities.on_entity_look_and_relative_move(eid, x, y, z, yaw, pitch)

    def on_entity_teleport(self, eid, x, y, z, yaw, pitch):
        self.entities.on_entity_teleport(eid, x, y, z, yaw, pitch)

    def on_pre_chunk(self, x, z, mode):
        self.world.on_pre_chunk(x, z, mode)

    def on_map_chunk(self, x, y, z, size_x, size_y, size_z, compressed_chunk_size, compressed_chunk):
        self.world.on_map_chunk(x, y, z, size_x, size_y, size_z, compressed_chunk_size, compressed_chunk)

    def on_multi_block_change(self, chunk_x, chunk_z, array_size, coords, kinds, metadatas):
        self.world.on_multi_block_change(chunk_x, chunk_z, array_size, coords, kinds, metadatas)

    def on_block_change(self, x, y, z, type, metadata):
        self.world.on_block_change(x, y, z, type, metadata)

