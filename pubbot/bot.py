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

# Bot object, which is where any AI work should be built on top of

# Right now we have a simple actions system - Say, Mine, Build, Move.
# More complicated behaviours will be build by combining these

import ConfigParser, os, re

from twisted.internet import task
from twisted.python import log

from pubbot.vector import Vector, forward
from pubbot import activity, actions

from pubbot.router import Pubbot

from . import packets

class Source(object):
    def __init__(self, protocol):
        self.protocol = protocol
    def msg(self, msg):
        self.protocol.send_chat_message(msg)
    notify = msg


class Bot(object):

    def __init__(self, protocol):
        self.started = False

        self.protocol = protocol
        self.name = protocol.username

        # dangerous
        self.free_will = True

        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.stance = 0
        self.on_ground = True

        self.actions = []

        self.chat = Pubbot()
        self.places = ConfigParser.ConfigParser()

        if os.path.exists("places.cfg"):
            self.places.read("places.cfg")

    @property
    def pos(self):
        return Vector(self.x, self.y, self.z)

    @property
    def eyepos(self):
        return Vector(self.x, self.y+1.65, self.z)

    def start(self):
        self.started = True

        self.update_task = task.LoopingCall(self.frame)
        self.update_task.start(0.05)

        # Hack to bootstrap pubbot into doing something

    def look_at_nearest(self):
        if not self.free_will:
            return

        nearby = []
        for entity in self.protocol.entities.names.itervalues():
            length = (entity.pos-self.pos).length()
            nearby.append((length, entity))
        if not nearby:
            log.msg("No one is nearby")
            return
        log.msg(len(nearby))
        nearby.sort()
        log.msg(nearby[0][1].player_name, nearby[0][0])
        pos = nearby[0][1].pos
        self.look_at(pos.x, pos.y+1.7, pos.z)
        if nearby[0][0] > 5 or nearby[0][0] < -5:
            if not self.actions:
                self.actions.append(actions.NavigateTo(self, nearby[0][1].pos))
            #self.move((pos-self.pos).normalize())


    def frame(self):
        #log.msg("Frame called")
        self.on_ground = False

        self.look_at_nearest()

        self.execute_actions()

        #self.move(forward(self.yaw, self.pitch).normalize())
        #log.msg(self.x, self.y, self.z)

        # Cap stance to 0.1 <= stance <= 1.65 or we get kicked
        if self.stance - self.y < 1:
            self.stance = self.y + 1
        elif self.stance - self.y > 1.65:
            self.stance = self.y + 1.6

        #if self.pitch < 0:
        #    self.pitch += 360

        #if self.yaw < 0:
        #    self.yaw += 360

        #log.msg(self.yaw, self.pitch)

        #log.msg(self.on_ground)

        self.send_location()

    def send_location(self):
        self.protocol.send("location",
            position = packets.Container(x=self.x, y=self.y, z=self.z, stance=self.stance),
            orientation = packets.Container(yaw=self.yaw, pitch=self.pitch),
            grounded = packets.Container(grounded=self.on_ground),
            )

    def look_at(self, x, y, z):
        aim = Vector(x, y, z) - self.eyepos
        self.yaw, self.pitch = aim.to_angles()

    def move(self, pos):
        self.x += pos.x
        self.y += pos.y
        self.z += pos.z
        self.on_ground = True

    def execute_actions(self):
        if self.actions:
            # Actually execute an action
            actions = self.actions.pop(0).do()

            # do() may return new things todo that are important: insert them into self.actions in the right place
            if actions:
                self.queue_immediate_actions(actions)

    def queue_immediate_actions(self, actions):
        if isinstance(actions, tuple):
            for action in reversed(actions):
                self.actions.insert(0, action)
        else:
            self.actions.insert(0, actions)

    def place_makekey(self, place):
        return re.sub('[\W_]+', '', place).lower()

    def on_grounded(self, grounded):
        self.on_ground = grounded

    def on_position(self, x, y, z, stance):
        self.x = x
        self.y = y
        self.z = z
        self.stance = stance

    def on_orientation(self, yaw, pitch):
        self.yaw = yaw
        self.pitch = pitch

    def on_update_health(self, hp, fp, saturation):
        self.health = hp
        self.food = fp
        self.saturation = saturation

    def on_chat(self, name, message):
        acts = None

        if name == self.name:
            return

        if message == "heel!":
            try:
                acts = activity.heel(self, self.protocol.entities.names[name])
            except KeyError:
                self.protocol.send_chat_message("i don't know where you are")

        elif message == "mine!":
            acts = activity.grief(self)

        elif message == "fire!":
            acts = activity.fire(self)

        elif message.startswith("this is "):
            placename = self.place_makekey(message[8:])
            if not self.places.has_section(placename):
                 self.places.add_section(placename)
            self.places.set(placename, "x", self.pos.x)
            self.places.set(placename, "y", self.pos.y)
            self.places.set(placename, "z", self.pos.z)
            self.places.write(open("places.cfg", "w"))

        elif message.startswith("go to"):
            placename = self.place_makekey(message[5:])
            try:
                x = float(self.places.get(placename, "x"))
                y = float(self.places.get(placename, "y"))
                z = float(self.places.get(placename, "z"))
                pos = Vector(x, y, z)
            except ConfigParser.NoSectionError:
                self.protocol.send_chat_message("I don't know that place :(")
                return

            acts = activity.flyto(self, pos)

        elif message.startswith("tunnel"):
            try:
                ent = self.protocol.entities.names[name]
            except:
                self.protocol.send_chat_message("i don't know where you are")
                return

            from pubbot.quaternion import directions
            dir = directions(ent.yaw, ent.pitch).forward
            tunnel_loc = self.world.trace(ent.pos, dir)

            self.protocol.send_chat_message("I'm looking at %s but you didnt teach me to tunnel yet", tunnel_loc)

        elif message.startswith("orient"):
            if len(message) > 6:
                pitch, yaw = message.strip().split(" ")[1:]
                self.pitch = float(pitch)
                self.yaw = float(yaw)
                self.free_will = False
            else:
                self.protocol.send_chat_message("Current orientation is %s, %s" % (self.pitch, self.yaw))

        elif message.startswith("pos"):
            self.free_will = False
            if len(message) > 3:
                x, y, z = message.strip().split(" ")[1:]
                self.x = float(x)
                self.y = float(y)
                self.z = float(z)
                self.free_will = False
            else:
                self.protocol.send_chat_message("Current pos is %s, %s, %s" % (self.pos.x, self.pos.y, self.pos.z))

        elif message.startswith("mine"):
            x, y, z, face = message.strip().split(" ")[1:]
            a = actions.Dig(Vector(float(x), float(y), float(z)), int(face))
            acts = (a, )

        elif message.startswith("place"):
            x, y, z, tid = message.strip().split(" ")[1:]
            a = actions.Build(self, Vector(float(x), float(y), float(z)), int(tid))
            acts = (a, )

        if acts:
            self.queue_immediate_actions(acts)
            return


        self.chat.on_message(Source(self.protocol), name, message)

    def on_player_join(self, name):
        if self.name == name:
            return
        self.chat.on_join(Source(self.protocol), name, "")

