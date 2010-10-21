
class Action(object):

    def __init__(self, bot):
        self.bot = bot

    def do(self):
        raise NotImplementedError


class Idle(Action):

    def __init__(self, time):
        super(MoveTo, self).__init__(bot)
        self.time = time

    def do(self):
        self.time -= 0.1
        if self.time > 0:
            return self


class Say(Action):

    def __init__(self, bot, target):
        super(Teleport, self).__init__(bot)
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
        # Need to move toward the target, but without tripping speed hack detection

        # Trace down and find the ground - do if need to experience gravity

        # Have we arrived?
        if self.x == self.bot.x and self.y == self.bot.y and self.z == self.bot.z:
            return None

        return self


class Functor(Action):

    def __init__(self, bot, func, *args, **kwargs):
        super(Functor, self).__init__(bot)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def do(self):
        return self.func(*args, **kwargs)


