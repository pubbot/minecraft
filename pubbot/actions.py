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

# Simple actions or steps the bot can do

from twisted.python import log


class Action(object):

    def __init__(self, bot):
        self.bot = bot

    def do(self):
        raise NotImplementedError


class Idle(Action):

    """ I wait a certain number of game ticks """

    def __init__(self, bot, ticks):
        super(Idle, self).__init__(bot)
        self.ticks = ticks

    def do(self):
        self.ticks -= 1
        if self.ticks > 0:
            return self


class Say(Action):

    """ I say things in chat """

    def __init__(self, bot, message):
        super(Say, self).__init__(bot)
        self.message = message

    def do(self):
        self.bot.protocol.send_chat_message(self.message)
        return None


class Teleport(Action):

    """ If bot has ops, then I teleport to other players """

    def __init__(self, bot, target):
        super(Teleport, self).__init__(bot)
        self.target = target

    def do(self):
        self.bot.protocol.send_chat_message("/tp %(bot)s %(target)s" % dict(bot=self.bot.protocol.username, target=target))
        # wait for 2 seconds after teleport to give map data, etc. chance to update
        return Idle(self.bot, 2.0)


class MoveTo(Action):

    """ I would move to a coordinate, but John has been concentrating on mining """

    def __init__(self, bot, x, y, z):
        super(MoveTo, self).__init__(bot)
        self.x = x
        self.y = y
        self.z = z

    def do(self):
        # If i'm in free fall i can't move towards an objective
        if not self.bot.on_ground:
            return self

        # Need to move toward the target, but without tripping speed hack detection

        # Trace down and find the ground - do if need to experience gravity

        # Have we arrived?
        if self.x == self.bot.x and self.y == self.bot.y and self.z == self.bot.z:
            return None

        return self


class Dig(Action):

    """ I mine blocks """

    def __init__(self, bot, pos, face=-1):
        super(Dig, self).__init__(bot)
        self.pos = pos
        self.face = face
        self.stage = "start"
        self.calls = {
            "start": self.do_start,
            "mining": self.do_mine,
            "destroy": self.do_destroy,
            "finish": self.do_finish,
            }

    def do_start(self):
        # If we don't have chunk data for this task, hold of for now
        if not self.bot.protocol.world.has_chunk(self.pos):
            log.msg("Not loaded yet")
            return self

        block = self.bot.protocol.world.get_block(self.pos)
        if block.kind == 0 or block.kind == 9:
            # Trying to mine air, skip this task
            log.msg("Trying to mine air, heg")
            return

        log.msg(block.kind, block.pos.x, block.pos.y, block.pos.z)
        log.msg(block.name)

        # holda diamond pick-axe. TODO: Work out of spade or axe is better
        self.bot.protocol.send_holding_change(0, block.preferred_tool)

        # animate arm
        self.bot.protocol.send_arm_animation(0, True)

        # actually mine
        self.stage = "mining"
        if self.face == -1:
            self.face = block.get_face(self.bot.pos)[0]
        self.timer = block.ftl

        self.mine(0)

        return self

    def do_mine(self):
        self.mine(1)
        self.timer -= 1

        self.bot.protocol.send_arm_animation(0, True)

        if self.timer < 1:
            self.stage = "destroy"

        return self

    def do_destroy(self):
        self.mine(3)

        # un-animate arm
        self.bot.protocol.send_arm_animation(0, False)

        # stop holding a thing
        self.bot.protocol.send_holding_change(0, 51)

        self.stage = "finish"

        return self

    def do_finish(self):
        self.mine(2)

    def mine(self, status):
        self.bot.protocol.send_player(True)
        if status == 3:
            self.bot.protocol.send_player_digging(1, self.pos.x, self.pos.y, self.pos.z, self.face)
        self.bot.protocol.send_player_digging(status, self.pos.x, self.pos.y, self.pos.z, self.face)
        self.bot.protocol.send_player(True)

    def do(self):
        self.bot.look_at(self.pos.x, self.pos.y, self.pos.z)
        return self.calls[self.stage]()


class Build(Action):

    """ I build blocks """

    def __init__(self, bot, pos, block_type):
        super(Build, self).__init__(bot)
        self.pos = pos
        self.block_type = block_type

    def do(self):
        self.bot.protocol.send_player_block_placement(self.block_type, self.pos.x, self.pos.y, self.pos.z, 0)


class Functor(Action):

    """ I let you call any function in the context of the actions framework """

    def __init__(self, bot, func, *args, **kwargs):
        super(Functor, self).__init__(bot)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def do(self):
        return self.func(*self.args, **self.kwargs)


