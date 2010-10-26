
class Action(object):

    def __init__(self, bot):
        self.bot = bot

    def do(self):
        raise NotImplementedError


class Idle(Action):

    def __init__(self, bot, ticks):
        super(Idle, self).__init__(bot)
        self.ticks = ticks

    def do(self):
        self.ticks -= 1
        if self.ticks > 0:
            return self


class Say(Action):

    def __init__(self, bot, message):
        super(Say, self).__init__(bot)
        self.message = message

    def do(self):
        self.bot.protocol.send_chat_message(self.message)
        return None


class Teleport(Action):

    def __init__(self, bot, target):
        super(Teleport, self).__init__(bot)
        self.target = target

    def do(self):
        self.bot.protocol.send_chat_message("/tp %(bot)s %(target)s" % dict(bot=self.bot.protocol.username, target=target))
        # wait for 2 seconds after teleport to give map data, etc. chance to update
        return Idle(self.bot, 2.0)


class MoveTo(Action):

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


class Mine(Action):

    def __init__(self, bot, pos):
        super(Mine, self).__init__(bot)
        self.pos = pos
        self.status = 0

    def do(self):
        self.bot.send_player_digging(self.status, self.pos.x, self.pos.y, self.pos.z, 0)
        self.status = status + 1
        if self.status < 5:
            return self


class Build(Action):

    def __init__(self, bot, pos, block_type):
        super(Build, self).__init__(bot)
        self.pos = pos
        self.block_type = block_type

    def do(self):
        self.bot.send_player_block_placement(self, self.block_type, self.pos.x, self.pos.y, self.pos.z, 0)


class Functor(Action):

    def __init__(self, bot, func, *args, **kwargs):
        super(Functor, self).__init__(bot)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def do(self):
        return self.func(*self.args, **self.kwargs)


