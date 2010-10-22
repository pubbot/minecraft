
from math import sqrt, atan2

from twisted.internet import task
from twisted.python import log

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

    def start(self):
        self.update_task = task.LoopingCall(self.frame)
        self.update_task.start(0.1)

        # Hack to bootstrap pubbot into doing something
        self.queue_immediate_actions(activity.grief(self))

    def frame(self):
        self.execute_actions()

        # Cap stance to 0.1 <= stance <= 1.65 or we get kicked
        if self.stance - self.y < 0.1:
            self.stance = self.y + 0.1
        elif self.stance - self.y > 1.65:
            self.stance = self.y + 1.65

        self.protocol.send_player_position_and_look(self.x, self.y, self.stance, self.z, self.yaw, self.pitch, self.on_ground)

    def look_at(self, x, y, z):
        x -= self.x
        y -= self.y
        z -= self.z

        r = sqrt(x*x + z*z)

        self.yaw = atan2(x, z)
        self.pitch = atan2(y - 1.0, r)

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


