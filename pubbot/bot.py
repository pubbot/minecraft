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

from twisted.internet import task
from twisted.python import log

from pubbot.vector import Vector, forward
from pubbot import activity


class Bot(object):

    def __init__(self, protocol):
        self.protocol = protocol

        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.stance = 0
        self.on_ground = True

        self.actions = []

    @property
    def pos(self):
        return Vector(self.x, self.y, self.z)

    def start(self):
        self.update_task = task.LoopingCall(self.frame)
        self.update_task.start(0.1)

        # Hack to bootstrap pubbot into doing something

    def look_at_nearest(self):
        nearby = []
        for entity in self.protocol.entities.names.itervalues():
            length = (entity.pos-self.pos).length()
            nearby.append((length, entity))
        if not nearby:
            #log.msg("No one is nearby")
            return
        #log.msg(len(nearby))
        nearby.sort()
        #log.msg(nearby[0][1].player_name, nearby[0][0])
        pos = nearby[0][1].pos
        self.look_at(pos.x, pos.y, pos.z)
        #if nearby[0][0] > 5 or nearby[0][0] < -5:
        #    self.move((pos-self.pos).normalize())


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

        if self.pitch < 0:
            self.pitch += 360

        # if self.yaw < 0:
        #     self.yaw += 360

        #log.msg(self.yaw, self.pitch)

        #log.msg(self.on_ground)

        self.protocol.send_player(self.on_ground)
        self.protocol.send_player_position(self.x, self.y, self.stance, self.z, self.on_ground)
        self.protocol.send_player_look(self.yaw, self.pitch, self.on_ground)

    def look_at(self, x, y, z):
        aim = self.pos - Vector(x, y, z)
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


    def on_chat(self, name, message):
        acts = None

        if message == "heel!":
            try:
                acts = activity.heel(self, self.protocol.entities.names[name])
            except KeyError:
                self.protocol.send_chat_message("i don't know where you are")
        elif message == "mine!":
            acts = activity.grief(self)

        if acts:
            self.queue_immediate_actions(acts)
