
from pubbot import actions
from pubbot.vector import Vector

def grief(bot):
    pos = bot.pos + Vector(1,1,1)

    say = actions.Say(bot, "Hello, is anybody there?")
    wait = actions.Idle(bot, 100)

    build = actions.Build(bot, pos, 41)
    say2 = actions.Say(bot, "I made a thing!")
    wait2 = actions.Idle(bot, 100)

    mine = actions.Dig(bot, pos)
    say3 = actions.Say(bot, "My thing is gone :(")
    wait3 = actions.Idle(bot, 100)

    repeat = actions.Functor(bot, grief, bot)
    return (say, wait, build, say2, wait2, mine, say3, wait3, repeat)

