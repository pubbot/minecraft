
from twisted.internet import task


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

    def frame(self):
        self.execute_actions()
        self.send_player_position_and_look(self.x, self.stance, self.y, self.z, self.yaw, self.pitch, self.on_ground)

    def execute_actions(self):
        if self.actions:
            # Actually execute an action
            nia = actions.pop(0).do()

            # do() may return new things todo that are important: insert them into self.actions in the right place
            if nia:
                if isinstance(nia, tuple):
                    for i in range(len(nia)-1, 0):
                        self.actions.insert(0, nia[i])
                else:
                    self.actions.insert(0, nia)


