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
from twisted.protocols.policies import TimeoutMixin

from bravo.packets.beta import parse_packets, make_packet, make_error_packet

from pubbot.vector import Vector

(STATE_UNAUTHENTICATED, STATE_AUTHENTICATED) = range(2)


class BetaClientProtocol(object, Protocol, TimeoutMixin):
    """
    The Minecraft Alpha/Beta client protocol.

    This class is mostly designed to be a skeleton for featureful clients.
    You will need to subclass to make it do useful things.
    """

    server_password = "Password"

    def __init__(self, username, password, session_id):
        self.username = username
        self.password = password
        self.session_id = session_id

        self.state = STATE_UNAUTHENTICATED

        self.handlers = {
            0: self.ping,
            1: self.login_response,
            2: self.handshake,
            3: self.chat_message,
            4: self.time_update,
            5: self.entity_equipment,
            6: self.spawn_position,
            7: self.use,
            8: self.player_health,
            9: self.player_respawn,
            13: self.player_position_and_look,
            16: self.holding_change,
            17: self.use_bed,
            18: self.arm_animation,
            19: self.action,
            20: self.named_entity_spawn,
            21: self.pickup_spawn,
            22: self.collect_item,
            23: self.add_object_vehicle,
            24: self.mob_spawn,
            25: self.painting,
            27: self.unknown,
            28: self.unknown,
            29: self.destroy_entity,
            30: self.entity,
            31: self.entity_relative_move,
            32: self.entity_look,
            33: self.entity_look_and_relative_move,
            34: self.entity_teleport,
            38: self.entity_damage,
            39: self.unknown,
            40: self.unknown,
            50: self.pre_chunk,
            51: self.map_chunk,
            52: self.multi_block_change,
            53: self.block_change,
            54: self.unknown,
            59: self.complex_entity,
            60: self.unknown,
            70: self.complex_entity,
            100: self.unknown,
            101: self.unknown,
            103: self.unknown,
            104: self.unknown,
            105: self.unknown,
            106: self.unknown,
            130: self.unknown,
            255: self.kick,
            }

    def connectionMade(self):
        """
        I am called when a connection has been established to a Minecraft server
        """
        self.send_handshake(self.username)

     def dataReceived(self, data):
         self.buf += data

         packets, self.buf = parse_packets(self.buf)

         if packets:
             self.resetTimeout()

         for header, payload in packets:
             if header in self.handlers:
                 self.handlers[header](payload)
             else:
                 log.err("Didn't handle parseable packet %d!" % header)
                 log.err(payload)


    def ping(self, payload):
        self.send_keep_alive()

    def login_response(self, payload):
        """
        I am sent by the server if it accepts the login request
        """
        pass

    @defer.inlineCallbacks
    def handshake(self, payload):
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
            confirmation = yield getPage("http://www.minecraft.net/game/joinserver.jsp?user=%s&sessionId=%s&serverId=%s" % (self.username, self.session_id, connection_hash.encode("UTF-8")), timeout=60)
            if confirmation != "OK":
                raise ValueError("Minecraft.net says no")

        self.send_login_request(10, self.username, self.server_password, 0, 0)

    def chat_message(self, payload):
        """
        I am called when the client is sent a chat message
        """
        log.msg("Got message: %s" % message)

    def time_update(self, payload):
        """
        I am called with the world or region time in minutes
        """
        pass

    def player_inventory(self, payload):
        pass

    def spawn_position(self, payload):
        pass

    def player_position_and_look(self, player):
        self.send_player_position_and_look(x, y, stance, z, yaw, pitch, on_ground)

        if self.state != STATE_AUTHENTICATED:
            self.keepalive = task.LoopingCall(self.send_keep_alive)
            self.keepalive.start(40)

            self.state = STATE_AUTHENTICATED

    def player_health(self, half_hearts):
        pass

    def add_to_inventory(self, payload):
        pass

    def arm_animation(self, payload):
        pass

    def named_entity_spawn(self, payload):
        pass

    def pickup_spawn(self, payload):
        pass

    def collect_item(self, payload):
        pass

    def add_object_vehicle(self, payload):
        pass

    def mob_spawn(self, payload):
        pass

    def destroy_entity(self, payload):
        pass

    def entity(self, payload):
        pass

    def entity_relative_move(self, payload):
        pass

    def entity_look(self, payload):
        pass

    def entity_look_and_relative_move(self, payload):
        pass

    def entity_teleport(self, payload):
        pass

    def pre_chunk(self, payload):
        pass

    def map_chunk(self, payload):
        pass

    def multi_block_change(self, payload):
        pass

    def block_change(self, payload):
        pass

    def complex_entity(self, payload):
        pass

    def kick(self, payload):
        """
        I am called when the server disconnects a client
        """
        log.msg("Got kicked: %s" % reason)
        self.transport.loseConnection()

    def invalid_bed(self, payload):
        pass

    def write_packet(self, header, **payload):
        """
        Send a packet to the server.
        """
        self.transport.write(make_packet(header, **payload))


