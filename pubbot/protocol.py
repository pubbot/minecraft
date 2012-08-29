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

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5

from . import bot, entities, world
from .packets import make_packet, parse_packets, packet_names
from .utils import *


class BaseMinecraftClientProtocol(Protocol):

    """
    I am a basic implementation of the client protocol

    I only ensure successful connection to the server, and do some of the heavy
    lifting processing the protocol. My subclasses are responsible for actually 
    implementing useful clients
    """

    VERSION = 39

    def __init__(self, username, password, session):
        self.username = username
        self.password = password
        self.session = session
        self.buffered = ""
        self.encryption_on = False

    def dataReceived(self, data):
        if self.encryption_on:
            data = self.decryptor.decrypt(data)

        packets, self.buffered = parse_packets(self.buffered + data)
        for p in packets:
            packet_id, packet = p
            packet_name = packet_names[packet_id]
            #if not packet_id in (0x38, 0x33):
            #    log.msg("SERVER %s %s" % (packet_name, packet))
            #else:
            #    log.msg("SERVER %s" % packet_name)

            try:
                fn = getattr(self, "on_" + packet_name.replace("-", "_"))
            except AttributeError:
                #log.msg("Packet not processed: %s %s" % (packet_id, packet_name))
                continue
            fn(packet)

        if self.buffered:
            log.msg("Waiting for data for packed type %d" % ord(self.buffered[0]))

    def send(self, name, **kwargs):
        #log.msg("CLIENT %s %s" % (name, kwargs))

        data = make_packet(name, kwargs)
        if self.encryption_on:
            data = self.encryptor.encrypt(data)
        self.transport.write(data)

    def connectionMade(self):
        self.loading_map = True

        peer = self.transport.getPeer()
        self.send("handshake", username=self.username, protocol=self.VERSION, server_host=peer.host, server_port=peer.port)

    def connectionLost(self, reason):
        log.msg("connectionLost", reason)

    @defer.inlineCallbacks
    def on_encryption_key_request(self, packet):
        self.public_key = RSA.importKey(packet.public_key)
        self.shared_key = Random.get_random_bytes(16)

        log.msg("About to register against session server")

        yield self.session.join_server(
            packet.server_id.encode('UTF-8'),
            self.shared_key,
            packet.public_key,
            )

        log.msg("Registered against session server - setting up ciphers")

        self.encryptor = AES.new(self.shared_key, AES.MODE_CFB, self.shared_key, segment_size=8)
        self.decryptor = AES.new(self.shared_key, AES.MODE_CFB, self.shared_key, segment_size=8)

        self.send("encryption-key-response",
            shared_secret=PKCS1_v1_5.new(self.public_key).encrypt(self.shared_key),
            verify_token=PKCS1_v1_5.new(self.public_key).encrypt(packet.verify_token),
            )

    def on_encryption_key_response(self, packet):
        self.encryption_on = True
        self.send("client-status", status=0)

    def on_login(self, packet):
        pass

    def on_ping(self, packet):
        self.send("ping", pid=packet.pid)

    def on_error(self, packet):
        log.msg(packet.message)

    def on_location(self, packet):
        self.send("location",
            grounded = Grounded.from_packet(packet.grounded),
            position = Location.from_packet(packet.position),
            orientation = Orientation.from_packet(packet.orientation),
            )


class MinecraftClientProtocol(BaseMinecraftClientProtocol):

    def __init__(self, username, password, session):
        BaseMinecraftClientProtocol.__init__(self, username, password, session)
        self.bot = bot.Bot(self)
        self.entities = entities.Entities()
        self.world = world.World()

    def on_location(self, packet):
        BaseMinecraftClientProtocol.on_location(self, packet)

        self.bot.on_grounded(grounded=packet.grounded.grounded)
        self.bot.on_position(x=packet.position.x, y=packet.position.y, z=packet.position.z, stance=packet.position.stance)
        self.bot.on_orientation(yaw=packet.orientation.rotation, pitch=packet.orientation.pitch)

        if not self.bot.started:
            self.bot.start()

    def on_update_health(self, packet):
        self.bot.on_update_health(
            hp = packet.hp,
            fp = packet.fp,
            saturation = packet.saturation,
            )


    def on_spawn_named_entity(self, packet):
        self.entities.on_spawn_named_entity(
            eid = packet.eid,
            username = packet.username,
            x = packet.x,
            y = packet.y,
            z = packet.z,
            yaw = packet.yaw,
            pitch = packet.pitch,
            item = packet.item,
            )

    def on_entity_position(self, p):
        self.entities.on_entity_position(p.eid, p.dx, p.dy, p.dz)

    def on_entity_orientation(self, p):
        self.entities.on_entity_orientation(eid=p.eid, yaw=p.yaw, pitch=p.pitch)

    def on_entity_location(self, p):
        self.on_entity_position(p)
        self.on_entity_orientation(p)

    def on_entity_teleport(self, p):
        self.entities.on_entity_teleport(p.eid, p.x, p.y, p.z)
        self.on_entity_orientation(p)

